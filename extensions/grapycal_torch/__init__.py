from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from .basic import *
from .cnn import *
from .activation import *
from .tensor_operations import *
from .tensor import *
from .optimizerNode import *
from .transform import *
from .dataloader import *
from .normalize import *
from .loss import *
from .generative import *
from .networkDef import *



import torch
from torch import nn
import torchvision

from grapycal import ImageControl, Node, TextControl, ButtonControl, Edge, InputPort

import io
import matplotlib
matplotlib.use('agg') # use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

class MnistDatasetNode(SourceNode):
    category = 'torch/dataset'
    def build_node(self):
        super().build_node()
        self.label.set('MNIST Dataset')
        self.out = self.add_out_port('MNIST Dataset')

    def task(self):
        ds = torchvision.datasets.mnist.MNIST('data', download=True)
        self.out.push_data(ds)


del ModuleNode, SimpleModuleNode, Node, SourceNode, FunctionNode