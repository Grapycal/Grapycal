from typing import Dict, List
from grapycal import Node, TextControl, ListTopic, ObjDictTopic, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import ObjDictTopic

class FuncDefManager:
    calls: Dict[str,List['FuncCallNode']] = {}
    ins: Dict[str,'FuncInNode'] = {}
    outs: Dict[str,'FuncOutNode'] = {}

class FuncCallNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('FuncCall')
        self.shape.set('normal')
        self.func_name = self.add_attribute('func_name',StringTopic,editor_type='text')

    def init_node(self):
        FuncDefManager.calls
        self.func_name.on_set.add_auto(self.on_func_name_changed)

    def recover_from_version(self, version, old: NodeInfo):
        super().recover_from_version(version, old)
        self.recover_attributes('func_name')

    def on_func_name_changed(self, new):
        self.label.set(f'Call {new}')
    

class FuncInNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('FuncIn')
        self.shape.set('normal')

        self.outs = self.add_attribute('outs',ListTopic,editor_type='list')

    def init_node(self):
        self.outs.add_validator(ListTopic.unique_validator)
        self.outs.on_insert.add_auto(self.on_output_added)
        self.outs.on_pop.add_auto(self.on_output_removed)

        if self.is_new:
            self.outs.insert('x')

    def recover_from_version(self, version, old: NodeInfo):
        super().recover_from_version(version, old)
        self.recover_attributes('outs')

    def on_output_added(self, name, position):
        self.add_out_port(name,display_name = name)

    def on_output_removed(self, name, position):
        self.remove_out_port(name)

class FuncOutNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('FuncOut')
        self.shape.set('normal')

        self.ins = self.add_attribute('ins',ListTopic,editor_type='list')

    def init_node(self):
        self.ins.on_insert.add_auto(self.on_input_arg_added)
        self.ins.on_pop.add_auto(self.on_input_arg_removed)

        if self.is_new:
            self.ins.insert('x')

    def recover_from_version(self, version, old: NodeInfo):
        super().recover_from_version(version, old)
        self.recover_attributes('ins')

    def on_input_arg_added(self, arg_name, position):# currently only support adding to the end
        self.add_in_port(arg_name,1,display_name = arg_name)

    def on_input_arg_removed(self, arg_name, position):
        self.remove_in_port(arg_name)

    def input_edge_added(self, edge: Edge, port: InputPort):
        self.calculate()

    def edge_activated(self, edge: Edge, port: InputPort):
        self.calculate()

    def calculate(self):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
            if len(port.edges) == 0:
                return
        arg_values = [port.get_one_data() for port in self.in_ports]

        def task():
            pass
                
        self.run(task)