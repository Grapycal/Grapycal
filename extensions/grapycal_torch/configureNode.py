from typing import List
from grapycal.extension.utils import NodeInfo
from grapycal import Node, Edge, InputPort, ButtonControl, OptionControl

from .utils import link_control_with_network_names

from .moduleNode import ModuleNode
from .manager import Manager as M


class ConfigureNode(Node):
    category='torch/training'

    def build_node(self):
        self.label.set('Configure Network')
        self.network_port = self.add_in_port('network',control_type=OptionControl, options=['net a','net b'])
        self.device_port = self.add_in_port('device',control_type=OptionControl, options=['default','cpu','cuda'],value='default')
        self.mode_port = self.add_in_port('mode',control_type=OptionControl, options=['train','eval'],value='train')
        self.reset_port = self.add_in_port('reset network',control_type=ButtonControl)

    def init_node(self):
        self.network_name = self.network_port.default_control.value
        self.device = self.device_port.default_control.value
        self.mode = self.mode_port.default_control.value

        if self.is_new:
            existing_networks = M.net.get_network_names()
            if len(existing_networks) > 0:
                self.network_name.set(existing_networks[0])
                
        self.on_network_name_changed('',self.network_name.get())
        self.network_name.on_set2.add_manual(self.on_network_name_changed)
        self.network_name.on_set += lambda value: self.label.set('Configure '+value)

        self.to_unlink = link_control_with_network_names(self.network_port.default_control)
        
    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('network','device','mode')

    def on_network_name_changed(self,old,new):
        if old != '':
            M.conf.remove(old,self)
        if new != '':
            M.conf.add(new,self)

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.reset_port:
            self.run(self.reset)
            port.get_one_data()

    def reset(self):
        for mn in self.get_module_nodes():
            mn.create_module_and_update_name(self.device.get())

    def set_mn_device(self):
        device = self.device.get()
        for mn in self.get_module_nodes():
            mn.to(device)

    def set_mn_mode(self,mode):
        assert mode in ['train','eval']
        for mn in self.get_module_nodes():
            mn.mode.set(mode)

    def get_module_nodes(self)->List[ModuleNode]:
        name = self.network_name.get()
        if not M.net.has_network(name):
            return []
        return M.net.get_module_nodes(name)
    
    def destroy(self):
        self.to_unlink()
        if self.network_name.get() != '':
            M.conf.remove(self.network_name.get(),self)
        return super().destroy()