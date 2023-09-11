from abc import ABCMeta, abstractmethod
from typing import Any
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort
from torch import nn
from grapycal import EventTopic
import torch

class ModuleNode(Node,metaclass=ABCMeta):
    category = 'torch/nn'
    def build_node(self):
        #TODO: save and load
        self.shape.set('simple')
        self.label.set('Module')
        self.create_module_topic = self.add_attribute('create_module',EventTopic,editor_type='button')

    def init_node(self):
        self.module: nn.Module|None = None
        self.create_module_topic.on_emit.add_manual(lambda:self.run(self.create_module_and_update_name))

    def create_module_and_update_name(self):
        self.module = self.create_module()
        self.label.set(str(self.module))
        print('created module',self.module)

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
        self.run(self.task)

    def task(self):
        if self.module is None:
            self.create_module_and_update_name()
        self.forward()
        
class SimpleModuleNode(ModuleNode):
    inputs = []
    input_edge_limit = []
    outputs = []
    display_port_names = True

    def build_node(self):
        super().build_node()
        self._input_edge_limit = self.input_edge_limit[:]
        while len(self._input_edge_limit) < len(self.inputs):
            self._input_edge_limit.append(1)
        for i in range(len(self._input_edge_limit)):
            if self._input_edge_limit[i] is None:
                self._input_edge_limit[i] = 64
        for name, max_edges in zip(self.inputs,self._input_edge_limit): #type: ignore
            display_name = name if self.display_port_names else ''
            self.add_in_port(name,max_edges,display_name=display_name)
        for name in self.outputs:
            display_name = name if self.display_port_names else ''
            self.add_out_port(name,display_name=display_name)

    def task(self):
        if self.module is None:
            self.create_module_and_update_name()
        inputs = {}
        for port in self.in_ports:
            inputs[port.name.get()] = port.get_one_data()

        result = self.forward(**inputs)

        if len(self.out_ports) == 1:
            self.out_ports[0].push_data(result)
        else:
            for port, data in zip(self.out_ports, result):
                port.push_data(data)

    @abstractmethod
    def forward(self,**inputs)->Any:
        pass

    