
from grapycal_torch.moduleNode import SimpleModuleNode
from grapycal import StringTopic
from torch import nn


class MaxPool2dNode(SimpleModuleNode):
    category = 'torch/neural network'
    inputs = ['inp']
    max_in_degree = [1]
    outputs = ['out']
    def build_node(self,kernel_size=2,stride=2):
        super().build_node()
        self.label.set('MaxPooling2d')
        self.kernel_size = self.add_attribute('kernel_size',StringTopic , editor_type='text', init_value=str(kernel_size))
        self.stride = self.add_attribute('stride',StringTopic , editor_type='text', init_value=str(stride))
        self.icon_path.set('cnn')

    def create_module(self) -> nn.Module:
        return nn.MaxPool2d(
            kernel_size=eval(self.kernel_size.get()),
            stride=eval(self.stride.get())
        )
                         
    def generate_label(self):
        return f'MaxPooling2D {self.kernel_size.get()} {self.stride.get()}'
    
    def forward(self, inp):
        return self.module(inp)