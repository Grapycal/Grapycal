
from typing import Dict, Generic, List, TypeVar
from grapycal import Bus
from grapycal.utils.misc import Action

from grapycal import Node
from objectsync import Topic

from .moduleNode import ModuleNode
if 1+1==3: # smart way to avoid circular imports
    from . import networkDef, configureNode


T = TypeVar('T')
class ListDict(Generic[T]):
    def __init__(self):
        self.d:Dict[str,List[T]] = {}

    def append(self, key:str, value:T):
        if key not in self.d:
            self.d[key] = []
        self.d[key].append(value)

    def remove(self, key:str, value:T):
        self.d[key].remove(value)
        if len(self.d[key]) == 0:
            self.d.pop(key)

    def has(self, key:str):
        return key in self.d
    
    def get(self, key:str):
        if key not in self.d:
            return []
        return self.d[key]
    
class DefaultBusDict:
    def __init__(self) -> None:
        self.d:Dict[str,Bus] = {}

    def __add__(self, key_topic_pair:tuple[str,Topic]):
        key,topic = key_topic_pair
        if key not in self.d:
            self.d[key] = Bus()
        self.d[key] += topic
        return self
    
    def __sub__(self, key_topic_pair:tuple[str,Topic]):
        key,topic = key_topic_pair
        self.d[key] -= topic
        return self
    
    def __contains__(self, key:str):
        return key in self.d
    
    def __getitem__(self, key:str):
        return self.d[key]._topics
    
class ConfManager:
    def __init__(self):
        self.confs:ListDict['configureNode.ConfigureNode'] = ListDict()
        self.device_buses:DefaultBusDict = DefaultBusDict()
        self.mode_buses:DefaultBusDict = DefaultBusDict()

    def add(self, name, conf:'configureNode.ConfigureNode'):
        self.confs.append(name,conf)
        self.device_buses += name,conf.device
        self.mode_buses += name,conf.mode

    def remove(self, name, conf:'configureNode.ConfigureNode'):
        self.confs.remove(name,conf)
        self.device_buses -= name,conf.device
        self.mode_buses -= name,conf.mode

    def get_device(self, name):
        if name not in self.device_buses:
            return None
        return self.device_buses[name][0].get()
    
    def get_mode(self, name):
        if name not in self.mode_buses:
            return None
        return self.mode_buses[name][0].get()
        
class NetManager:
    def __init__(self):
        self.calls:ListDict['networkDef.NetworkCallNode'] = ListDict()
        self.ins:Dict[str,'networkDef.NetworkInNode'] = {}
        self.outs:Dict[str,'networkDef.NetworkOutNode'] = {}
        self.on_network_names_changed = Action()

    def get_module_nodes(self, name)->list[ModuleNode]:
        def _get_modules_after(node:Node,res:set[ModuleNode])->None:
            if node in res:
                return 
            if isinstance(node,ModuleNode):
                res.add(node)
            output_edges = [edge for port in node.out_ports for edge in port.edges]
            if isinstance(node,ModuleNode):
                if node.module is not None:
                    res.add(node)
            for edge in output_edges:
                _get_modules_after(edge.head.get().node,res)

        res = set()
        _get_modules_after(self.ins[name],res)
        return list(res)
    
    def has_network(self, name):
        return name in self.ins and name in self.outs
    
    def get_network_names(self):
        res = []
        for name in self.ins:
            if name in self.outs:
                res.append(name)
        return res


class Manager:
    '''
    A static class that holds all the networks, configure nodes, and network calls etc.-+
    '''
    net = NetManager()
    conf = ConfManager()