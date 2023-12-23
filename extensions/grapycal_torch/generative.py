from grapycal import Node, StringTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.sourceNode import SourceNode
import numpy as np

# ported from https://github.com/pvigier/perlin-numpy/blob/master/perlin2d.py

import torch
import math

def rand_perlin_2d(shape, res, fade = lambda t: 6*t**5 - 15*t**4 + 10*t**3):
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    
    grid = torch.stack(torch.meshgrid(torch.arange(0, res[0], delta[0]), torch.arange(0, res[1], delta[1])), dim = -1) % 1
    angles = 2*math.pi*torch.rand(res[0]+1, res[1]+1)
    gradients = torch.stack((torch.cos(angles), torch.sin(angles)), dim = -1)
    
    tile_grads = lambda slice1, slice2: gradients[slice1[0]:slice1[1], slice2[0]:slice2[1]].repeat_interleave(d[0], 0).repeat_interleave(d[1], 1)
    dot = lambda grad, shift: (torch.stack((grid[:shape[0],:shape[1],0] + shift[0], grid[:shape[0],:shape[1], 1] + shift[1]  ), dim = -1) * grad[:shape[0], :shape[1]]).sum(dim = -1)
    
    n00 = dot(tile_grads([0, -1], [0, -1]), [0,  0])
    n10 = dot(tile_grads([1, None], [0, -1]), [-1, 0])
    n01 = dot(tile_grads([0, -1],[1, None]), [0, -1])
    n11 = dot(tile_grads([1, None], [1, None]), [-1,-1])
    t = fade(grid[:shape[0], :shape[1]])
    return math.sqrt(2) * torch.lerp(torch.lerp(n00, n10, t[..., 0]), torch.lerp(n01, n11, t[..., 0]), t[..., 1])

def rand_perlin_2d_octaves(shape, res, octaves=1, persistence=0.5):
    noise = torch.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        noise += amplitude * rand_perlin_2d(shape, (frequency*res[0], frequency*res[1]))
        frequency *= 2
        amplitude *= persistence
    return noise

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    
    noise = rand_perlin_2d((256, 256), (8, 8))
    plt.figure()
    plt.imshow(noise, cmap='gray', interpolation='lanczos')
    plt.colorbar()
    plt.savefig('perlin.png')
    plt.close()
    
    noise = rand_perlin_2d_octaves((256, 256), (8, 8), 5)
    plt.figure()
    plt.imshow(noise, cmap='gray', interpolation='lanczos')
    plt.colorbar()
    plt.savefig('perlino.png')
    plt.close()

class PerlinNoiseNode(SourceNode):
    category = 'torch/generative'

    def build_node(self):
        super().build_node()
        self.label.set('Perlin Noise')
        self.shape.set('normal')
        self.out_port = self.add_out_port('noise')

    def task(self):
        noise = rand_perlin_2d_octaves((256, 256), (8, 8), 5)
        self.out_port.push_data(noise)

class ConvolutionKernelNode(SourceNode):
    category = 'torch/generative'

    kernels = {
        'gradient_x': (torch.tensor([[-1, 0, 1]]),1/2),
        'gradient_y': (torch.tensor([[-1], [0], [1]]),1/2),
        'laplacian': (torch.tensor([[0, 1, 0], [1, -4, 1], [0, 1, 0]]), 1/4),
        'sobel_x': (torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]), 1/8),
        'sobel_y': (torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]), 1/8),
        'gaussian3': (torch.tensor([[1, 2, 1], [2, 4, 2], [1, 2, 1]]), 1/16),
        'gaussian5': (torch.tensor([[1, 4, 6, 4, 1], [4, 16, 24, 16, 4], [6, 24, 36, 24, 6], [4, 16, 24, 16, 4], [1, 4, 6, 4, 1]]) , 1/256),
        'sharpen': (torch.tensor([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) , 1),
        'emboss': (torch.tensor([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]) , 1/4),
        'edge_detect': (torch.tensor([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]) , 1/8),
        'outline': (torch.tensor([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]), 1),
        'identity': (torch.tensor([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) , 1),
        'ridge_x': (torch.tensor([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]]), 1/3),
        'ridge_y': (torch.tensor([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]]), 1/3),
    }

    def build_node(self):
        super().build_node()
        self.label.set('Convolution Kernel')
        self.shape.set('simple')
        self.out_port = self.add_out_port('kernel')
        self.kernel = self.add_attribute('kernel',StringTopic, 'laplacian',editor_type='options',options=list(self.kernels.keys()))
        self.preview = self.add_text_control('',name='preview',readonly=True)

    def init_node(self):
        super().init_node()
        self.kernel.on_set.add_manual(self.update_preview)
    
    def update_preview(self,new_kernel_name):
        self.preview.set(self.get_preview(self.kernels[new_kernel_name][0]))

    def task(self):
        k,factor = self.kernels[self.kernel.get()]
        self.out_port.push_data(k.to(torch.float32)*factor)

    def get_preview(self,tensor: torch.Tensor):
        res=''
        res += self.kernel.get() + '\n'
        for row in tensor.tolist():
            for val in row:
                res+=f'{val:2d} '
            res+='\n'
        return res[:-1]
    
class ArangeNode(SourceNode):
    category = 'torch/generative'

    def build_node(self):
        super().build_node()
        self.label.set('Arange')
        self.shape.set('simple')
        self.out_port = self.add_out_port('arange',display_name='')
        self.start = self.add_attribute('start',StringTopic, '0',editor_type='text')
        self.stop = self.add_attribute('stop',StringTopic, '10',editor_type='text')
        self.step = self.add_attribute('step',StringTopic, '1',editor_type='text')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('start','stop','step')

    def task(self):
        start = float(self.start.get())
        stop = float(self.stop.get())
        step = float(self.step.get())
        self.out_port.push_data(torch.arange(start,stop,step))