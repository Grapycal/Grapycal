from grapycal import FloatTopic
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
    
class LeakyReLUNode(SimpleModuleNode):
    category = 'torch/nn'
    inputs = ['inp']
    input_edge_limit = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('LeakyReLU')
        self.negative_slope = self.add_attribute('negative_slope', FloatTopic, 0.01, editor_type='float')

    def generate_label(self):
        return f'LeakyReLU {self.negative_slope.get()}'

    def create_module(self) -> nn.Module:
        return nn.LeakyReLU(negative_slope=self.negative_slope.get())

    def forward(self, inp):
        return self.module(inp)
    