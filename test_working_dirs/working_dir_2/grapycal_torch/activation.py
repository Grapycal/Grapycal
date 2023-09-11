from .moduleNode import SimpleModuleNode
from torch import nn

class ReLUNode(SimpleModuleNode):
    category = 'torch/nn'
    inputs = ['inp']
    input_edge_limit = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('ReLU')

    def create_module(self) -> nn.Module:
        return nn.ReLU()

    def forward(self, inp):
        return self.module(inp)
    