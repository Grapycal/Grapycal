from ast import pattern
from typing import Any
from grapycal import FunctionNode, IntTopic, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.textControl import TextControl
import torch
import torch.nn.functional as F
import einops

class CatNode(FunctionNode):
    category = 'torch/operations'
    def build_node(self):
        self.label.set('🐱0')
        self.shape.set('round')
        self.dim = self.add_attribute('dim',IntTopic,0,editor_type='int')
        self.add_in_port('inputs')
        self.add_out_port('out')
    
    def init_node(self):
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('dim')

    def dim_changed(self,dim):
        self.label.set('🐱'+str(dim))
    
    def calculate(self, inputs: list[Any]):
        return torch.cat(inputs,dim=self.dim.get())

class StackNode(FunctionNode):
    category = 'torch/operations'
    def build_node(self):
        self.dim = self.add_attribute('dim',IntTopic,editor_type='int')
        self.label.set('☰0')
        self.shape.set('round')
        self.add_in_port('inputs')
        self.add_out_port('out')
    
    def init_node(self):
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('dim')

    def dim_changed(self,dim):
        self.label.set('☰'+str(dim))
    
    def calculate(self, inputs: list[Any]):
        return torch.stack(inputs,dim=self.dim.get())
    
class UnsqueezeNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inputs']
    outputs = ['out']
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.dim = self.add_attribute('dim',IntTopic,editor_type='int')
        self.label.set('U0')
        self.shape.set('round')
    
    def init_node(self):
        super().init_node()
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('dim')

    def dim_changed(self,dim):
        self.label.set('U'+str(dim))
    
    def calculate(self, inputs):
        return torch.unsqueeze(inputs[0],dim=self.dim.get())
    
class SqueezeNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inputs']
    outputs = ['out']
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.dim = self.add_attribute('dim',IntTopic,editor_type='int')
        self.label.set('S0')
        self.shape.set('round')
    
    def init_node(self):
        super().init_node()
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('dim')

    def dim_changed(self,dim):
        self.label.set('S'+str(dim))
    
    def calculate(self, inputs):
        return torch.squeeze(inputs[0],dim=self.dim.get())
    
class RearrangeNode(FunctionNode):
    category = 'torch/operations'
    def build_node(self):
        super().build_node()
        self.pattern_control = self.add_control(TextControl,name='pattern_control',label='')
        self.label.set('Rearrange')
        self.shape.set('simple')
        self.add_in_port('inputs')
        self.add_out_port('out')
        self.css_classes.append('fit-content')

    def init_node(self):
        super().init_node()
        if self.is_new:
            self.pattern_control.text.set('b c h w -> b (c h w)')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('pattern_control')

    def calculate(self, inputs):
        raw_arg = self.pattern_control.text.get().split(',')
        pattern = raw_arg[0]
        axes_lengths = {}
        for arg in raw_arg[1:]:
            key,value = arg.split('=')
            key = key.strip()
            value = int(value.strip())
            axes_lengths[key] = value
            
        return einops.rearrange(inputs[0],pattern,**axes_lengths)
    
class BackwardNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inputs']
    def build_node(self):
        super().build_node()
        self.label.set('↤')
        self.shape.set('round')

    def calculate(self, inputs: list[Any]):
        inputs[0].backward()

class ToCudaNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inputs']
    outputs = ['tensor']
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('cu')
        self.shape.set('round')

    def calculate(self, inputs: list[Any]):
        return inputs[0].cuda()
    
class FConv2DNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['x','kernel']
    max_in_degree = [1,1]
    outputs = ['result']
    def build_node(self):
        super().build_node()
        self.label.set('Conv2D')
        self.shape.set('normal')
        self.icon_path.set('cnn')

    def calculate(self, x:torch.Tensor, kernel:torch.Tensor):
        is_c1hw = False
        orig_x = x
        orig_kernel = kernel
        if len(x.shape) == 2:
            x = x.unsqueeze(0)
        if len(kernel.shape) == 2:
            kernel = kernel.unsqueeze(0).unsqueeze(0)
        elif len(kernel.shape) == 3:
            kernel = kernel.unsqueeze(0)
        if len(x.shape) == 3 and x.shape[0] != 1 and kernel.shape[1] == 1:
            is_c1hw = True
            x = x.unsqueeze(1)
        y = F.conv2d(x,kernel,padding=kernel.shape[-1]//2)
        if is_c1hw:
            y = y.squeeze(1)
        if len(orig_x.shape) == 2:
            y = y.squeeze(0)
        return y
    
class SinNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('sin')
        self.shape.set('round')

    def calculate(self, inp):
        return torch.sin(inp)
    
class CosNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('cos')
        self.shape.set('round')

    def calculate(self, inp):
        return torch.cos(inp)
    
class CumprodNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('cumprod 0')
        self.shape.set('simple')
        self.dim = self.add_attribute('dim',IntTopic,0,editor_type='int')

    def init_node(self):
        super().init_node()
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def dim_changed(self,dim):
        self.label.set('cumprod '+str(dim))

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('dim')

    def calculate(self, inp):
        return torch.cumprod(inp,dim=self.dim.get())
    
class GatherNode(FunctionNode):
    category = 'torch/operations'
    inputs = ['inp','index']
    outputs = ['result']
    max_in_degree = [1,1]
    def build_node(self):
        super().build_node()
        self.label.set('gather 0')
        self.shape.set('simple')
        self.dim = self.add_attribute('dim',IntTopic,0,editor_type='int')

    def init_node(self):
        super().init_node()
        self.dim.on_set.add_manual(self.dim_changed)
        if self.is_new:
            self.dim.set(0)

    def dim_changed(self,dim):
        self.label.set('gather '+str(dim))

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('dim')

    def calculate(self, inp,index):
        return torch.gather(inp,dim=self.dim.get(),index=index)