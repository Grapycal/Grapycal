from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from .cnn import *
from .tensor_operations import *
from .tensor import *
from .optimizer import *
del ModuleNode



import torch
from torch import nn
import torchvision

from grapycal import ImageControl, Node, TextControl, ButtonControl, Edge, InputPort

import io
import matplotlib
matplotlib.use('agg') # use non-interactive backend
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

class ImageDisplayNode(Node):
    category = 'torch'
    def build_node(self):
        self.label.set('imshow')
        self.shape.set('simple')
        self.img = self.add_control(ImageControl)
        self.add_in_port('tensor', 1)

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.update_image)

    def update_image(self):
        data = self.in_ports[0].edges[0].get_data()

        if isinstance(data, Image.Image):
            data = np.array(data)

        if isinstance(data, torch.Tensor):
            if len(data.shape) == 3:
                data = data.permute(1,2,0)
            data = data.detach().cpu().numpy()

        # use plt to convert to jpg
        buf = io.BytesIO()
        fig = plt.figure()
        plt.imshow(data)
        plt.axis('off')
        plt.savefig(buf,format='jpg',bbox_inches='tight', transparent="True", pad_inches=0)
        plt.close(fig)
        self.img.set_image(buf)

    def input_edge_removed(self, edge: Edge, port: InputPort):
        self.img.set_image(None)

class MnistDatasetNode(Node):
    category = 'torch/dataset'
    def build_node(self):
        self.label.set('MNIST')
        self.out = self.add_out_port('dataset')

    def init_node(self):
        def task():
            ds = torchvision.datasets.mnist.MNIST('data', download=True)
            self.out.push_data(ds,retain=True)
        self.run(task)