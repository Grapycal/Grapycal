from grapycal import FloatTopic
from .moduleNode import SimpleModuleNode
from torch import nn

class ReLUNode(SimpleModuleNode):
    category = 'torch/neural network'
    inputs = ['inp']
    max_in_degree = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('ReLU')
        self.icon_path.set('relu')

    def create_module(self) -> nn.Module:
        return nn.ReLU()

    def forward(self, inp):
        return self.module(inp)
    
class LeakyReLUNode(SimpleModuleNode):
    category = 'torch/neural network'
    inputs = ['inp']
    max_in_degree = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('LeakyReLU')
        self.negative_slope = self.add_attribute('negative_slope', FloatTopic, 0.01, editor_type='float')
        self.icon_path.set('relu')

    def generate_label(self):
        return f'LeakyReLU {self.negative_slope.get()}'

    def create_module(self) -> nn.Module:
        return nn.LeakyReLU(negative_slope=self.negative_slope.get())

    def forward(self, inp):
        return self.module(inp)
    
class SigmoidNode(SimpleModuleNode):
    category = 'torch/neural network'
    inputs = ['inp']
    max_in_degree = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('Sigmoid')

    def create_module(self) -> nn.Module:
        return nn.Sigmoid()

    def forward(self, inp):
        return self.module(inp)
    