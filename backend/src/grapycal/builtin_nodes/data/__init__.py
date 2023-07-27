from typing import Any, Dict
from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import StringTopic, ListTopic

class VariableNode(Node):
    category = 'data'
    
    def build_node(self):
        self.in_port = self.add_in_port('set',1)
        self.out_port = self.add_out_port('get')
        self.text_control = self.add_control(TextControl)
        self.label.set('Variable')
        self.shape.set('simple')

    def init(self):
        super().init()
        self.value = None
        self.has_value = False

    def edge_activated(self, edge: Edge, port: InputPort):
        self.workspace.vars()[self.text_control.text.get()] = edge.get_data()

    def double_click(self):
        self.value = self.workspace.vars()[self.text_control.text.get()]
        self.has_value = True
        for edge in self.out_port.edges:
            edge.push_data(self.value)

    def output_edge_added(self, edge: Edge, port: OutputPort):
        if self.has_value:
            edge.push_data(self.value)

class SplitNode(Node):
    category = 'data'

    def build_node(self):
        self.in_port = self.add_in_port('in',1)
        self.out_port_dict:Dict[str,OutputPort] = {}
        self.label.set('Split')
        self.shape.set('simple')
        self.add_attribute('indices', ListTopic, editor_type='list').set(['x','y','z'])
        

    def edge_activated(self, edge: Edge, port: InputPort):
        pass

        