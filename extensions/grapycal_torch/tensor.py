from typing import Any, Dict
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.functionNode import FunctionNode
from grapycal.sobjects.sourceNode import SourceNode
import torch
from grapycal import Node, TextControl, StringTopic, FloatTopic, IntTopic


class ZeroesNode(SourceNode):
    category = 'torch/generative'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Zeroes')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl,'shape_text',text='2,2')
        self.shape_text.label.set('Shape')
        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('shape_text')
        self.restore_attributes('device')

    def task(self):
        self.out.push(torch.zeros(*map(int, self.shape_text.text.get().split(',')),device=self.device.get()))

class OnesNode(SourceNode):
    category = 'torch/generative'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Ones')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl,'shape_text',text='2,2')
        self.shape_text.label.set('Shape')
        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('shape_text')
        self.restore_attributes('device')

    def task(self):
        self.out.push(torch.ones(*map(int, self.shape_text.text.get().split(',')),device=self.device.get()))

class RandNode(SourceNode):
    category = 'torch/generative'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Rand')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl,'shape_text',text='2,2')
        self.shape_text.label.set('Shape')
        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')
        self.min = self.add_attribute('min',FloatTopic,0,editor_type='float')
        self.max = self.add_attribute('max',FloatTopic,1,editor_type='float')


    def task(self):
        self.out.push(torch.rand(*map(int, self.shape_text.text.get().split(',')),device=self.device.get())*(self.max.get()-self.min.get())+self.min.get())

class RandnNode(SourceNode):
    category = 'torch/generative'
    def build_node(self):
        super().build_node()
        self.shape.set('simple')
        self.label.set('Randn')
        self.out = self.add_out_port('tensor')
        self.shape_text = self.add_control(TextControl,'shape_text',text='2,2')
        self.shape_text.label.set('Shape')
        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')
        

    def task(self):
        self.out.push(torch.randn(*map(int, self.shape_text.text.get().split(',')),device=self.device.get()))

class GridNode(SourceNode):
    category = 'torch/generative'
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

        self.x_shape_text = self.add_control(TextControl,'x_shape_text')
        self.x_shape_text.editable.set(0)

        self.y_shape_text = self.add_control(TextControl,'y_shape_text')
        self.y_shape_text.editable.set(0)

        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')

    def init_node(self):
        super().init_node()
        self.x_start.on_set.add_auto(self.update_label_x)
        self.x_end.on_set.add_auto(self.update_label_x)
        self.x_steps.on_set.add_auto(self.update_label_x)
        self.y_start.on_set.add_auto(self.update_label_y)
        self.y_end.on_set.add_auto(self.update_label_y)
        self.y_steps.on_set.add_auto(self.update_label_y)
        if self.is_new:
            self.update_label_x()
            self.update_label_y()

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('x start','x end','x steps','y start','y end','y steps','device')
        self.restore_controls('x_shape_text','y_shape_text')

    def update_label_x(self,*args):
        self.x_shape_text.text.set(f'x: [{self.x_start.get()},{self.x_end.get()}] / {self.x_steps.get()}')

    def update_label_y(self,*args):
        self.y_shape_text.text.set(f'y: [{self.y_start.get()},{self.y_end.get()}] / {self.y_steps.get()}')

    def task(self):
        x_axis = torch.linspace(self.x_start.get(),self.x_end.get(),self.x_steps.get(),device=self.device.get())
        y_axis = torch.linspace(self.y_start.get(),self.y_end.get(),self.y_steps.get(),device=self.device.get())
        yy, xx = torch.meshgrid(y_axis,x_axis)
        self.out_x.push(xx)
        self.out_y.push(yy)

class RandnLikeNode(FunctionNode):
    category = 'torch/generative'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('Randn Like')
        self.shape.set('simple')
        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')

    def calculate(self, inp) -> Any:
        return torch.randn_like(inp,device=self.device.get())