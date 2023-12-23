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

class CIFAR10DatasetNode(SourceNode):
    category = 'torch/dataset'
    def build_node(self):
        super().build_node()
        self.label.set('CIFAR10 Dataset')
        self.out = self.add_out_port('CIFAR10 Dataset')

    def task(self):
        ds = torchvision.datasets.cifar.CIFAR10('data', download=True)
        self.out.push_data(ds)

class CelebADatasetNode(SourceNode):
    category = 'torch/dataset'
    def build_node(self):
        super().build_node()
        self.label.set('CelebA Dataset')
        self.out = self.add_out_port('CelebA Dataset')

    def task(self):
        ds = torchvision.datasets.celeba.CelebA('data', download=True)
        self.out.push_data(ds)

class ImageFolderWithoutLabel(torchvision.datasets.ImageFolder):
    def __getitem__(self, index: int):
        """
        Args:
            index (int): Index
    
        Returns:
            tuple: (sample, target) where target is class_index of the target class.
        """
        path, target = self.samples[index]
        sample = self.loader(path)
        if self.transform is not None:
            sample = self.transform(sample)
        return sample
    

class ImageDatasetNode(SourceNode):
    category = 'torch/dataset'
    def build_node(self):
        super().build_node()
        self.label.set('Image Dataset')
        self.path = self.add_text_control('path',name='path')
        self.out = self.add_out_port('Image Dataset')

    def task(self):
        tr = torchvision.transforms.ToTensor()
        ds = ImageFolderWithoutLabel(self.path.text.get(),tr)
        self.out.push_data(ds)



del ModuleNode, SimpleModuleNode, Node, SourceNode, FunctionNode