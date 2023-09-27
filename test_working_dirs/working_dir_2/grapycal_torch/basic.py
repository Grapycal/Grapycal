from grapycal.extension.utils import NodeInfo
from .moduleNode import SimpleModuleNode
from torch import nn
from grapycal import IntTopic, Node

class LinearNode(SimpleModuleNode):
    category = 'torch/nn'
    inputs = ['inp']
    input_edge_limit = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('Linear')
        self.in_features = self.add_attribute('in_features',IntTopic,1,editor_type='int')
        self.out_features = self.add_attribute('out_features',IntTopic,1,editor_type='int')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('in_features','out_features')

    def create_module(self) -> nn.Module:
        return nn.Linear(self.in_features.get(),self.out_features.get())
    
    def generate_label(self):
        return f'Linear {self.in_features.get()} → {self.out_features.get()}'

    def forward(self, inp):
        return self.module(inp)


    