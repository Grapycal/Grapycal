from typing import Any, Dict
import torch
from grapycal import Node, TextControl, FloatTopic, IntTopic


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

class RandnNode(Node):
    category = 'torch/tensor'
    def build_node(self):
        self.shape.set('simple')
        self.label.set('Randn')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def double_click(self):
        self.out.push_data(torch.randn(*map(int, self.shape_text.text.get().split(','))),retain=True)

class GridNode(Node):
    category = 'torch/tensor'
    def build_node(self):
        self.shape.set('simple')
        self.label.set('Grid 2D')

        self.x_start = self.add_attribute('x start',FloatTopic,0,editor_type='float')
        self.x_end = self.add_attribute('x end',FloatTopic,1,editor_type='float')
        self.x_steps = self.add_attribute('x steps',IntTopic,0.1,editor_type='int')
        self.y_start = self.add_attribute('y start',FloatTopic,0,editor_type='float')
        self.y_end = self.add_attribute('y end',FloatTopic,1,editor_type='float')
        self.y_steps = self.add_attribute('y steps',IntTopic,0.1,editor_type='int')

        self.out_x = self.add_out_port('x')
        self.out_y = self.add_out_port('y')

    def double_click(self):
        x_axis = torch.linspace(self.x_start.get(),self.x_end.get(),self.x_steps.get())
        y_axis = torch.linspace(self.y_start.get(),self.y_end.get(),self.y_steps.get())
        xx, yy = torch.meshgrid(x_axis, y_axis)
        self.out_x.push_data(xx,retain=True)
        self.out_y.push_data(yy,retain=True)