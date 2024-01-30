from typing import Dict, Generic, List, TypeVar
from grapycal import Node, ListTopic, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from grapycal.utils.misc import Action
from objectsync.sobject import SObjectSerialized
import torch.nn as nn

from .manager import Manager as M

class NetworkCallNode(Node):
    '''
    A NetworkCallNode represents a call to a network, specified by name.
    Once you set the network name to the NetworkCallNode, Grapycal will search for a NetworkInNode and a NetworkOutNode existing
    in the workspace with the same name. Then, its ports will be updated accroding to the network
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
        M.net.calls.append(self.network_name.get(),self)
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)
        self.update_ports()
        self.label.set(f'{self.network_name.get()}')

    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('network name')

    def on_network_name_changed(self, old, new):
        self.label.set(f'{new}')
        M.net.calls.remove(old,self)
        M.net.calls.append(new,self)

    def on_network_name_changed_auto(self,new):
        self.update_ports()

    def update_ports(self):
        self.update_input_ports()
        self.update_output_ports()

    def update_input_ports(self):
        if self.network_name.get() not in M.net.ins:
            return
        keys = M.net.ins[self.network_name.get()].outs.get()
        for key in keys:
            if not self.has_in_port(key):
                self.add_in_port(key,1,display_name = key)
        for port in self.in_ports:
            key = port.name.get()
            if key not in keys:
                self.remove_in_port(key)

    def update_output_ports(self):
        if self.network_name.get() not in M.net.outs:
            return
        keys = M.net.outs[self.network_name.get()].ins.get()
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

        M.net.ins[self.network_name.get()].start_function(inputs)

    def end_function(self):
        if self.is_destroyed():
            return
        if self.network_name.get() not in M.net.outs:
            return # assume its intended to be a void function
        M.net.outs[self.network_name.get()].end_function(self)

    def push_result(self, result:dict):
        for key, value in result.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        M.net.calls.remove(self.network_name.get(),self)
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

        self.network_name.add_validator(lambda x,_: x not in M.net.ins)
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)
        self.update_label()
        
        if self.network_name.get() != '':
            assert self.network_name.get() not in M.net.ins
            M.net.ins[self.network_name.get()] = self
            for call in M.net.calls.get(self.network_name.get()):
                call.update_ports()

        M.net.on_network_names_changed.invoke()

        
        if self.is_preview:
            self.label.set('Network Input')
        

    def on_network_name_changed(self, old, new):
        if new != '':
            M.net.ins[new] = self
        if old != '':
            M.net.ins.pop(old)
        M.net.on_network_names_changed.invoke()
        self.update_label()

    def on_network_name_changed_auto(self,new):
        if new != '':
            for call in M.net.calls.get(self.network_name.get()):
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
        for call in M.net.calls.get(self.network_name.get()):
            call.update_input_ports()

    def start_function(self,args:dict):
        '''
        First, check mns to have the right configuration (device, mode, etc)
        The check happens every time the network has a forward pass so very dynamic :D
        Hopefully it's not the bottleneck if the network is GPU bound.
        If the network uses CPU, it is already slow so let it be. Or buy a GPU XD
        '''
        name = self.network_name.get()
        device = M.conf.get_device(name)
        if device is not None:
            for mn in M.net.get_module_nodes(name):
                mn.to(device)

        mode = M.conf.get_mode(name)
        if mode is not None:
            for mn in M.net.get_module_nodes(name):
                mn.set_mode(mode)

        # Then, push the data to the input ports
        for key, value in args.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        if self.network_name.get() != '':
            M.net.ins.pop(self.network_name.get())
        M.net.on_network_names_changed.invoke()
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

        self.network_name.add_validator(lambda x,_: x not in M.net.outs)
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set.add_auto(self.on_network_name_changed_auto)
        self.update_label()
        
        if self.network_name.get() != '':
            assert self.network_name.get() not in M.net.outs
            M.net.outs[self.network_name.get()] = self
        M.net.on_network_names_changed.invoke()

        
        if self.is_preview:
            self.label.set('Network Output')

            

    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('ins','network name')

    def on_network_name_changed(self, old, new):
        if new != '':
            M.net.outs[new] = self
        if old != '':
            M.net.outs.pop(old)
        M.net.on_network_names_changed.invoke()
        self.update_label()


    def on_network_name_changed_auto(self,new):
        if new != '':
            for call in M.net.calls.get(self.network_name.get()):
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
        for call in M.net.calls.get(self.network_name.get()):
            call.update_output_ports()

    def end_function(self,caller:NetworkCallNode):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                self.print_exception(RuntimeError(f'Output data missing for {port.name.get()}'))
                return
        result = {key: self.get_in_port(key).get_one_data() for key in self.ins.get()}
        caller.push_result(result)

    def destroy(self) -> SObjectSerialized:
        if self.network_name.get() != '':
            M.net.outs.pop(self.network_name.get())
        M.net.on_network_names_changed.invoke()
        return super().destroy()