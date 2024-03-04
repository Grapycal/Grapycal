from collections import defaultdict
from os import remove
from typing import Dict, Generic, List, TypeVar
from grapycal import Node, ListTopic, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from ..utils import find_next_valid_name
from objectsync.sobject import SObjectSerialized

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

class FuncDefManager:
    calls: ListDict['FuncCallNode'] = ListDict()
    ins: Dict[str,'FuncInNode'] = {}
    outs: Dict[str,'FuncOutNode'] = {}

class FuncCallNode(Node):
    '''
    A FuncCallNode represents a call to a specific function.
    Once you assign a function name to the FuncCallNode, Grapycal will search for a FuncInNode and a FuncOutNode existing
    in the workspace with the same function name. Then, its ports will be updated accroding to the function
    definition.
    '''

    category = 'function'
    def build_node(self):
        self.label.set('')
        self.shape.set('normal')
        self.func_name = self.add_attribute('func_name',StringTopic,editor_type='text',init_value='MyFunc')
        self.func_name.add_validator(lambda x,_: x != '') # empty name may confuse users

        # manually restore in_ports and out_ports
        if not self.is_new:
            assert self.old_node_info is not None
            for port in self.old_node_info.in_ports:
                self.add_in_port(port.name, 1, display_name=port.name)
            for port in self.old_node_info.out_ports:
                self.add_out_port(port.name, display_name=port.name)
                
    def init_node(self):
        self.update_ports()
        
        self.func_name.on_set2.add_manual(self.on_func_name_changed)
        self.func_name.on_set.add_auto(self.on_func_name_changed_auto)
        FuncDefManager.calls.append(self.func_name.get(),self)
        self.label.set(f' {self.func_name.get()}')

    def on_func_name_changed(self, old, new):
        self.label.set(f' {new}')
        FuncDefManager.calls.remove(old,self)
        FuncDefManager.calls.append(new,self)

    def on_func_name_changed_auto(self,new):
        self.update_ports()

    def update_ports(self):
        self.update_input_ports()
        self.update_output_ports()

    def update_input_ports(self):
        if self.func_name.get() not in FuncDefManager.ins:
            return
        names = FuncDefManager.ins[self.func_name.get()].outs.get()

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
        if self.func_name.get() not in FuncDefManager.outs:
            return
        names = FuncDefManager.outs[self.func_name.get()].ins.get()
    
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

    def build_node(self):
        self.shape.set('normal')

        # setup attributes
        self.outs = self.add_attribute('outs',ListTopic,editor_type='list',init_value=['x'])
        self.outs.add_validator(ListTopic.unique_validator)
        self.restore_attributes('outs')
        
        self.func_name = self.add_attribute('func_name',StringTopic,editor_type='text',init_value='MyFunc')
        self.func_name.add_validator(lambda x,_: x not in FuncDefManager.ins) # function name must be unique
        self.func_name.add_validator(lambda x,_: x != '') # empty name may confuse users
        try:
            self.restore_attributes('func_name')
        except:
            self.func_name.set('MyFunc')
            
        self.func_name.set(find_next_valid_name(self.func_name.get(),FuncDefManager.ins))

    def init_node(self):
        # add callbacks to attributes
        self.outs.on_insert.add_auto(self.on_output_added)
        self.outs.on_pop.add_auto(self.on_output_removed)
        self.outs.on_set.add_auto(self.on_output_set)

        self.func_name.on_set2.add_manual(self.on_func_name_changed)
        self.func_name.on_set.add_auto(self.on_func_name_changed_auto)

        self.update_label()

        for out in self.outs.get():
            self.add_out_port(out,display_name = out)
        
        if not self.is_preview.get():
            FuncDefManager.ins[self.func_name.get()] = self         

    def post_create(self):
        for call in FuncDefManager.calls.get(self.func_name.get()):
            call.update_ports()

    def on_func_name_changed(self, old, new):
        if not self.is_preview.get():
            FuncDefManager.ins[new] = self
            FuncDefManager.ins.pop(old)
        self.update_label()

    def on_func_name_changed_auto(self,new):
        if not self.is_preview.get():
            for call in FuncDefManager.calls.get(self.func_name.get()):
                call.update_ports()

    def update_label(self):
        self.label.set(f'{self.func_name.get()}')

    def on_output_added(self, name, position):
        self.add_out_port(name,display_name = name)

    def on_output_removed(self, name, position):
        self.remove_out_port(name)

    def on_output_set(self, new):
        if not self.is_preview.get():
            print(FuncDefManager.calls.get(self.func_name.get()),self.func_name.get())
            for call in FuncDefManager.calls.get(self.func_name.get()):
                call.update_input_ports()

    def start_function(self,args:dict):
        for key, value in args.items():
            self.get_out_port(key).push_data(value)

    def destroy(self) -> SObjectSerialized:
        if not self.is_preview.get():
            FuncDefManager.ins.pop(self.func_name.get())
        return super().destroy()

class FuncOutNode(Node):
    category = 'function'
    
    def build_node(self):
        self.shape.set('normal')

        # setup attributes
        self.ins = self.add_attribute('ins',ListTopic,editor_type='list',init_value=['x'])
        self.ins.add_validator(ListTopic.unique_validator)
        self.restore_attributes('ins')
        
        self.func_name = self.add_attribute('func_name',StringTopic,editor_type='text',init_value='MyFunc')
        self.func_name.add_validator(lambda x,_: x not in FuncDefManager.outs)
        self.func_name.add_validator(lambda x,_: x != '') # empty name may confuse users
        try:
            self.restore_attributes('func_name')
        except:
            self.func_name.set('MyFunc')

        self.func_name.set(find_next_valid_name(self.func_name.get(),FuncDefManager.outs))

    def init_node(self):
        # add callbacks to attributes
        self.ins.on_insert.add_auto(self.on_input_added)
        self.ins.on_pop.add_auto(self.on_input_removed)
        self.ins.on_set.add_auto(self.on_input_set)

        self.func_name.on_set2.add_manual(self.on_func_name_changed)
        self.func_name.on_set.add_auto(self.on_func_name_changed_auto)

        self.update_label()

        for inp in self.ins.get():
            self.add_in_port(inp,1,display_name = inp)

        if not self.is_preview.get():
            FuncDefManager.outs[self.func_name.get()] = self

    def post_create(self):
        if not self.is_preview.get():
            for call in FuncDefManager.calls.get(self.func_name.get()):
                call.update_ports()

    def on_func_name_changed(self, old, new):
        if not self.is_preview.get():
            FuncDefManager.outs[new] = self
            FuncDefManager.outs.pop(old)
        self.update_label()

    def on_func_name_changed_auto(self,new):
        if not self.is_preview.get():
            for call in FuncDefManager.calls.get(self.func_name.get()):
                call.update_ports()

    def update_label(self):
        self.label.set(f'{self.func_name.get()}')

    def on_input_added(self, arg_name, position):# currently only support adding to the end
        self.add_in_port(arg_name,1,display_name = arg_name)

    def on_input_removed(self, arg_name, position):
        self.remove_in_port(arg_name)

    def on_input_set(self, new):
        if not self.is_preview.get():
            for call in FuncDefManager.calls.get(self.func_name.get()):
                call.update_output_ports()

    def end_function(self,caller:FuncCallNode):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                self.print_exception(RuntimeError(f'Output data missing for {port.name.get()}'))
                return
        result = {key: self.get_in_port(key).get_one_data() for key in self.ins.get()}
        caller.push_result(result)

    def destroy(self) -> SObjectSerialized:
        if not self.is_preview.get():
            FuncDefManager.outs.pop(self.func_name.get())
        return super().destroy()