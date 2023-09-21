from typing import List
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort
from grapycal import FloatTopic, StringTopic
from objectsync import ObjSetTopic, SObject
import torch
from torch import nn
from .moduleNode import ModuleNode


class OptimizerNode(Node):
    category='torch/training'

    def build_node(self):
        self.label.set('Optimizer')
        self.modules = self.add_attribute('modules',ObjSetTopic,editor_type='objSet')
        self.lr = self.add_attribute('lr',FloatTopic,0.001,editor_type='float')
        self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')
        self.init_modules_port = self.add_in_port('init modules')
        self.zero_grad_port = self.add_in_port('zero_grad()')
        self.step_port = self.add_in_port('step()')

    def init_node(self):
        self.optimizer : torch.optim.Optimizer | None = None
        self.tracked_modules : set[nn.Module]|None = set()

    def recover_from_version(self, version: str, old: NodeInfo):
        super().recover_from_version(version, old)
        self.recover_attributes('modules','lr','device')

    def getModules(self)->List[nn.Module]:
        result: List[nn.Module] = []
        for mn in self.modules.get():
            if isinstance(mn,ModuleNode) and mn.module is not None:
                result.append(mn.module)
        return result

    def recreate_optimizer_if_needed(self):
        current_modules = set(self.getModules())
        if current_modules != self.tracked_modules:
            self.tracked_modules = current_modules
            self.optimizer = torch.optim.Adam([p for m in self.tracked_modules for p in m.parameters()],lr=self.lr.get())
            print('recreated optimizer, ',len(self.tracked_modules),' modules')

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.step_port:
            self.run(self.step)
        elif port == self.zero_grad_port:
            self.run(self.zero_grad)
        elif port == self.init_modules_port:
            self.run(self.init_modules)

    def init_modules(self):
        for mn in self.modules.get():
            if isinstance(mn,ModuleNode):
                mn.create_module_and_update_name(self.device.get())

    def step(self):
        self.recreate_optimizer_if_needed()
        if self.tracked_modules == set():
            return
        self.optimizer.step()

    def zero_grad(self):
        self.recreate_optimizer_if_needed()
        if self.tracked_modules == set():
            return
        self.optimizer.zero_grad()
            