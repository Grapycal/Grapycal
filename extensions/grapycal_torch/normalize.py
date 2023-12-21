from grapycal.extension.utils import NodeInfo
from .moduleNode import SimpleModuleNode
from torch import nn
from grapycal import IntTopic, Node, FloatTopic

class BatchNorm2dNode(SimpleModuleNode):
    category = 'torch/neural network'
    inputs = ['inp']
    max_in_degree = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('BatchNorm2d')
        self.num_features = self.add_attribute('num_features',IntTopic,1,editor_type='int')
        self.icon_path.set('bn')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('num_features')

    def create_module(self) -> nn.Module:
        return nn.BatchNorm2d(self.num_features.get())
    
    def generate_label(self):
        return f'BatchNorm2d {self.num_features.get()}'

    def forward(self, inp):
        return self.module(inp)

class Dropout2dNode(SimpleModuleNode):
    category = 'torch/neural network'
    inputs = ['inp']
    max_in_degree = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('Dropout2d')
        self.p = self.add_attribute('p',FloatTopic,0.5,editor_type='float')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('p')

    def create_module(self) -> nn.Module:
        return nn.Dropout2d(self.p.get())
    
    def generate_label(self):
        return f'Dropout2d {self.p.get()}'

    def forward(self, inp):
        return self.module(inp)

class DropoutNode(SimpleModuleNode):
    category = 'torch/neural network'
    inputs = ['inp']
    max_in_degree = [None]
    outputs = ['out']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('Dropout')
        self.p = self.add_attribute('p',FloatTopic,0.5,editor_type='float')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('p')

    def create_module(self) -> nn.Module:
        return nn.Dropout(self.p.get())
    
    def generate_label(self):
        return f'Dropout {self.p.get()}'

    def forward(self, inp):
        return self.module(inp)