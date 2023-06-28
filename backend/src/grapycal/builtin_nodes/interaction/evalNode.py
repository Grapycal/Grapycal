import logging
from typing import Any
from grapycal.builtin_nodes.textInputNode import TextInputNode
from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import StringTopic

class EvalNode(Node):
    category = 'interaction'
    def pre_build(self, attribute_values, workspace, is_preview:bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self.label.set('eval')
        self.shape.set('simple')
        self.has_value = False
        self.value = None
    
    def build(self):
        super().build()
        self.out_port = self.add_out_port('')
        self.text_control = self.add_control(TextControl)

    def activate(self):
        expression = self.text_control.text.get()
        self.value = eval(expression)
        self.has_value = True
        for edge in self.out_port.edges:
            edge.push_data(self.value)

    def double_click(self):
        self.activate()

    def output_edge_added(self, edge: Edge, port: OutputPort):
        if self.has_value:
            edge.push_data(self.value)