import logging
logger = logging.getLogger(__name__)
import importlib.util
from typing import Any, Callable, Dict, Generic, List, TypeVar
from grapycal.utils.misc import Action
from objectsync.sobject import SObjectSerialized
import asyncio

from pathlib import Path
import pkg_resources

I=TypeVar('I')
O=TypeVar('O')
class LazyDict(Generic[I,O]):
    def __init__(self,gen:Callable[[I],O],keys:List[I]) -> None:
        self.gen = gen
        self._keys=keys

    def __getitem__(self,idx:I)->O:
        return self.gen(idx)
    
    def __contains__(self,idx:I)->bool:
        return idx in self._keys
    
    def keys(self):
        return self._keys


class AttrInfo:
    def __init__(self, name, type_name, value, is_stateful, order_strict):
        self.name = name
        self.type = type_name
        self.value = value
        self.is_stateful = is_stateful
        self.order_strict = order_strict

class SObjectInfo:
    def __init__(self,serialized:SObjectSerialized):
        self.serialized = serialized
        self.attr_info: Dict[str,AttrInfo] = {}
        self.attributes: Dict[str,Any] = {}
        for name, type_name, value, is_stateful, order_strict  in self.serialized.attributes:
            self.attr_info[name] = AttrInfo(name, type_name, value, is_stateful, order_strict)
            self.attributes[name] = value

        

    def has_attribute(self,name):
        return name in self.attr_info
    
    def __getitem__(self,name:str):
        '''
        Returns the value of an attribute
        '''
        return self.attributes[name]

class ControlInfo(SObjectInfo):
    pass

class NodeInfo(SObjectInfo):
    '''
    An easier-to-use interface to read SObjectSerialized of a node
    '''
    def __init__(self, serialized: SObjectSerialized):
        super().__init__(serialized)
        children = serialized.children
        controls: Dict[str,str] = self.attributes['controls']
        self.controls=LazyDict[str,ControlInfo](lambda name: ControlInfo(children[controls[name]]),list(controls.keys()))

class Clock:
    def __init__(self, interval: float):
        self.interval = interval
        self.on_tick = Action()


    async def run(self):
        while True:
            await asyncio.sleep(self.interval)
            self.on_tick.invoke()

def get_package_version(package_name:str)->str:
    '''
    Find the version of a package. Considering editable installs, the developer may have changed the version but not installed it.
    In this case, the new version will not be reflected in pkg_resources. So we first try to find the version in pyproject.toml.
    '''

    version = get_package_version_from_pyproject(package_name)
    if version is not None:
        return version
    
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        # the package is not installed
        return '0.0.0'

def get_package_version_from_pyproject(package_name:str)->str|None:
    init_location = importlib.util.find_spec(package_name).origin
    if init_location is None:
        return None
    package_location = Path(init_location).parent
    pyproject = Path(package_location) / 'pyproject.toml'
    
    if not pyproject.exists():
        return None
    
    with open(pyproject,'r') as f:
        pyproject_toml = f.read()

    import toml
    pyproject_toml = toml.loads(pyproject_toml)
    # try poetry
    try:
        return pyproject_toml['tool']['poetry']['version']
    except KeyError:
        pass
    # try pep 621
    try:
        return pyproject_toml['project']['version']
    except KeyError:
        pass
    logger.warning(f'Package {package_name} has a pyproject.toml but no version is found in it')
    return None
    
def list_to_dict(l:List[dict],key:str)->Dict[Any,dict]:
    '''
    Convert a list of dicts to a dict of dicts
    '''
    return {d[key]:d for d in l}

def get_extension_info(name) -> dict:
    # returns the same as Extension.get_info(), but no need to load the extension
    return {
        'name':name,
        'version':get_package_version(name),
    }