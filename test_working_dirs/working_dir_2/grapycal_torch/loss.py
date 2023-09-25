from .moduleNode import SimpleModuleNode
from torch import nn

class BCEWithLogitsLossNode(SimpleModuleNode):
    category = 'torch/loss'
    inputs = ['input','target']
    input_edge_limit = [None]
    outputs = ['loss']
    def build_node(self):
        super().build_node()
        self.label.set('BCEWithLogitsLoss')

    def create_module(self) -> nn.Module:
        return nn.BCEWithLogitsLoss()
    
    def generate_label(self):
        return f'BCEWithLogitsLoss'

    def forward(self, input,target):
        return self.module(input,target)
    
class MSELossNode(SimpleModuleNode):
    category = 'torch/loss'
    inputs = ['input','target']
    input_edge_limit = [None]
    outputs = ['loss']
    def build_node(self):
        super().build_node()
        self.label.set('MSELoss')

    def create_module(self) -> nn.Module:
        return nn.MSELoss()
    
    def generate_label(self):
        return f'MSELoss'

    def forward(self, input,target):
        return self.module(input,target)