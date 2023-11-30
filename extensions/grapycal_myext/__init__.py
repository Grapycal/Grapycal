import inspect
import io
from typing import Any, Dict, List
from grapycal import Node, Edge, InputPort, TextControl, ButtonControl, IntTopic, FunctionNode
from grapycal.core.workspace import Workspace
from grapycal.sobjects.controls.imageControl import ImageControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort

import matplotlib
matplotlib.use('agg') # use non-interactive backend
import matplotlib.pyplot as plt

class IsEvenNode(Node):
    category = 'function'

    def build_node(self):
        self.label.set('IsEven')
        self.add_in_port('number')
        self.out_port = self.add_out_port('isEven')
        self.text = self.add_control(TextControl)
        self.button = self.add_control(ButtonControl, label='Test')
        
    def init_node(self):
        self.i=1
        self.button.on_click += self.button_clicked

    def button_clicked(self):
        self.i += 1
        self.text.text.set(f'IsEven {self.i}')

    def edge_activated(self, edge: Edge, port: InputPort):
        result = edge.get_data() % 2 == 0
        for e in self.out_port.edges:
            e.push_data(result)


class CounterNode(Node):
    category = 'demo'

    def build_node(self):
        self.text = self.add_text_control('0')
        self.button = self.add_button_control('Add')
        self.i = self.add_attribute('count', IntTopic, 0)

    def init_node(self):
        self.button.on_click += self.button_clicked

    def button_clicked(self):
        self.i.set(self.i.get() + 1)
        self.text.set(str(self.i.get()))

# class TestNode2(Node):
#     category = 'test'
#     def build(self):
#         self.add_out_port('out')
#         self.shape.set('simple')
#         self.label.set('ROS Topic')
        
#         self.add_control(TextControl)

# class TestNode3(Node):
#     category = 'test/1/1'
#     def build(self):
#         self.shape.set('round')
#         self.add_in_port('in')
#         self.label.set('<-')
#         self.add_control(TextControl).text.set('<-')

class AdditionNode(FunctionNode):
    '''
    Adds a set of numbers together.
    '''
    category = 'function/math'

    inputs = ['numbers']
    max_in_degree = [None]
    outputs = ['sum']

    def calculate(self, data: List[Any]):
        return sum(data)
