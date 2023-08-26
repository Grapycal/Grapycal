from abc import ABCMeta, abstractmethod
from turtle import forward
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort
from torch import nn

class ModuleNode(Node,metaclass=ABCMeta):
    category = 'torch/nn'
    def build_node(self):
        #TODO: save and load
        self.label.set('Module')

    def init_node(self):
        self.module: nn.Module|None = None
        self.module = self.create_module() #TODO: move to button pressed

    @abstractmethod
    def create_module(self)->nn.Module:
        pass

    @abstractmethod
    def forward(self):
        '''
        Consume the input from the input ports, run a forward pass, and output the result to the output ports
        '''
        pass

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.forward)
        

