from collections import defaultdict
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from objectsync.sobject import SObjectSerialized
from .forNode import ForNode
from .eventNode import EventNode
from .procedureNode import ProcedureNode
from .limiterNode import LimiterNode
from .funcDef import *

class PortalManager:
    ins = ListDict['InPortalNode']()
    outs = ListDict['OutPortalNode']()

class InPortalNode(Node):
    category = 'procedural'
    def build_node(self):
        self.shape.set('simple')
        self.label.set('🔵')
        self.name = self.add_attribute('name',StringTopic,editor_type='text')
        self.in_port = self.add_in_port('jump')
        self.out_port = self.add_out_port('then')
        self.css_classes.append('fit-content')
    
    def init_node(self):
        PortalManager.ins.append(self.name.get(),self)
        self.name.on_set2.add_manual(self.on_name_set)

    def on_name_set(self, old, new):
        self.label.set(f'🔵{new}')
        PortalManager.ins.remove(old,self)
        PortalManager.ins.append(new,self)
    
    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.after_jump,to_queue=False)
        for node in PortalManager.outs.get(self.name.get()):
            node.jump()

    def after_jump(self):
        self.out_port.push_data(None)

    def destroy(self) -> SObjectSerialized:
        PortalManager.ins.remove(self.name.get(),self)
        return super().destroy()

class OutPortalNode(Node):
    category = 'procedural'
    def build_node(self):
        self.shape.set('simple')
        self.label.set('🟠')
        self.name = self.add_attribute('name',StringTopic,editor_type='text')
        self.out_port = self.add_out_port('do')
        self.css_classes.append('fit-content')
    
    def init_node(self):
        PortalManager.outs.append(self.name.get(),self)
        self.name.on_set2.add_manual(self.on_name_set)

    def on_name_set(self, old, new):
        self.label.set(f'🟠{new}')
        PortalManager.outs.remove(old,self)
        PortalManager.outs.append(new,self)

    def jump(self):
        self.out_port.push_data(None)
    
    def destroy(self) -> SObjectSerialized:
        PortalManager.outs.remove(self.name.get(),self)
        return super().destroy()