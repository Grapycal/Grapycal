from typing import List
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.functionNode import FunctionNode
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort
from grapycal import FloatTopic, StringTopic
from objectsync import ObjSetTopic, SObject
import torch
from torch import nn

from .networkDef import NetworkDefManager
from .moduleNode import ModuleNode



class TrainerNode(Node):
    category='torch/training'

    def build_node(self):
        self.label.set('Trainer')
        self.css_classes.append('fit-content')
        self.lr = self.add_attribute('lr',FloatTopic,0.001,editor_type='float')
        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')
        self.init_modules_port = self.add_in_port('initialize network')

        self.train_port = self.add_in_port('train network using loss')

        self.train_mode_port = self.add_in_port('switch to train mode')
        self.eval_port = self.add_in_port('switch to eval mode')

        self.network_names = self.add_text_control(label='network name: ',name='network name')

    def init_node(self):
        self.optimizer : torch.optim.Optimizer | None = None
        self.tracked_modules : set[nn.Module]= set()


    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('modules','lr','device')
        self.restore_controls('network name')

    def get_module_nodes(self)->List[ModuleNode]:
        result: List[ModuleNode] = []
        for name in self.network_names.get().split(','):
            mn = NetworkDefManager.get_module_nodes(name)
            result += mn
        return result

    def getModules(self)->List[nn.Module]:
        return [mn.get_module() for mn in self.get_module_nodes()]

    def check_modules_to_track_changed(self):
        current_modules = set(self.getModules())
        if current_modules != self.tracked_modules:
            self.tracked_modules = current_modules
            self.optimizer = torch.optim.Adam([p for m in self.tracked_modules for p in m.parameters()],lr=self.lr.get())
            self.print('recreated optimizer, ',len(self.tracked_modules),' modules')

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.train_port:
            self.run(self.train_step,loss = edge.get_data())
            return
        
        if port == self.init_modules_port:
            self.run(self.init_modules)
        elif port == self.eval_port:
            self.run(self.eval_mode)
        elif port == self.train_mode_port:
            self.run(self.train_mode)
        port.get_data() # deactivates the edge

    def init_modules(self):
        for mn in self.get_module_nodes():
            mn.create_module_and_update_name(self.device.get())

    def step(self):
        self.check_modules_to_track_changed()
        if self.tracked_modules == set():
            raise Exception('No modules to optimize')
        self.optimizer.step()

    def train_step(self,loss:torch.Tensor):
        self.check_modules_to_track_changed()
        if self.tracked_modules == set():
            return
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
            
    def eval_mode(self):
        for m in self.tracked_modules:
            m.eval()

    def train_mode(self):
        for m in self.tracked_modules:
            m.train()
