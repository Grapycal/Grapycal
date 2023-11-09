import logging
import pkgutil

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

    def import_extension(self, extension_name: str, create_preview_nodes = True) -> Extension:
        extension = self._load_extension(extension_name)
        if create_preview_nodes:
            self.create_preview_nodes(extension_name)
        self._update_available_extensions_topic()
        return extension

    def update_extension(self, extension_name: str) -> None:
        old_version = self._extensions[extension_name]
        old_node_types = set(old_version.node_types_without_extension_name.keys())
        new_version = Extension(extension_name,set(self._objectsync.get_all_node_types().values())-set(old_version.node_types.values()))

        # Get diff between old and new version
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
                raise Exception(f'Cannot update extension {extension_name} because there are still nodes of type {type_name_without_extension} in the workspace.')

        # Find nodes of changed types
        def hit(node:objectsync.SObject) -> bool:
            # Only update nodes that are not previews...
            if not isinstance(node,Node):
                return False
            if node.is_preview.get():
                return False
            
            # ... and are of the changed types.
            # Node type name format: grapycal_packagename.node_type_name
            node_type_name = node.get_type_name() 
            node_extension_name,node_type_name_without_extension = node_type_name.split('.')
            return node_extension_name == extension_name and node_type_name_without_extension in changed_node_types

        nodes_to_update = self._workspace.get_workspace_object().main_editor.top_down_search(
            accept=hit,
            stop=hit,
            type=Node
        )
        
        # Remove nodes of the changed types
        nodes_to_recover:List[objectsync.sobject.SObjectSerialized] = []
        edges_to_recover:List[objectsync.sobject.SObjectSerialized] = []
        
        for node in nodes_to_update:
            # First serialize the node
            nodes_to_recover.append(node.serialize())
            ports: List[Port] = node.in_ports.get() + node.out_ports.get() # type: ignore
            for port in ports:
                for edge in port.edges.copy():
                    edges_to_recover.append(edge.serialize())
                    self._objectsync.destroy_object(edge.get_id())

            # Then destroy the node
            self._objectsync.destroy_object(node.get_id())

        type_map = {}
        for type_name in changed_node_types:
            type_map[old_version.add_extension_name_to_node_type(type_name)] = new_version.add_extension_name_to_node_type(type_name)
            
        for node in nodes_to_recover:
            node.update_type_names(type_map)

        '''
        Now, the old nodes, ports and edges are destroyed. Their information is stored in nodes_to_recover and edges_to_recover.
        '''

        # Unimport old version
        self._destroy_preview_nodes(old_version.extension_name)
        self.unimport_extension(old_version.extension_name)
        self.import_extension(new_version.extension_name,create_preview_nodes=False)

        self._workspace.get_workspace_object().main_editor.restore(nodes_to_recover,edges_to_recover)

        self.create_preview_nodes(new_version.extension_name)
        self._update_available_extensions_topic()

        logger.info(f'Updated extension {extension_name}')

        #TODO: cut history

    def unimport_extension(self, extension_name: str) -> None:
        self._destroy_preview_nodes(extension_name)
        self._check_extension_not_used(extension_name)
        self._unload_extension(extension_name)
        self._update_available_extensions_topic()

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
        for pkg in pkgutil.iter_modules():
            if  pkg.name.startswith('grapycal_') and pkg.name != 'grapycal':
                if pkg.name not in self._extensions:
                    available_extensions.append(pkg.name)
        return available_extensions

    def _load_extension(self, name: str) -> Extension:
        self._extensions[name] = Extension(name,set(self._objectsync.get_all_node_types().values()))
        self._register_extension(name)
        self._imported_extensions_topic.add(name,{
            'name':name
        })
        for node_type_name, node_type in self._extensions[name].node_types.items():
            self._node_types_topic.add(node_type_name,{
                'name':node_type_name,
                'category':node_type.category
            })
        return self._extensions[name]
    
    def _register_extension(self, name: str) -> None:
        for node_type_name, node_type in self._extensions[name].node_types.items():
            self._objectsync.register(node_type,node_type_name)
    
    def _check_extension_not_used(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        for obj in self._objectsync.get_objects():
            if isinstance(obj, Node):
                if obj.get_type_name() in node_types:
                    raise Exception(f'Cannot unload extension {name}, there are still objects of this type in the workspace')

    def _unload_extension(self, name: str) -> None:
        node_types = self._extensions[name].node_types
        for node_type in node_types:
            self._objectsync.unregister(node_type)
        self._extensions.pop(name)
        self._imported_extensions_topic.pop(name)
        for node_type_name in node_types:
            self._node_types_topic.pop(node_type_name)
            
    def create_preview_nodes(self, name: str) -> None:
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