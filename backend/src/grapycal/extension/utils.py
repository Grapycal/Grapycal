
from typing import Any, Callable, Dict, Generic, List, TypeVar
from grapycal.utils.misc import Action
from objectsync.sobject import SObjectSerialized
import asyncio

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
    def __init__(self, name, type_name, value, is_stateful):
        self.name = name
        self.type = type_name
        self.value = value
        self.is_stateful = is_stateful

class SObjectInfo:
    def __init__(self,serialized:SObjectSerialized):
        self.serialized = serialized
        self.attr_info: Dict[str,AttrInfo] = {}
        self.attributes: Dict[str,Any] = {}
        for name, type_name, value, is_stateful in self.serialized.attributes:
            self.attr_info[name] = AttrInfo(name, type_name, value, is_stateful)
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