from .moduleNode import ModuleNode
from torch import nn

class Conv2dNode(ModuleNode):
    category = 'torch/nn'
    def build_node(self):
        self.label.set('Conv2d')
        self.add_in_port('in',1)
        self.add_out_port('out')

    def init_node(self):
    
    def create_module(self) -> nn.Module:
        return nn.Conv2d(1, 1,3)
    
    def forward(self):
        inp = self.get_in_port('in').get_one_data()
        out = self.module(inp)
        self.get_out_port('out').push_data(out)