import importlib
import inspect
import random
from typing import TYPE_CHECKING, Dict
import sys
from os.path import join, dirname
import shutil
from grapycal.extension.extension import Extension
from grapycal.sobjects.node import Node
from grapycal.utils.file import get_direct_sub_folders
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

        self._rescan_available_extensions()

    def load_extensions(self,extension_names) -> None:
        for name in extension_names:
            self._load_extension(name)
        
        self._rescan_available_extensions()

    def import_extension(self, base_name: str) -> None:
        name = self._fetch_extension(base_name)
        self._load_extension(name)
        self._create_preview_nodes(name)
        self._rescan_available_extensions()

    def update_extension(self, extension_name: str) -> None:
        # First, import the new version
        #TODO: Make a backup of the old version
        new_name = self._fetch_extension(extension_name)
        self._load_extension(new_name)
        # Get diff between old and new version
        old_node_types = set(self.get_node_types_from_module(self._extensions[extension_name].module))
        new_node_types = set(self.get_node_types_from_module(self._extensions[new_name].module))
        removed_node_types = old_node_types - new_node_types
        added_node_types = new_node_types - old_node_types
        # Remove old nodes


    def unimport_extension(self, extension_name: str) -> None:
        self._check_extension_not_used(extension_name)
        self._destroy_preview_nodes(extension_name)
        self._unload_extension(extension_name)
        self._rescan_available_extensions()
        # Don't unfetch now, because the user might change their mind.
        # The Grapycal App will unfetch the unused extension when closing.

    def _rescan_available_extensions(self) -> None:
        available_extensions = self._scan_available_extensions()
        for name in available_extensions:
            if name not in self._avaliable_extensions_topic.get():
                self._avaliable_extensions_topic.add(name,{
                    'name':name
                })
        for name in list(self._avaliable_extensions_topic.get().keys()):
            if name not in available_extensions:
                self._avaliable_extensions_topic.remove(name)

    def _scan_available_extensions(self) -> None:
        available_extensions = []
        # Local
        for name in get_direct_sub_folders('.'):
            if not name.startswith('grapycal_'):
                continue
            continue_flag = False
            for extension in self._extensions.values():
                if name == extension.base_name:
                    continue_flag = True
                    break
            if continue_flag:
                continue

            available_extensions.append(name)

        # TODO: Pip
        return available_extensions

    def _fetch_extension(self, base_name: str) -> str:
        '''
        Copy the current version of the extension to .grapycal/extensions, so it cannot be modified by the user.
        '''
        if base_name == 'builtin_nodes':
            source_name = 'grapycal.builtin_nodes'
        else:
            assert base_name.startswith('grapycal_'), f'Extension name must start with grapycal_, got {base_name}'
            source_name = base_name
        extension_source = dirname(importlib.import_module(source_name).__file__) # type: ignore

        name = f'{base_name}_{random.randint(0,1000000)}'
        assert extension_source is not None
        shutil.copytree(extension_source,join(self._local_extension_dir,name))
        return name

    def _load_extension(self, name: str) -> Extension:
        self._extensions[name] = Extension(name)
        for node_type in self.get_node_types_from_module(self._extensions[name].module):
            self._objectsync.register(node_type,f'{name}.{node_type.__name__}')
        self._imported_extensions_topic.add(name,{
            'name':name
        })
        return self._extensions[name]
    
    def _check_extension_not_used(self, name: str) -> None:
        node_types = self.get_node_types_from_module(self._extensions[name].module)
        for obj in self._objectsync.get_objects():
            if isinstance(obj, Node):
                if not obj.is_preview.get() and type(obj) in node_types:
                    raise Exception(f'Cannot unload extension {name}, there are still objects of this type in the workspace')

    def _unload_extension(self, name: str) -> None:
        node_types = self.get_node_types_from_module(self._extensions[name].module)
        for node_type in node_types:
            self._objectsync.unregister(node_type)
        self._extensions.pop(name)
        self._imported_extensions_topic.remove(name)
    
    def _create_preview_nodes(self, name: str) -> None:
        module = self._extensions[name].module
        node_types = self.get_node_types_from_module(module)
        for node_type in node_types:
            if not node_type.category == 'hidden':
                self._objectsync.create_object(node_type,parent_id=self._workspace.get_workspace_object().sidebar.get_id(),is_preview=True)
 
    def _destroy_preview_nodes(self, name: str) -> None:
        module = self._extensions[name].module
        node_types = self.get_node_types_from_module(module)
        for obj in self._workspace.get_workspace_object().sidebar.get_children_of_type(Node):
            if type(obj) in node_types:
                self._objectsync.destroy_object(obj.get_id())

    def get_extension(self, name: str) -> Extension:
        return self._extensions[name]
    
    def get_extention_names(self) -> list[str]:
        return list(self._extensions.keys())
    
    '''
    Helper functions
    '''

    def get_node_types_from_module(self, module) -> list[type[Node]]:
        node_types: list[type[Node]] = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Node) and obj != Node:
                node_types.append(obj)
        return node_types