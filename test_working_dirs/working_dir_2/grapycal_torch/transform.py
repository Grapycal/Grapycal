    
from typing import Any
from PIL import Image
import numpy as np
from grapycal.sobjects.functionNode import FunctionNode
from grapycal import StringTopic
import torch


class ToTensorNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inputs']
    outputs = ['out']
    def build_node(self):
        super().build_node()
        self.label.set('to tensor')
        self.shape.set('simple')
        self.dtype = self.add_attribute('dtype',StringTopic,'float32',editor_type='text') #TODO: dropdown

    def init_node(self):
        super().init_node()

    def calculate(self, inputs: list[Any]):
        x = inputs[0]
        match x:
            case torch.Tensor():
                return x
            case Image.Image():
                return torch.tensor(np.array(x))
            case np.ndarray():
                return torch.tensor(x)
            case _:
                return torch.tensor(x)