from typing import Any, Dict
import torch
from grapycal import Node, TextControl


class ZeroesNode(Node):
    category = 'torch/tensor'
    def build_node(self):
        self.shape.set('simple')
        self.label.set('Zeroes')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def double_click(self):
        self.out.push_data(torch.zeros(*map(int, self.shape_text.text.get().split(','))),retain=True)

class OnesNode(Node):
    category = 'torch/tensor'
    def build_node(self):
        self.shape.set('simple')
        self.label.set('Ones')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def double_click(self):
        self.out.push_data(torch.ones(*map(int, self.shape_text.text.get().split(','))),retain=True)

class RandNode(Node):
    category = 'torch/tensor'
    def build_node(self):
        self.shape.set('simple')
        self.label.set('Rand')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def double_click(self):
        self.out.push_data(torch.rand(*map(int, self.shape_text.text.get().split(','))),retain=True)