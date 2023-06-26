from importlib import util as importlib_util
from pprint import pprint
import random
from typing import TYPE_CHECKING, Dict, List, Tuple
import sys
from os.path import join, dirname
import shutil
from grapycal.extension.extension import Extension
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import Port
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
        self._objectsync.on('import_extension',self.import_extension,is_stateful=False)
        self._objectsync.on('unimport_extension',self.unimport_extension,is_stateful=False)
        self._objectsync.on('update_extension',self.update_extension,is_stateful=False)

        self._update_available_extensions_topic()

    def load_extensions(self,extension_names) -> None:
        for name in extension_names:
            self._load_extension(name)
        
        self._update_available_extensions_topic()

    def import_extension(self, package_name: str) -> Extension:
        name = self._fetch_extension(package_name)
        extension = self._load_extension(name)
        self._create_preview_nodes(name)
        self._update_available_extensions_topic()
        return extension

    def update_extension(self, extension_name: str) -> None:
        old_version = self._extensions[extension_name]
        package_name = '_'.join(extension_name.split('_')[:-1])
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
        edges_to_recover:List[Tuple[str,str,str]] = []
        port_map_1 = {}
        for node in nodes_to_update:
            # First serialize the node
            nodes_to_recover.append((node.serialize(),node.get_parent().get_id()))

            # To handle edge recovery, we need to know the mapping between old and new port ids.
            # We use the port name and the node id to identify a port.
            # The mapping can be accessed by combining the following maps:
            #   port_map_1: old id -> (port name, old node id)
            #   node_id_map: old node id -> new node id
            #   port_map_2: (port name, new node id) -> new id
            ports: List[Port] = node.in_ports.get() + node.out_ports.get() # type: ignore
            for port in ports:
                port_map_1[port.get_id()] = (port.name.get(),node.get_id())
            for port in ports:
                for edge in port.edges:
                    edges_to_recover.append((edge.tail._topic.get(),edge.head._topic.get(),edge.get_parent().get_id()))
                    self._objectsync.destroy_object(edge.get_id())

            # Then destroy the node
            self._objectsync.destroy_object(node.get_id())
        
        # Recover nodes with new version
        node_id_map = {}
        port_map_2 = {}
        for old_serialized, parent_id in nodes_to_recover:
            type_name = f'{new_version.extension_name}.{old_serialized.type.split(".")[1]}' #TODO: Handle removed node types
            new_node: Node = self._objectsync.create_object_s(type_name,parent_id=parent_id) # type: ignore
            new_node.translation.set(old_serialized.attributes['translation'])
            node_id_map[old_serialized.id] = new_node.get_id()

            ports: List[Port] = new_node.in_ports.get() + new_node.out_ports.get() # type: ignore
            for port in ports:
                port_map_2[(port.name.get(),new_node.get_id())] = port.get_id()
            
            #TODO: let the new node class handle the recovery for backwards compatibility

        # Recover edges if possible
        def port_id_map(old_port_id:str) -> str|None:
            
            try:
                port_name, old_node_id = port_map_1[old_port_id]
            except KeyError:
                return old_port_id
            
            new_node_id = node_id_map[old_node_id]

            try:
                new_port_id =  port_map_2[(port_name,new_node_id)]
            except KeyError:
                return None
            
            return new_port_id

        for tail_id, head_id, parent_id in edges_to_recover:
            print('tail_id:',tail_id,'head_id:',head_id,'parent_id:',parent_id,port_map_1,port_map_2,node_id_map)
            new_tail_id = port_id_map(tail_id)
            new_head_id = port_id_map(head_id)
            if new_tail_id is None or new_head_id is None:
                continue # The port does not present in the new version
            
            new_edge = self._objectsync.create_object(Edge,parent_id=parent_id)
            new_edge.tail.set(as_type(self._objectsync.get_object(new_tail_id),Port))
            new_edge.head.set(as_type(self._objectsync.get_object(new_head_id),Port))

        # Unimport old version
        self.unimport_extension(old_version.extension_name)
        self._create_preview_nodes(new_version.extension_name)

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
                self._avaliable_extensions_topic.remove(name)

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

    def _fetch_extension(self, package_name: str) -> str:
        '''
        Copy the current version of the extension to .grapycal/extensions, so it cannot be modified by the user.
        '''
        if package_name == 'builtin_nodes':
            source_name = 'grapycal.builtin_nodes'
        else:
            assert package_name.startswith('grapycal_'), f'Extension name must start with grapycal_, got {package_name}'
            source_name = package_name
        source_path = dirname(importlib_util.find_spec(source_name).origin) # type: ignore

        extension_name = f'{package_name}_{random.randint(0,1000000)}'
        assert source_path is not None
        shutil.copytree(source_path,join(self._local_extension_dir,extension_name),dirs_exist_ok=True)
        return extension_name

    def _load_extension(self, name: str) -> Extension:
        self._extensions[name] = Extension(name,self._objectsync.get_all_node_types())
        pprint(('before register',self._objectsync._object_types))
        for node_type_name, node_type in self._extensions[name].node_types.items():
            print('extension ',name,' _register ',node_type_name)
            self._objectsync.register(node_type,node_type_name)
        pprint(('after register',self._objectsync._object_types))
        self._imported_extensions_topic.add(name,{
            'name':name
        })
        return self._extensions[name]
    
    def _check_extension_not_used(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        for obj in self._objectsync.get_objects():
            if isinstance(obj, Node):
                if not obj.is_preview.get() and obj.get_type_name() in node_types:
                    raise Exception(f'Cannot unload extension {name}, there are still objects of this type in the workspace')

    def _unload_extension(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        pprint(('before unregister',self._objectsync._object_types))
        for node_type in node_types:
            
            print('extension ',name,' _unregister ',node_type)
            self._objectsync.unregister(node_type)
        pprint(('after unregister',self._objectsync._object_types))
        self._extensions.pop(name)
        self._imported_extensions_topic.remove(name)
    
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