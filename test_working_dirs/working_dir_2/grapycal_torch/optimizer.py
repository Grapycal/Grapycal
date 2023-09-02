from grapycal.sobjects.node import Node
from objectsync import ObjSetTopic
import torch


class OptimizerNode(Node):
    category='torch'

    def build_node(self):
        self.label.set('Optimizer')
        self.add_attribute('modules',ObjSetTopic,editor_type='objSet')

    def init_node(self):
        self.optimizer : torch.optim.Optimizer | None = None