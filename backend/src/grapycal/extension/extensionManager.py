import logging

from grapycal.extension.utils import NodeInfo
logger = logging.getLogger(__name__)

from importlib import util as importlib_util
import random
from typing import TYPE_CHECKING, Dict, List, Tuple
import sys
from os.path import join, dirname
import shutil
from grapycal.extension.extension import Extension
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort, Port
from grapycal.utils.file import get_direct_sub_folders
from grapycal.utils.misc import as_type
import objectsync

if TYPE_CHECKING:  
    from grapycal.core.workspace import Workspace

class ExtensionManager:
    def __init__(self,objectsync_server:objectsync.Server,workspace:'Workspace') -> None:
        self._objectsync = objectsync_server
        self._workspace = workspace
        cwd = sys.path[0]
        self._local_extension_dir = join(cwd,'.grapycal','extensions')
        sys.path.append(self._local_extension_dir)
        self._extensions: Dict[str, Extension] = {}

        # Use this topic to inform the client about the extensions
        self._imported_extensions_topic = self._objectsync.create_topic('imported_extensions',objectsync.DictTopic,is_stateful=False)
        self._avaliable_extensions_topic = self._objectsync.create_topic('avaliable_extensions',objectsync.DictTopic,is_stateful=False)
        self._node_types_topic = self._objectsync.create_topic('node_types',objectsync.DictTopic,is_stateful=False)
        self._objectsync.on('import_extension',self.import_extension,is_stateful=False)
        self._objectsync.on('unimport_extension',self.unimport_extension,is_stateful=False)
        self._objectsync.on('update_extension',self.update_extension,is_stateful=False)
        self._objectsync.on('refresh_extensions',self._update_available_extensions_topic,is_stateful=False)

        self._update_available_extensions_topic()

    def load_extensions(self,extension_names) -> List[str]:
        
        refetched_extensions = []
        for name in extension_names:
            if not Extension.extension_exists(name):
                logger.info(f'Extension {name} is not fetched. Fetching...')
                self._fetch_extension(name.split('_')[0]+'_'+name.split('_')[1],name.split('_')[2])
                refetched_extensions.append(name)
            self._load_extension(name)
        
        self._update_available_extensions_topic()

        return refetched_extensions

    def import_extension(self, package_name: str) -> Extension:
        name = self._fetch_extension(package_name)
        extension = self._load_extension(name)
        self._create_preview_nodes(name)
        self._update_available_extensions_topic()
        return extension

    def update_extension(self, extension_name: str) -> None:
        package_name = '_'.join(extension_name.split('_')[:-1])
        logger.info(f'Updating extension {package_name}')
        old_version = self._extensions[extension_name]
        new_version = self._load_extension(self._fetch_extension(package_name))

        # Get diff between old and new version
        old_node_types = set(old_version.node_types_without_extension_name.keys())
        new_node_types = set(new_version.node_types_without_extension_name.keys())
        removed_node_types = old_node_types - new_node_types
        added_node_types = new_node_types - old_node_types
        changed_node_types = old_node_types & new_node_types

        existing_nodes = self._workspace.get_workspace_object().get_children_of_type(Node)

        # Ensure there are no nodes of removed types
        for node in existing_nodes:
            type_name_without_extension = node.get_type_name().split('.')[1]
            if type_name_without_extension in removed_node_types:
                self._unload_extension(extension_name)
                raise Exception(f'Cannot update extension {package_name} because there are still nodes of type {type_name_without_extension} in the workspace.')

        # Find nodes of changed types
        def hit(node:objectsync.SObject) -> bool:
            # Only update nodes that are not previews...
            if not isinstance(node,Node):
                return False
            if node.is_preview.get():
                return False
            
            # ... and are of the changed types.
            # Node type name format: grapycal_packagename_version.node_type_name
            node_type_name = node.get_type_name() 
            a = node_type_name.rfind('_',0,node_type_name.find('.'))
            b = node_type_name.find('.')
            node_package_name = node_type_name[:a]
            node_type_name_without_extension = node_type_name[b+1:]
            return node_package_name == package_name and node_type_name_without_extension in changed_node_types

        nodes_to_update = self._objectsync.get_root_object().top_down_search(
            accept=hit,
            stop=hit,
            type=Node
        )
        
        # Remove nodes of the changed types
        nodes_to_recover:List[Tuple[objectsync.sobject.SObjectSerialized,str]] = []
        wrapped_topics:set[Tuple[str,str]] = set()
        edges_to_recover:Dict[str,Tuple[str,str,str]] = {}
        removed_ports = set[str]()
        port_map_1 = {}
        for node in nodes_to_update:
            # First serialize the node
            nodes_to_recover.append((node.serialize(),node.get_parent().get_id()))

            for name, topic in node._attributes.items():
                if isinstance(topic,objectsync.WrappedTopic):
                    wrapped_topics.add((node.get_id(),name))

            # To handle edge recovery, we need to know the mapping between old and new port ids.
            # We use the port name and the node id to identify a port.
            # The mapping can be accessed by combining the following maps:
            #   port_map_1: old id -> (port name, old node id)
            #   node_id_map: old node id -> new node id
            #   port_map_2: (port name, new node id) -> new id
            ports: List[Port] = node.in_ports.get() + node.out_ports.get() # type: ignore
            for port in ports:
                port_map_1[port.get_id()] = (port.is_input.get(),port.name.get(),node.get_id())
            for port in ports:
                removed_ports.add(port.get_id())
                for edge in port.edges.copy():
                    edges_to_recover[edge.get_id()] = (edge.tail._topic.get(),edge.head._topic.get(),edge.get_parent().get_id())
                    self._objectsync.destroy_object(edge.get_id())

            # Then destroy the node
            self._objectsync.destroy_object(node.get_id())


        '''
        Now, the old nodes, ports and edges are destroyed. Their information is stored in nodes_to_recover and edges_to_recover.
        '''
        
        # Recover nodes with new version
        
        node_id_map = {}
        new_nodes:Dict[str,Tuple[objectsync.sobject.SObjectSerialized,Node]] = {}
        for old_serialized, parent_id in nodes_to_recover:
            type_name = f'{new_version.extension_name}.{old_serialized.type.split(".")[1]}'

            # Create the new node instance
            new_node: Node = self._objectsync.create_object_s(type_name,parent_id=parent_id) # type: ignore
            new_nodes[new_node.get_id()] = (old_serialized,new_node)
            node_id_map[old_serialized.id] = new_node.get_id()
        
        # Update values of wrapped topics
        for old_serialized,new_node in new_nodes.values():
            for attr in old_serialized.attributes:
                if (old_serialized.id,attr[0]) in wrapped_topics:
                    if isinstance(attr[2],list):
                        tmp = []
                        for value in attr[2]:
                            if value in node_id_map:
                                tmp.append(node_id_map[value])
                            else:
                                tmp.append(value)
                        attr[2] = tmp
                    elif isinstance(attr[2],dict):
                        tmp = {}
                        for key,value in attr[2].items():
                            if value in node_id_map:
                                tmp[key] = node_id_map[value]
                            else:
                                tmp[key] = value
                        attr[2] = tmp
                    else:
                        attr[2] = node_id_map[attr[2]] if attr[2] in node_id_map else attr[2]
                        

        # Recover the new nodes
        port_map_2 = {}
        for old_serialized,new_node in new_nodes.values():
            # Let the node handle the recovery
            old_node_info = NodeInfo(old_serialized)
            new_node.old_node_info = old_node_info
            new_node.restore_from_version('',old_node_info) #TODO version name


            ports: List[Port] = new_node.in_ports.get() + new_node.out_ports.get() # type: ignore
            for port in ports:
                port_map_2[(port.is_input.get(),port.name.get(),new_node.get_id())] = port.get_id()
            
            #TODO: let the new node class handle the recovery for backwards compatibility


        # Recover edges if possible
        def port_id_map(old_port_id:str) -> str|None:
            
            try:
                is_input, port_name, old_node_id = port_map_1[old_port_id]
            except KeyError:
                return None
            
            new_node_id = node_id_map[old_node_id]

            try:
                new_port_id =  port_map_2[(is_input,port_name,new_node_id)]
            except KeyError:
                return None
            
            return new_port_id

        for tail_id, head_id, parent_id in edges_to_recover.values():
            #print('tail_id:',tail_id,'head_id:',head_id,'parent_id:',parent_id,port_map_1,port_map_2,node_id_map)
            if tail_id not in removed_ports:
                new_tail_id = tail_id
            else:
                new_tail_id = port_id_map(tail_id)
            if head_id not in removed_ports:
                new_head_id = head_id
            else:
                new_head_id = port_id_map(head_id)

            if new_tail_id is None or new_head_id is None:
                continue # The port does not present in the new version, unfortunately we cannot recover the edge.
            
            new_tail = self._objectsync.get_object(new_tail_id)
            new_head = self._objectsync.get_object(new_head_id)
            new_edge = self._objectsync.create_object(Edge,parent_id=parent_id,tail=new_tail,head=new_head)

        # Unimport old version
        self.unimport_extension(old_version.extension_name)
        self._create_preview_nodes(new_version.extension_name)

        logger.info(f'Updated extension {package_name}')

        #TODO: cut history

    def unimport_extension(self, extension_name: str) -> None:
        self._check_extension_not_used(extension_name)
        self._destroy_preview_nodes(extension_name)
        self._unload_extension(extension_name)
        self._update_available_extensions_topic()
        # Don't unfetch now, because the user might change their mind.
        # The Grapycal App will unfetch the unused extension when closing.

    def _update_available_extensions_topic(self) -> None:
        available_extensions = self._scan_available_extensions()
        for name in available_extensions:
            if name not in self._avaliable_extensions_topic.get():
                self._avaliable_extensions_topic.add(name,{
                    'name':name
                })
        for name in list(self._avaliable_extensions_topic.get().keys()):
            if name not in available_extensions:
                self._avaliable_extensions_topic.pop(name)

    def _scan_available_extensions(self) -> list[str]:
        '''
        Returns a list of available extensions in local folder.
        '''
        available_extensions = []
        # Local
        for name in get_direct_sub_folders('.'):
            if not name.startswith('grapycal_'):
                continue
            continue_flag = False
            for extension in self._extensions.values():
                if name == extension.package_name:
                    continue_flag = True
                    break
            if continue_flag:
                continue

            available_extensions.append(name)

        # TODO: pip
        return available_extensions

    def _fetch_extension(self, package_name: str, number=None) -> str:
        '''
        Copy the current version of the extension to .grapycal/extensions, so it cannot be modified by the user.
        '''
        assert package_name.startswith('grapycal_'), f'Extension name must start with grapycal_, got {package_name}'
        source_name = package_name
        source_path = dirname(importlib_util.find_spec(source_name).origin) # type: ignore

        if number is None:
            number = random.randint(0,1000000)
        extension_name = f'{package_name}_{number}'
        assert source_path is not None
        shutil.copytree(source_path,join(self._local_extension_dir,extension_name),dirs_exist_ok=True)
        return extension_name

    def _load_extension(self, name: str) -> Extension:
        self._extensions[name] = Extension(name,self._objectsync.get_all_node_types())
        for node_type_name, node_type in self._extensions[name].node_types.items():
            self._objectsync.register(node_type,node_type_name)
        self._imported_extensions_topic.add(name,{
            'name':name
        })
        for node_type_name, node_type in self._extensions[name].node_types.items():
            self._node_types_topic.add(node_type_name,{
                'name':node_type_name,
                'category':node_type.category
            })
        logger.info(f'Loaded extension {name}')
        return self._extensions[name]
    
    def _check_extension_not_used(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        for obj in self._objectsync.get_objects():
            if isinstance(obj, Node):
                if not obj.is_preview.get() and obj.get_type_name() in node_types:
                    raise Exception(f'Cannot unload extension {name}, there are still objects of this type in the workspace')

    def _unload_extension(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        for node_type in node_types:
            self._objectsync.unregister(node_type)
        self._extensions.pop(name)
        self._imported_extensions_topic.pop(name)
        for node_type_name in node_types:
            self._node_types_topic.pop(node_type_name)
        logger.info(f'Unloaded extension {name}')
    
    def _create_preview_nodes(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        for node_type in node_types.values():
            if not node_type.category == 'hidden':
                self._objectsync.create_object(node_type,parent_id=self._workspace.get_workspace_object().sidebar.get_id(),is_preview=True)
 
    def _destroy_preview_nodes(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        for obj in self._workspace.get_workspace_object().sidebar.get_children_of_type(Node):
            if obj.get_type_name() in node_types:
                self._objectsync.destroy_object(obj.get_id())

    def get_extension(self, name: str) -> Extension:
        return self._extensions[name]
    
    def get_extention_names(self) -> list[str]:
        return list(self._extensions.keys())