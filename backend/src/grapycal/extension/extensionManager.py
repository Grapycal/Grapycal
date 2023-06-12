import importlib
import inspect
import random
from typing import TYPE_CHECKING, Dict
import sys
from os.path import join, dirname
import shutil
from grapycal.extension.extension import Extension
from grapycal.sobjects.node import Node
import objectsync

if TYPE_CHECKING:  
    from grapycal.core.workspace import Workspace

class ExtensionManager:
    def __init__(self,objectsync:objectsync.Server,workspace:'Workspace') -> None:
        self._objectsync = objectsync
        self._workspace = workspace
        cwd = sys.path[0]
        self._local_extension_dir = join(cwd,'.grapycal','extensions')
        sys.path.append(self._local_extension_dir)
        self._extensions: Dict[str, Extension] = {}

    def load_extensions(self,extension_names) -> None:
        for name in extension_names:
            self._load_extension(name)

    def import_extension(self, base_name: str) -> None:
        name = self._fetch_extension(base_name)
        self._load_extension(name)
        self._create_preview_nodes(name)

    def update_extension(self, name: str) -> None:
        pass # TODO

    def unimport_extension(self, name: str) -> None:
        pass # TODO

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
        return self._extensions[name]
    
    def _create_preview_nodes(self, name: str) -> None:
        module = self._extensions[name].module
        node_types = self.get_node_types_from_module(module)
        for node_type in node_types:
            if not node_type.category == 'hidden':
                self._objectsync.create_object(node_type,parent_id=self._workspace.get_workspace_object().sidebar.get_id(),is_preview=True)
 
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