from typing import Any, Dict
from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import StringTopic

class VariableNode(Node):
    category = 'data'
    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace, is_preview: bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self.label.set('Variable')
        self.shape.set('simple')
        self.value = None
        self.has_value = False
    
    def build(self):
        self.in_port = self.add_in_port('set',1)
        self.out_port = self.add_out_port('get',64)
        self.text_control = self.add_control(TextControl)

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