from typing import Dict, Generic, List, TypeVar
from grapycal import Node, ListTopic, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from objectsync.sobject import SObjectSerialized
import torch.nn as nn

from .moduleNode import ModuleNode

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

class NetworkDefManager:
    calls: ListDict['NetworkCallNode'] = ListDict()
    ins: Dict[str,'NetworkInNode'] = {}
    outs: Dict[str,'NetworkOutNode'] = {}

    @staticmethod
    def get_module_nodes(name)->list[ModuleNode]:
        '''
        Get all PyTorch modules in a network definition.
        '''
        
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
        _get_modules_after(NetworkDefManager.ins[name],res)
        return list(res)
                
                

class NetworkCallNode(Node):
    '''
    A NetworkCallNode represents a call to a specific function.
    Once you assign a function name to the NetworkCallNode, Grapycal will search for a NetworkInNode and a NetworkOutNode existing
    in the workspace with the same function name. Then, its ports will be updated accroding to the function
    definition.
    '''

    category = 'torch/neural network'
    def build_node(self):
        self.label.set('')
        self.shape.set('normal')
        self.network_name = self.add_attribute('network name',StringTopic,editor_type='text')
        self.icon_path.set('nn')

    def init_node(self):
        if self.is_preview:
            self.label.set('Call Network')
        NetworkDefManager.calls.append(self.network_name.get(),self)
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)
        self.update_ports()
        self.label.set(f'{self.network_name.get()}')

    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('network name')

    def on_network_name_changed(self, old, new):
        self.label.set(f'{new}')
        NetworkDefManager.calls.remove(old,self)
        NetworkDefManager.calls.append(new,self)

    def on_network_name_changed_auto(self,new):
        self.update_ports()

    def update_ports(self):
        self.update_input_ports()
        self.update_output_ports()

    def update_input_ports(self):
        if self.network_name.get() not in NetworkDefManager.ins:
            return
        keys = NetworkDefManager.ins[self.network_name.get()].outs.get()
        for key in keys:
            if not self.has_in_port(key):
                self.add_in_port(key,1,display_name = key)
        for port in self.in_ports:
            key = port.name.get()
            if key not in keys:
                self.remove_in_port(key)

    def update_output_ports(self):
        if self.network_name.get() not in NetworkDefManager.outs:
            return
        keys = NetworkDefManager.outs[self.network_name.get()].ins.get()
        for key in keys:
            if not self.has_out_port(key):
                self.add_out_port(key,display_name = key)
        for port in self.out_ports:
            key = port.name.get()
            if key not in keys:
                self.remove_out_port(key)

    def edge_activated(self, edge: Edge, port):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
        self.run(self.start_function)
        self.run(self.end_function, to_queue=False)

    def start_function(self):
        if self.is_destroyed():
            return
        inputs = {}
        for port in self.in_ports:
            inputs[port.name.get()] = port.get_one_data()

        NetworkDefManager.ins[self.network_name.get()].start_function(inputs)

    def end_function(self):
        if self.is_destroyed():
            return
        if self.network_name.get() not in NetworkDefManager.outs:
            return # assume its intended to be a void function
        NetworkDefManager.outs[self.network_name.get()].end_function(self)

    def push_result(self, result:dict):
        for key, value in result.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        NetworkDefManager.calls.remove(self.network_name.get(),self)
        return super().destroy()

class NetworkInNode(Node):
    category = 'torch/neural network'

    # def spawn(self, client_id):
    #     new_node = self.workspace.get_workspace_object().main_editor.get().create_node(type(self))
    #     new_node.add_tag(f'spawned_by_{client_id}')
    #     new_node = self.workspace.get_workspace_object().main_editor.get().create_node(NetworkOutNode)
    #     new_node.add_tag(f'spawned_by_{client_id}')

    def build_node(self):
        self.shape.set('normal')

        self.network_name = self.add_attribute('network name',StringTopic,editor_type='text')
        self.outs = self.add_attribute('outs',ListTopic,editor_type='list')
        self.icon_path.set('nn')

    def init_node(self):
        self.outs.add_validator(ListTopic.unique_validator)
        self.outs.on_insert.add_auto(self.on_output_added)
        self.outs.on_pop.add_auto(self.on_output_removed)
        self.outs.on_set.add_auto(self.on_output_set)

        if self.is_new:
            self.outs.insert('x')

        self.network_name.add_validator(lambda x,_: x not in NetworkDefManager.ins)
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)
        self.update_label()
        
        if self.network_name.get() != '':
            assert self.network_name.get() not in NetworkDefManager.ins
            NetworkDefManager.ins[self.network_name.get()] = self
            for call in NetworkDefManager.calls.get(self.network_name.get()):
                call.update_ports()

        
        if self.is_preview:
            self.label.set('Network Input')
        

    def on_network_name_changed(self, old, new):
        if new != '':
            NetworkDefManager.ins[new] = self
        if old != '':
            NetworkDefManager.ins.pop(old)
        self.update_label()

    def on_network_name_changed_auto(self,new):
        if new != '':
            for call in NetworkDefManager.calls.get(self.network_name.get()):
                call.update_ports()

    def update_label(self):
        self.label.set(f'{self.network_name.get()}\'s input')


    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('outs','network name')

    def on_output_added(self, name, position):
        self.add_out_port(name,display_name = name)

    def on_output_removed(self, name, position):
        self.remove_out_port(name)

    def on_output_set(self, new):
        if self.network_name.get() == '':
            return
        for call in NetworkDefManager.calls.get(self.network_name.get()):
            call.update_input_ports()

    def start_function(self,args:dict):
        for key, value in args.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        if self.network_name.get() != '':
            NetworkDefManager.ins.pop(self.network_name.get())
        return super().destroy()

class NetworkOutNode(Node):
    category = 'torch/neural network'
    def build_node(self):
        self.shape.set('normal')

        self.network_name = self.add_attribute('network name',StringTopic,editor_type='text')
        self.ins = self.add_attribute('ins',ListTopic,editor_type='list')
        self.icon_path.set('nn')

    def init_node(self):
        self.ins.add_validator(ListTopic.unique_validator)
        self.ins.on_insert.add_auto(self.on_input_added)
        self.ins.on_pop.add_auto(self.on_input_removed)
        self.ins.on_set.add_auto(self.on_input_set)

        if self.is_new:
            self.ins.insert('x')

        self.network_name.add_validator(lambda x,_: x not in NetworkDefManager.outs)
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)
        self.update_label()
        
        if self.network_name.get() != '':
            assert self.network_name.get() not in NetworkDefManager.outs
            NetworkDefManager.outs[self.network_name.get()] = self

        
        if self.is_preview:
            self.label.set('Network Output')

            

    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('ins','network name')

    def on_network_name_changed(self, old, new):
        if new != '':
            NetworkDefManager.outs[new] = self
        if old != '':
            NetworkDefManager.outs.pop(old)
        self.update_label()


    def on_network_name_changed_auto(self,new):
        if new != '':
            for call in NetworkDefManager.calls.get(self.network_name.get()):
                call.update_ports()

    def update_label(self):
        self.label.set(f'{self.network_name.get()}\'s output')

    def on_input_added(self, arg_name, position):# currently only support adding to the end
        self.add_in_port(arg_name,1,display_name = arg_name)

    def on_input_removed(self, arg_name, position):
        self.remove_in_port(arg_name)

    def on_input_set(self, new):
        if self.network_name.get() == '':
            return
        for call in NetworkDefManager.calls.get(self.network_name.get()):
            call.update_output_ports()

    def end_function(self,caller:NetworkCallNode):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                self._on_exception(RuntimeError(f'Output data missing for {port.name.get()}'))
                return
        result = {key: self.get_in_port(key).get_one_data() for key in self.ins.get()}
        caller.push_result(result)

    def destroy(self) -> SObjectSerialized:
        if self.network_name.get() != '':
            NetworkDefManager.outs.pop(self.network_name.get())
        return super().destroy()