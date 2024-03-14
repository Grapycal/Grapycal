from typing import TYPE_CHECKING, List
from grapycal.extension.utils import NodeInfo
from grapycal import Node, Edge, InputPort, ButtonControl, OptionControl

from .utils import setup_net_name_ctrl

from .moduleNode import ModuleNode

if TYPE_CHECKING:
    from grapycal_torch import GrapycalTorch


class ConfigureNode(Node):
    ext: "GrapycalTorch"
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
                
        self.on_network_name_changed('',self.network_name.get())
        self.network_name.on_set2.add_manual(self.on_network_name_changed)

        self.label.set('Configure '+self.network_name.get())
        self.network_name.on_set += lambda value: self.label.set('Configure '+value)

        self.to_unlink = setup_net_name_ctrl(self.network_port.default_control,self.ext, set_value=self.is_new)
        
    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('network','device','mode')

    def on_network_name_changed(self,old,new):
        if old != '':
            self.ext.conf.remove(old,self)
        if new != '':
            self.ext.conf.add(new,self)

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.reset_port:
            self.run(self.reset)
            port.get_one_data()

    def reset(self):
        for mn in self.get_module_nodes():
            mn.create_module_and_update_name()

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
        if not self.ext.net.has_network(name):
            return []
        return self.ext.net.get_module_nodes(name)
    
    def destroy(self):
        self.to_unlink()
        if self.network_name.get() != '':
            self.ext.conf.remove(self.network_name.get(),self)
        return super().destroy()