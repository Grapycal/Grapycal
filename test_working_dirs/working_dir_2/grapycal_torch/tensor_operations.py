from typing import Any
from grapycal import FunctionNode, IntTopic
import torch

class CatNode(FunctionNode):
    category = 'torch/nn'
    def build_node(self):
        self.label.set('C0')
        self.shape.set('round')
        self.dim = self.add_attribute('dim',IntTopic,0,editor_type='int')
        self.add_in_port('in')
        self.add_out_port('out')
    
    def init(self):
        super().init()
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def dim_changed(self,dim):
        self.label.set('C'+str(dim))
    
    def calculate(self, inputs: list[Any]):
        return torch.cat(inputs[0],dim=self.dim.get())

class StackNode(FunctionNode):
    category = 'torch/nn'
    def build_node(self):
        self.dim = self.add_attribute('dim',IntTopic,editor_type='int')
        self.label.set('S0')
        self.shape.set('round')
        self.add_in_port('in')
        self.add_out_port('out')
    
    def init(self):
        super().init()
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def dim_changed(self,dim):
        self.label.set('S'+str(dim))
    
    def calculate(self, inputs: list[Any]):
        return torch.stack(inputs[0],dim=self.dim.get())