from cProfile import label
from typing import Any
from grapycal.sobjects.controls.textControl import TextControl
from grapycal.sobjects.node import Node

class TestNode(Node):
    category = 'test'
    def build(self):
        self.add_in_port('in')
        self.add_in_port('in2')
        self.add_out_port('out')
        self.label.set('Normal Node')
        self.add_control(TextControl)

class TestNode2(Node):
    category = 'test'
    def build(self):
        self.add_in_port('in')
        self.add_out_port('out')
        self.add_out_port('out2')
        self.add_out_port('out3')
        self.shape.set('simple')
        self.label.set('Simple Node')
        self.add_control(TextControl)
        self.add_control(TextControl)

class TestNode3(Node):
    category = 'test/1/1'
    def build(self):
        self.add_in_port('in')
        self.add_out_port('out')
        self.shape.set('simple')
        self.label.set('Simple Node')
        text_ctrl = self.add_control(TextControl,label='Ctrl')
        text_ctrl.text.set('Hello World')