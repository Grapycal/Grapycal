import importlib
import inspect
import sys
from typing import Dict
from grapycal.extension.utils import get_extension_info

from grapycal.sobjects.node import Node
from objectsync import SObject
import logging
logger = logging.getLogger(__name__)

def load_or_reload_module(module_name:str):
    if module_name not in sys.modules:
        module = importlib.import_module(module_name)
        
        print(f'imported {module_name}')
    else:
        # delete all decentants of the module from sys.modules.
        # this trick makes importlib.import_module reload the module completely
        # (importlib.reload only reloads the module itself, not its decentants)
        for submodule_name in list(sys.modules.keys()):
            root_name = submodule_name.split('.')[0]
            if root_name == module_name:
                sys.modules.pop(submodule_name)

        module = importlib.import_module(module_name)
    return module

class Extension:
    def __init__(self,extension_name:str,existing_node_types:set[type[SObject]]=set(),reload=False) -> None:
        try:
            if reload:
                self.module = load_or_reload_module(extension_name)
            else:
                self.module = importlib.import_module(extension_name)
        except ModuleNotFoundError:
            logger.error(f'Error loading extension {extension_name}. Make sure it is installed.')
            raise
        self.name = extension_name
        self.version = self.module.__version__ if hasattr(self.module,'__version__') else get_extension_info(extension_name)['version']
        
        self.node_types:Dict[str,type[Node]] = {}
        self.node_types_without_extension_name:Dict[str,type[Node]] = {}
        for name, obj in inspect.getmembers(self.module):
            if inspect.isclass(obj) and issubclass(obj, Node):
                type_name = f'{self.name}.{obj.__name__}'

                '''
                It may happen that the same node type is defined in multiple extensions. It is possible caused
                by diamond-imports. For example, grapycal_ext1 and grapycal_ext2 both import FunctionNode from 
                grapycal.sobjects.functionNode, and both mistakenly expose it in their __init__.py. This will
                cause an error when trying to register the node type to ObjectSync. To prevent this, we check
                if the node type already exists in the existing_node_types dict. If it does, we skip it.
                Not very elegant, but hope it works.
                '''
                if obj in existing_node_types:
                    logger.warning(f'Node type {type_name} already exists. Skipping')
                    continue

                self.node_types[type_name] = obj
                self.node_types_without_extension_name[obj.__name__] = obj

    def add_extension_name_to_node_type(self,node_type:str)->str:
        return f'{self.name}.{node_type}'
    
    def get_info(self)->Dict[str,str]:
        return {
            'name': self.name,
            'version': self.version,
        }
