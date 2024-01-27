from typing import List
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.buttonControl import ButtonControl
from grapycal.sobjects.controls.optionControl import OptionControl
from grapycal.sobjects.controls.textControl import TextControl
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
        self.device = self.add_in_port('device',control_type=TextControl)
        self.network_names = self.add_in_port('network names',control_type=TextControl)
        self.init_modules_port = self.add_in_port('initialize network', control_type=ButtonControl)

        self.train_port = self.add_in_port('train network using loss')

        self.train_mode_port = self.add_in_port('switch to train mode', control_type=ButtonControl)
        self.eval_port = self.add_in_port('switch to eval mode', control_type=ButtonControl)        

    def init_node(self):
        self.optimizer : torch.optim.Optimizer | None = None
        self.tracked_modules : set[nn.Module]= set()


    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('lr','device')
        self.restore_controls('network name')

    def get_module_nodes(self)->List[ModuleNode]:
        result: List[ModuleNode] = []
        for name in self.network_names.get_one_data().split(','):
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
            mn.create_module_and_update_name(self.device.get_one_data())

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
            m.requires_grad_(False)

    def train_mode(self):
        for m in self.tracked_modules:
            m.train()
            m.requires_grad_(True)

def link_control_with_network_names(control:OptionControl):
    def on_network_names_changed():
        control.options.set(NetworkDefManager.get_network_names())
    NetworkDefManager.on_network_names_changed += on_network_names_changed
    on_network_names_changed()
    def unlink():
        NetworkDefManager.on_network_names_changed -= on_network_names_changed
    return unlink


class TrainNode(Node):
    category='torch/training'

    def build_node(self):
        self.label.set('Train')
        self.network_port = self.add_in_port('network',control_type=OptionControl, options=['net a','net b'])
        self.loss_port = self.add_in_port('loss',1)
        self.network_name = self.add_attribute('network name',StringTopic,'')

        existing_networks = NetworkDefManager.get_network_names()
        if len(existing_networks) > 0:
            self.network_name.set(existing_networks[0])
            self.network_port.default_control.value.set(existing_networks[0])

    def init_node(self):
        self.to_unlink = link_control_with_network_names(self.network_port.default_control)
        self.optimizing_modules : set[nn.Module]= set()

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.loss_port:
            self.run(self.train_step,loss = edge.get_data())
            return
        if port == self.network_port:
            network_name = self.network_port.get_one_data()
            self.network_name.set(network_name)
            self.label.set('Train '+network_name)

    def get_module_nodes(self)->List[ModuleNode]:
        name = self.network_name.get()
        if not NetworkDefManager.has_network(name):
            return []
        return NetworkDefManager.get_module_nodes(name)
    
    def getModules(self)->List[nn.Module]:
        return [mn.get_module() for mn in self.get_module_nodes()]

    def create_optimizer_if_needed(self):
        if self.optimizing_modules != set(self.getModules()):
            self.optimizing_modules = set(self.getModules())
            self.optimizer = torch.optim.Adam([p for m in self.optimizing_modules for p in m.parameters()])

    def train_step(self,loss:torch.Tensor):
        self.create_optimizer_if_needed()
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def destroy(self):
        self.to_unlink()
        return super().destroy()

class ConfigureNode(Node):
    category='torch/training'

    def build_node(self):
        self.label.set('Configure Network')
        self.network_port = self.add_in_port('network',control_type=OptionControl, options=['net a','net b'])
        self.device_port = self.add_in_port('device',control_type=OptionControl, options=['default','cpu','cuda'],value='default')
        self.reset_port = self.add_in_port('reset network',control_type=ButtonControl)
        self.mode_port = self.add_in_port('mode',control_type=OptionControl, options=['train','eval'],value='train')

        # they are attribute so they can be saved
        self.network_name = self.add_attribute('network name',StringTopic,'')
        self.device = self.add_attribute('device',StringTopic,'default')

        existing_networks = NetworkDefManager.get_network_names()
        if len(existing_networks) > 0:
            self.network_name.set(existing_networks[0])
            self.network_port.default_control.value.set(existing_networks[0])

    def init_node(self):
        self.to_unlink = link_control_with_network_names(self.network_port.default_control)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('network name','device')
        self.restore_controls('network name')

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.network_port:
            self.label.set('Configure '+self.network_port.get_one_data())
            self.network_name.set(self.network_port.get_one_data())
            mns = self.get_module_nodes()
            if len(mns) > 0:
                self.device.set(mns[0].get_device())
            self.device_port.default_control.value.set(self.device.get())
            self.run(self.set_mn_device)
        if port == self.reset_port:
            self.run(self.reset)
            port.get_one_data()
        if port == self.device_port:
            self.device.set(self.device_port.get_one_data())
            self.run(self.set_mn_device)

    def reset(self):
        for mn in self.get_module_nodes():
            mn.create_module_and_update_name(self.device.get())

    def set_mn_device(self):
        device = self.device.get()
        for mn in self.get_module_nodes():
            mn.to(device)

    def get_module_nodes(self)->List[ModuleNode]:
        name = self.network_name.get()
        if not NetworkDefManager.has_network(name):
            return []
        return NetworkDefManager.get_module_nodes(name)
    
    def destroy(self):
        self.to_unlink()
        return super().destroy()