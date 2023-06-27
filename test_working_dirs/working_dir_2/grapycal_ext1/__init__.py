from typing import Any
from grapycal.sobjects.controls.textControl import TextControl
from grapycal.sobjects.node import Node

class TestNode(Node):
    category = 'test'
    def build(self):
        self.add_in_port('in')
        self.add_in_port('in2')
        self.add_out_port('out')
        self.add_control(TextControl)