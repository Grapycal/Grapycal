from typing import Any, Dict
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.activeNode import ActiveNode
import torch
from grapycal import Node, TextControl, FloatTopic, IntTopic


class ZeroesNode(ActiveNode):
    category = 'torch/tensor'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Zeroes')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def task(self):
        self.out.push_data(torch.zeros(*map(int, self.shape_text.text.get().split(','))))

class OnesNode(ActiveNode):
    category = 'torch/tensor'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Ones')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def task(self):
        self.out.push_data(torch.ones(*map(int, self.shape_text.text.get().split(','))))

class RandNode(ActiveNode):
    category = 'torch/tensor'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Rand')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def task(self):
        self.out.push_data(torch.rand(*map(int, self.shape_text.text.get().split(','))))

class RandnNode(ActiveNode):
    category = 'torch/tensor'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Randn')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl)
        self.shape_text.text.set('2,2')
        self.shape_text.label.set('Shape')

    def task(self):
        self.out.push_data(torch.randn(*map(int, self.shape_text.text.get().split(','))))

class GridNode(ActiveNode):
    category = 'torch/tensor'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Grid 2D')

        self.x_start = self.add_attribute('x start',FloatTopic,0,editor_type='float')
        self.x_end = self.add_attribute('x end',FloatTopic,1,editor_type='float')
        self.x_steps = self.add_attribute('x steps',IntTopic,10,editor_type='int')
        self.y_start = self.add_attribute('y start',FloatTopic,0,editor_type='float')
        self.y_end = self.add_attribute('y end',FloatTopic,1,editor_type='float')
        self.y_steps = self.add_attribute('y steps',IntTopic,10,editor_type='int')

        self.out_x = self.add_out_port('x')
        self.out_y = self.add_out_port('y')

        self.x_shape_text = self.add_control(TextControl)
        self.x_shape_text.editable.set(0)

        self.y_shape_text = self.add_control(TextControl)
        self.y_shape_text.editable.set(0)

    def task(self):
        self.x_start.on_set.add_auto(self.update_label_x)
        self.x_end.on_set.add_auto(self.update_label_x)
        self.x_steps.on_set.add_auto(self.update_label_x)
        self.y_start.on_set.add_auto(self.update_label_y)
        self.y_end.on_set.add_auto(self.update_label_y)
        self.y_steps.on_set.add_auto(self.update_label_y)
        if self.is_new:
            self.update_label_x()
            self.update_label_y()

    def recover_from_version(self, version: str, old: NodeInfo):
        super().recover_from_version(version, old)
        self.recover_attributes('x start','x end','x steps','y start','y end','y steps')

    def update_label_x(self,*args):
        self.x_shape_text.text.set(f'x: [{self.x_start.get()},{self.x_end.get()}] / {self.x_steps.get()}')

    def update_label_y(self,*args):
        self.y_shape_text.text.set(f'y: [{self.y_start.get()},{self.y_end.get()}] / {self.y_steps.get()}')

    def double_click(self):
        x_axis = torch.linspace(self.x_start.get(),self.x_end.get(),self.x_steps.get())
        y_axis = torch.linspace(self.y_start.get(),self.y_end.get(),self.y_steps.get())
        yy, xx = torch.meshgrid(y_axis,x_axis)
        self.out_x.push_data(xx)
        self.out_y.push_data(yy)