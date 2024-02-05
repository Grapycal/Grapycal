from abc import ABCMeta, abstractmethod
from typing import Any
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort
from objectsync import StringTopic
from torch import nn
from grapycal import EventTopic

from .settings import SettingsNode
from .manager import Manager as M

class ModuleMover:
    '''
    Moves a module to a device, but asynchronusly
    '''
    def __init__(self):
        self._actual_device = 'default'
        self._target_device = 'default'

    def set_target_device(self,device):
        self._target_device = device

    def set_actual_device(self,device):
        self._actual_device = device

    def get_target_device(self,translate=False):
        if translate:
            return self.translate(self._target_device)
        return self._target_device
    
    def translate(self,device:str):
        if device == 'default':
            return SettingsNode.instance.default_device.get()
        return device

    def move_if_needed(self,module:nn.Module):
        real_target = self.translate(self._target_device)
        if real_target != self._actual_device:
            module.to(real_target)
            self._actual_device = real_target
            return True
        return False

class ModuleNode(Node):
    category = 'torch/neural network'
    def build_node(self):
        #TODO: save and load
        self.shape.set('simple')
        self.label.set('Module')
        self.create_module_topic = self.add_attribute('create_module',EventTopic,editor_type='button',is_stateful=False)
        self.icon_path.set('nn')
        self.mode = self.add_attribute('mode',StringTopic,'train')
        
        # the node's id changes when it's loaded from a file, so it needs another id to identify the state dict
        self.state_dict_id = self.add_attribute('state_dict_id',StringTopic,self.get_id())

    def init_node(self):
        self.module: nn.Module|None = None
        self.create_module_topic.on_emit.add_manual(lambda:self.run(self.create_module_and_update_name))
        self.module_mover = ModuleMover()
        self.mode.on_set.add_manual(self.on_mode_changed)
        M.mn.add(self)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        # TODO: avoid duplicate state_dict_id
        self.restore_attributes('state_dict_id')
        self.restore_attributes('mode')

    def create_module_and_update_name(self):
        self.module = self.create_module()
        self.module_mover.set_actual_device('cpu')
        self.on_mode_changed(self.mode.get())
        self.label.set(self.generate_label())
        num_params = sum(p.numel() for p in self.module.parameters() if p.requires_grad)
        if num_params >= 1000000:
            param_str = f'{num_params/1000000:.1f}M'
        elif num_params >= 1000:
            param_str = f'{num_params/1000:.1f}K'
        else:
            param_str = f'{num_params}'
        self.print('created module',self.module,'\nparameters:',param_str)

    def to(self,device):
        self.module_mover.set_target_device(device)

    def set_mode(self,mode):
        self.mode.set(mode)
        
    @abstractmethod
    def create_module(self)->nn.Module:
        pass

    def generate_label(self):
        '''
        Return a string to be displayed on the node
        The default is str(self.module), which is often too long. Override this method to provide a better label
        '''
        return str(self.module)

    @abstractmethod
    def forward(self):
        '''
        Consume the input from the input ports, run a forward pass, and output the result to the output ports
        '''
        pass

    def edge_activated(self, edge: Edge, port: InputPort):
        for port_ in self.in_ports:
            if not port_.is_all_edge_ready():
                return
        self.run(self.task)

    def task(self):
        if self.module is None:
            self.create_module_and_update_name()
        if self.module_mover.move_if_needed(self.module): #type: ignore
            self.print('moved to',self.module_mover.get_target_device(True))
        self.forward()

    def get_module(self)->nn.Module:
        assert self.module is not None
        return self.module 
    
    def get_device(self)->str:
        return self.module_mover.get_target_device()
    
    def on_mode_changed(self,mode):
        if self.module is None:
            return
        if mode == 'train':
            self.module.train()
            self.module.requires_grad_(True)
        elif mode == 'eval':
            self.module.eval()
            self.module.requires_grad_(False)

    def get_state_dict(self):
        if self.module is None:
            self.create_module_and_update_name()
        return self.module.state_dict()

    def load_state_dict(self,state_dict):
        if self.module is None:
            self.create_module_and_update_name()
        self.module.load_state_dict(state_dict)

    def destroy(self):
        M.mn.remove(self)
        return super().destroy()

class SimpleModuleNode(ModuleNode):
    inputs = []
    max_in_degree = []
    outputs = []
    display_port_names = True

    def build_node(self):
        super().build_node()
        self._max_in_degree = self.max_in_degree[:]
        while len(self._max_in_degree) < len(self.inputs):
            self._max_in_degree.append(1)
        for i in range(len(self._max_in_degree)):
            if self._max_in_degree[i] is None:
                self._max_in_degree[i] = 64
        for name, max_edges in zip(self.inputs,self._max_in_degree): #type: ignore
            display_name = name if self.display_port_names else ''
            self.add_in_port(name,max_edges,display_name=display_name)
        for name in self.outputs:
            display_name = name if self.display_port_names else ''
            self.add_out_port(name,display_name=display_name)

    def task(self):
        if self.module is None:
            self.create_module_and_update_name()
        if self.module_mover.move_if_needed(self.module): #type: ignore
            self.print('moved to',self.module_mover.get_target_device(True))

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

    