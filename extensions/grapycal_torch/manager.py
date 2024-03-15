
import os
from typing import Dict, Generic, List, TypeVar
from grapycal import Bus
from grapycal.extension.extension import CommandCtx
from grapycal.utils.misc import Action

from grapycal import Node
from grapycal_torch.networkDef import NetworkCallNode
from grapycal_torch.utils import find_next_valid_name
from objectsync import Topic
import torch

from . import  moduleNode
if 1+1==3: # smart way to avoid circular imports
    from . import GrapycalTorch, networkDef
    from grapycal_torch.networkDef import NetworkInNode, NetworkOutNode


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
    
# class ConfManager:
#     def __init__(self):
#         self.confs:ListDict['configureNode.ConfigureNode'] = ListDict()
#         self.device_buses:DefaultBusDict = DefaultBusDict()
#         self.mode_buses:DefaultBusDict = DefaultBusDict()

#     def add(self, name, conf:'configureNode.ConfigureNode'):
#         self.confs.append(name,conf)
#         self.device_buses += name,conf.device
#         self.mode_buses += name,conf.mode

#     def remove(self, name, conf:'configureNode.ConfigureNode'):
#         self.confs.remove(name,conf)
#         self.device_buses -= name,conf.device
#         self.mode_buses -= name,conf.mode

#     def get_device(self, name):
#         if name not in self.device_buses:
#             return None
#         return self.device_buses[name][0].get()
    
#     def get_mode(self, name):
#         if name not in self.mode_buses:
#             return None
#         return self.mode_buses[name][0].get()
        
class NetManager:
    def __init__(self,ext:'GrapycalTorch'):
        self.ext = ext
        self.calls:ListDict['networkDef.NetworkCallNode'] = ListDict()
        self.ins:Dict[str,'networkDef.NetworkInNode'] = {}
        self.outs:Dict[str,'networkDef.NetworkOutNode'] = {}
        self.on_network_names_changed = Action()

    def get_module_nodes(self, name)->list['moduleNode.ModuleNode']:
        def _get_modules_after(node:Node,res:list['moduleNode.ModuleNode'])->None:
            if node in res:
                return 
            if isinstance(node,moduleNode.ModuleNode):
                res.append(node)
            output_edges = [edge for port in node.out_ports for edge in port.edges]
            for edge in output_edges:
                _get_modules_after(edge.head.get().node,res)

        res = []
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
    
    def save_network(self, name, path):
        if name not in self.ins:
            raise Exception(f'Network {name} does not exist')
        self.make_id_valid(name)
        state_dicts = {}
        for mn in self.get_module_nodes(name):
            state_dicts[mn.state_dict_id.get()] = mn.get_state_dict()
        torch.save(state_dicts,path)

    def load_network(self, name, path, load_node):
        if name not in self.ins:
            raise Exception(f'Network {name} does not exist')
        if not os.path.exists(path):
            raise Exception(f'File {path} does not exist')
        self.make_id_valid(name)
        state_dicts:dict = torch.load(path)
        for mn in self.get_module_nodes(name):
            if mn.state_dict_id.get() in state_dicts:
                mn.load_state_dict(state_dicts.pop(mn.state_dict_id.get()))
            else:
                mn.print_exception(f'Warning: parameter for {mn.state_dict_id.get()} is missing in file {path}')
        if len(state_dicts) > 0:
            load_node.print_exception(f'Warning: layers {list(state_dicts.keys())} are absent in the current network architecture, so they are not loaded')

    def make_id_valid(self, name):
        # make sure state dict ids are set and unique
        existing_ids = set()
        for mn in self.get_module_nodes(name):
            if mn.state_dict_id.get() in existing_ids or mn.state_dict_id.get() == '':
                base = mn.__class__.__name__[:-4]
                i=0
                while f'{base}_{i}' in existing_ids:
                    i+=1
                mn.state_dict_id.set(f'{base}_{i}')
            existing_ids.add(mn.state_dict_id.get())

    def next_name(self,name:str):
        invalids = self.ins.keys() | self.outs.keys()
        return find_next_valid_name(name, invalids)

    def add_in(self, name:str, node:'NetworkInNode'):
        if not self.ext.has_command(f'Call: {name}'):
            self.ext.register_command(f'Call: {name}', lambda ctx: self._create_call(ctx,name))
        self.ins[name] = node
        self.on_network_names_changed.invoke()

    def remove_in(self, name:str):
        del self.ins[name]
        if name not in self.outs:
            self.ext.unregister_command(f'Call: {name}')
        self.on_network_names_changed.invoke()

    def add_out(self, name:str, node:'NetworkOutNode'):
        if not self.ext.has_command(f'Call: {name}'):
            self.ext.register_command(f'Call: {name}', lambda ctx: self._create_call(ctx,name))
        self.outs[name] = node
        self.on_network_names_changed.invoke()
        
    def remove_out(self, name:str):
        del self.outs[name]
        if name not in self.ins:
            self.ext.unregister_command(f'Call: {name}')
        self.on_network_names_changed.invoke()

    def _create_call(self, ctx:CommandCtx, name:str):
        from grapycal_torch.networkDef import NetworkCallNode # avoid circular imports
        self.ext.create_node(NetworkCallNode, ctx.mouse_pos, name=name)

    def set_mode(self, name, mode):
        for mn in self.get_module_nodes(name):
            mn.set_mode(mode)

    def set_device(self, name, device):
        for mn in self.get_module_nodes(name):
            mn.to(device)

class MNManager:
    def __init__(self):
        self.mns:set['moduleNode.ModuleNode'] = set()

    def add(self, mn:'moduleNode.ModuleNode'):
        self.mns.add(mn)

    def remove(self, mn:'moduleNode.ModuleNode'):
        self.mns.remove(mn)
