from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Generic, List, TypeVar
from grapycal import Node, ListTopic, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.utils.misc import Action
from objectsync.sobject import SObjectSerialized
import torch.nn as nn

from .utils import find_next_valid_name

if TYPE_CHECKING:
    from . import GrapycalTorch

class NetworkCallNode(Node):
    '''
    A NetworkCallNode represents a call to a network, specified by name.
    Once you set the network name to the NetworkCallNode, Grapycal will search for a NetworkInNode and a NetworkOutNode existing
    in the workspace with the same name. Then, its ports will be updated accroding to the network
    definition.
    '''
    ext: 'GrapycalTorch'
    category = 'torch/neural network'
    def build_node(self,name:str="Network"):
        self.label.set('')
        self.shape.set('normal')
        self.network_name = self.add_attribute('network name',StringTopic,editor_type='text',init_value=name)
        self.network_name.add_validator(lambda x,_: x != '') # empty name may confuse users
        self.restore_attributes('network name')
        # manually restore in_ports and out_ports
        if not self.is_new:
            assert self.old_node_info is not None
            for port in self.old_node_info.in_ports.values():
                self.add_in_port(port.name, 1, display_name=port.name)
            for port in self.old_node_info.out_ports.values():
                self.add_out_port(port.name, display_name=port.name)
                
        self.update_ports()

    def init_node(self):
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)
        self.ext.net.calls.append(self.network_name.get(),self)
        self.label.set(f' {self.network_name.get()}')
    

    def on_network_name_changed(self, old, new):
        self.label.set(f'{new}')
        self.ext.net.calls.remove(old,self)
        self.ext.net.calls.append(new,self)

    def on_network_name_changed_auto(self,new):
        self.update_ports()

    def update_ports(self):
        self.update_input_ports()
        self.update_output_ports()

    def update_input_ports(self):
        if self.network_name.get() not in self.ext.net.ins:
            return
        names = self.ext.net.ins[self.network_name.get()].outs.get()

        edgesd = defaultdict[str,list[OutputPort]](list)

        # reversed is a hack to make port order consistent when undoing (although it's not very important)
        for port in reversed(self.in_ports.get().copy()):
            name = port.get_name()
            for edge in port.edges.copy():
                edgesd[name].append(edge.get_tail())
                edge.remove()
            self.remove_in_port(name)

        for name in names:
            port = self.add_in_port(name,1)
            edges = edgesd.get(name,[])
            for tail in edges:
                self.editor.create_edge(tail,port)
                
    def update_output_ports(self):
        if self.network_name.get() not in self.ext.net.outs:
            return
        names = self.ext.net.outs[self.network_name.get()].ins.get()
    
        edgesd = defaultdict[str,list[InputPort]](list)
    
        for port in self.out_ports.get().copy():
            name = port.get_name()
            for edge in port.edges.copy():
                edgesd[name].append(edge.get_head())
                edge.remove()
            self.remove_out_port(name)
    
        for name in names:
            port = self.add_out_port(name)
            edges = edgesd.get(name,[])
            for head in edges:
                self.editor.create_edge(port,head)

    def edge_activated(self, edge: Edge, port):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
                    
        self.run(self.end_function, to_queue=False)
        self.run(self.start_function, to_queue=False)

    def start_function(self):
        if self.is_destroyed():
            return
        inputs = {}
        for port in self.in_ports:
            inputs[port.name.get()] = port.get_one_data()

        self.ext.net.ins[self.network_name.get()].start_function(inputs)

    def end_function(self):
        if self.is_destroyed():
            return
        if self.network_name.get() not in self.ext.net.outs:
            return # assume its intended to be a void function
        self.ext.net.outs[self.network_name.get()].end_function(self)

    def push_result(self, result:dict):
        for key, value in result.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        self.ext.net.calls.remove(self.network_name.get(),self)
        return super().destroy()

class NetworkInNode(Node):
    ext: 'GrapycalTorch'
    category = 'torch/neural network'

    def build_node(self,name:str="Network"):
        self.shape.set('normal')

        # setup attributes
        self.outs = self.add_attribute('outs',ListTopic,editor_type='list',init_value=['x'])
        self.outs.add_validator(ListTopic.unique_validator)
        self.restore_attributes('outs')
        
        self.network_name = self.add_attribute('network name',StringTopic,editor_type='text',init_value=name)
        self.network_name.add_validator(lambda x,_: x not in self.ext.net.ins) # function name must be unique
        self.network_name.add_validator(lambda x,_: x != '') # empty name may confuse users
        try:
            self.restore_attributes('network name')
        except:
            self.network_name.set(name)
            
        self.network_name.set(find_next_valid_name(self.network_name.get(),self.ext.net.ins))

        # add callbacks to attributes
        self.outs.on_insert.add_auto(self.on_output_added)
        self.outs.on_pop.add_auto(self.on_output_removed)
        self.outs.on_set.add_auto(self.on_output_set)

        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)

        self.update_label()

        if not self.is_new:
            for out in self.outs.get():
                self.add_out_port(out,display_name = out)
        else:
            self.add_out_port('x',display_name = 'x')

    def init_node(self):
        
        if not self.is_preview.get():
            self.ext.net.add_in(self.network_name.get(),self)     

    def post_create(self):
        for call in self.ext.net.calls.get(self.network_name.get()):
            call.update_ports()
        
    def on_network_name_changed(self, old, new):
        if not self.is_preview.get():
            self.ext.net.remove_in(old)
            self.ext.net.add_in(new,self)
        self.update_label()

    def on_network_name_changed_auto(self,new):
        if not self.is_preview.get():
            for call in self.ext.net.calls.get(self.network_name.get()):
                call.update_ports()

    def update_label(self):
        self.label.set(f'{self.network_name.get()}')

    def on_output_added(self, name, position):
        self.add_out_port(name,display_name = name)

    def on_output_removed(self, name, position):
        self.remove_out_port(name)

    def on_output_set(self, new):
        if not self.is_preview.get():
            print(self.ext.net.calls.get(self.network_name.get()),self.network_name.get())
            for call in self.ext.net.calls.get(self.network_name.get()):
                call.update_input_ports()

    def start_function(self,args:dict):
        for key, value in args.items():
            self.get_out_port(key).push_data(value)
        self.flash_running_indicator()

    def destroy(self) -> SObjectSerialized:
        if not self.is_preview.get():
            self.ext.net.remove_in(self.network_name.get())
        return super().destroy()

class NetworkOutNode(Node):
    ext: 'GrapycalTorch'
    category = 'torch/neural network'
    def build_node(self,name:str="Network"):
        self.shape.set('normal')

        # setup attributes
        self.ins = self.add_attribute('ins',ListTopic,editor_type='list',init_value=['y'])
        self.ins.add_validator(ListTopic.unique_validator)
        self.restore_attributes('ins')
        
        self.network_name = self.add_attribute('network name',StringTopic,editor_type='text',init_value=name)
        self.network_name.add_validator(lambda x,_: x not in self.ext.net.outs) # function name must be unique
        self.network_name.add_validator(lambda x,_: x != '') # empty name may confuse users
        try:
            self.restore_attributes('network name')
        except:
            self.network_name.set(name)
            
        self.network_name.set(find_next_valid_name(self.network_name.get(),self.ext.net.outs))

        if not self.is_new:
            for in_ in self.ins.get():
                self.add_in_port(in_,1,display_name = in_)
        else:
            self.add_in_port('y',1,display_name = 'y')

    def init_node(self):
        # add callbacks to attributes
        self.ins.on_insert.add_auto(self.on_input_added)
        self.ins.on_pop.add_auto(self.on_input_removed)
        self.ins.on_set.add_auto(self.on_input_set)

        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)

        self.update_label()
        
        if not self.is_preview.get():
            self.ext.net.add_out(self.network_name.get(),self)     

    def post_create(self):
        for call in self.ext.net.calls.get(self.network_name.get()):
            call.update_ports()
        
    def on_network_name_changed(self, old, new):
        if not self.is_preview.get():
            self.ext.net.remove_out(old)
            self.ext.net.add_out(new,self)
        self.update_label()

    def on_network_name_changed_auto(self,new):
        if not self.is_preview.get():
            for call in self.ext.net.calls.get(self.network_name.get()):
                call.update_ports()

    def update_label(self):
        self.label.set(f'{self.network_name.get()}')

    def on_input_added(self, name, position):
        self.add_in_port(name,1,display_name = name)

    def on_input_removed(self, name, position):
        self.remove_in_port(name)

    def on_input_set(self, new):
        if not self.is_preview.get():
            for call in self.ext.net.calls.get(self.network_name.get()):
                call.update_output_ports()

    def end_function(self,caller:NetworkCallNode):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                self.print_exception(RuntimeError(f'Output data missing for {port.name.get()}'))
                return
        result = {key: self.get_in_port(key).get_one_data() for key in self.ins.get()}
        caller.push_result(result)
        self.flash_running_indicator()

    def destroy(self) -> SObjectSerialized:
        if not self.is_preview.get():
            self.ext.net.remove_out(self.network_name.get())
        return super().destroy()