from grapycal.extension.utils import NodeInfo
from objectsync import IntTopic, StringTopic
from .moduleNode import ModuleNode
from torch import nn

class Conv2dNode(ModuleNode):
    category = 'torch/nn'
    def build_node(self):
        super().build_node()
        self.label.set('Conv2d')
        self.add_in_port('in',1)
        self.add_out_port('out')
        self.in_channels = self.add_attribute('in_channels',IntTopic , editor_type='int',init_value=1)
        self.out_channels = self.add_attribute('out_channels',IntTopic , editor_type='int',init_value=1)
        self.kernal_size = self.add_attribute('kernel_size',StringTopic , editor_type='text', init_value='3,3')
        self.padding = self.add_attribute('padding',StringTopic , editor_type='text', init_value='1,1')

    def init_node(self):
        super().init_node()

    def recover_from_version(self, version: str, old: NodeInfo):
        super().recover_from_version(version, old)
        self.in_channels.set(old.attributes['in_channels'])
        self.out_channels.set(old.attributes['out_channels'])
        self.kernal_size.set(old.attributes['kernel_size'])
        self.padding.set(old.attributes['padding'])
    
    def create_module(self) -> nn.Module:
        return nn.Conv2d(
            in_channels=self.in_channels.get(),
            out_channels=self.out_channels.get(),
            kernel_size=eval(self.kernal_size.get()),
            padding=eval(self.padding.get())
        )
                         
    def generate_label(self):
        self.module: nn.Conv2d
        return f'Conv2d {self.module.in_channels} → {self.module.out_channels} {self.module.kernel_size}'
    
    def forward(self):
        inp = self.get_in_port('in').get_one_data()
        out = self.module(inp)
        self.get_out_port('out').push_data(out)