from typing import Dict, List
from grapycal import Node, ListTopic, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from objectsync.sobject import SObjectSerialized

class ListDict:
    def __init__(self):
        self.d:Dict[str,List] = {}

    def append(self, key, value):
        if key not in self.d:
            self.d[key] = []
        self.d[key].append(value)

    def remove(self, key, value):
        self.d[key].remove(value)
        if len(self.d[key]) == 0:
            self.d.pop(key)

    def has(self, key):
        return key in self.d
    
    def get(self, key):
        if key not in self.d:
            return []
        return self.d[key]

class FuncDefManager:
    calls: ListDict = ListDict()
    ins: Dict[str,'FuncInNode'] = {}
    outs: Dict[str,'FuncOutNode'] = {}

class FuncCallNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('Call:')
        self.shape.set('normal')
        self.func_name = self.add_attribute('func_name',StringTopic,editor_type='text')

    def init_node(self):
        FuncDefManager.calls.append(self.func_name.get(),self)
        self.func_name.on_set2.add_manual(self.on_func_name_changed)

    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('func_name')

    def on_func_name_changed(self, old, new):
        self.label.set(f'Call: {new}')
        FuncDefManager.calls.remove(old,self)
        FuncDefManager.calls.append(new,self)
        self.update_input_ports()
        self.update_output_ports()

    def update_input_ports(self):
        if self.func_name.get() not in FuncDefManager.ins:
            return
        keys = FuncDefManager.ins[self.func_name.get()].outs.get()
        for key in keys:
            if not self.has_in_port(key):
                self.add_in_port(key,1,display_name = key)
        for port in self.in_ports:
            key = port.name.get()
            if key not in keys:
                self.remove_in_port(key)

    def update_output_ports(self):
        if self.func_name.get() not in FuncDefManager.outs:
            return
        keys = FuncDefManager.outs[self.func_name.get()].ins.get()
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

        FuncDefManager.ins[self.func_name.get()].start_function(inputs)

    def end_function(self):
        if self.is_destroyed():
            return
        if self.func_name.get() not in FuncDefManager.outs:
            return # assume its intended to be a void function
        FuncDefManager.outs[self.func_name.get()].end_function(self)

    def push_result(self, result:dict):
        for key, value in result.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        FuncDefManager.calls.remove(self.func_name.get(),self)
        return super().destroy()

class FuncInNode(Node):
    category = 'function'

    # def spawn(self, client_id):
    #     new_node = self.workspace.get_workspace_object().main_editor.get().create_node(type(self))
    #     new_node.add_tag(f'spawned_by_{client_id}')
    #     new_node = self.workspace.get_workspace_object().main_editor.get().create_node(FuncOutNode)
    #     new_node.add_tag(f'spawned_by_{client_id}')

    def build_node(self):
        self.shape.set('normal')

        self.func_name = self.add_attribute('func_name',StringTopic,editor_type='text')
        self.outs = self.add_attribute('outs',ListTopic,editor_type='list')

    def init_node(self):
        self.outs.add_validator(ListTopic.unique_validator)
        self.outs.on_insert.add_auto(self.on_output_added)
        self.outs.on_pop.add_auto(self.on_output_removed)
        self.outs.on_set.add_auto(self.on_output_set)

        if self.is_new:
            self.outs.insert('x')

        self.func_name.add_validator(lambda x,_: x not in FuncDefManager.ins)
        self.func_name.on_set2.add_manual(self.on_func_name_changed)
        self.update_label()
        
        if self.func_name.get() != '':
            assert self.func_name.get() not in FuncDefManager.ins
            FuncDefManager.ins[self.func_name.get()] = self
        

    def on_func_name_changed(self, old, new):
        if new != '':
            FuncDefManager.ins[new] = self
        if old != '':
            FuncDefManager.ins.pop(old)
        self.update_label()

    def update_label(self):
        self.label.set(f'Input of: {self.func_name.get()}')


    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('outs','func_name')

    def on_output_added(self, name, position):
        self.add_out_port(name,display_name = name)

    def on_output_removed(self, name, position):
        self.remove_out_port(name)

    def on_output_set(self, new):
        if self.func_name.get() == '':
            return
        for call in FuncDefManager.calls.get(self.func_name.get()):
            call.update_input_ports()

    def start_function(self,args:dict):
        for key, value in args.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        if self.func_name.get() != '':
            FuncDefManager.ins.pop(self.func_name.get())
        return super().destroy()

class FuncOutNode(Node):
    category = 'function'
    def build_node(self):
        self.shape.set('normal')

        self.func_name = self.add_attribute('func_name',StringTopic,editor_type='text')
        self.ins = self.add_attribute('ins',ListTopic,editor_type='list')

    def init_node(self):
        self.ins.add_validator(ListTopic.unique_validator)
        self.ins.on_insert.add_auto(self.on_input_added)
        self.ins.on_pop.add_auto(self.on_input_removed)
        self.ins.on_set.add_auto(self.on_input_set)

        if self.is_new:
            self.ins.insert('x')

        self.func_name.add_validator(lambda x,_: x not in FuncDefManager.outs)
        self.func_name.on_set2.add_manual(self.on_func_name_changed)
        self.update_label()
        
        if self.func_name.get() != '':
            assert self.func_name.get() not in FuncDefManager.outs
            FuncDefManager.outs[self.func_name.get()] = self

    def restore_from_version(self, version, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('ins','func_name')

    def on_func_name_changed(self, old, new):
        if new != '':
            FuncDefManager.outs[new] = self
        if old != '':
            FuncDefManager.outs.pop(old)
        self.update_label()

    def update_label(self):
        self.label.set(f'Output of: {self.func_name.get()}')

    def on_input_added(self, arg_name, position):# currently only support adding to the end
        self.add_in_port(arg_name,1,display_name = arg_name)

    def on_input_removed(self, arg_name, position):
        self.remove_in_port(arg_name)

    def on_input_set(self, new):
        if self.func_name.get() == '':
            return
        for call in FuncDefManager.calls.get(self.func_name.get()):
            call.update_output_ports()

    def end_function(self,caller:FuncCallNode):
        result = {key: self.get_in_port(key).get_one_data() for key in self.ins.get()}
        caller.push_result(result)

    def destroy(self) -> SObjectSerialized:
        if self.func_name.get() != '':
            FuncDefManager.outs.pop(self.func_name.get())
        return super().destroy()