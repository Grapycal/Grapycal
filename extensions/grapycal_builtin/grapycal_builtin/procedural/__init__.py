from collections import defaultdict
from typing import Any
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.textControl import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.functionNode import FunctionNode
from grapycal.sobjects.port import InputPort
from objectsync.sobject import SObjectSerialized
from .forNode import *
from .procedureNode import ProcedureNode
from .limiterNode import LimiterNode
from .funcDef import *
import time

class PortalManager:
    ins = ListDict['InPortalNode']()
    outs = ListDict['OutPortalNode']()

class InPortalNode(Node):
    category = 'procedural'
    def build_node(self):
        self.shape.set('simple')
        if self.is_preview.get():
            self.label.set('In Portal')
        self.name = self.add_attribute('name',StringTopic,editor_type='text')
        self.in_port = self.add_in_port('jump',display_name='')
        self.out_port = self.add_out_port('then',display_name='')
        self.css_classes.append('fit-content')
        self.label.set(f'{self.name.get()}')
    
    def init_node(self):
        PortalManager.ins.append(self.name.get(),self)
        self.name.on_set2.add_manual(self.on_name_set)

    def on_name_set(self, old, new):
        self.label.set(f'{new}')
        PortalManager.ins.remove(old,self)
        PortalManager.ins.append(new,self)
    
    def edge_activated(self, edge: Edge, port: InputPort):
        data = edge.get()
        self.run(self.after_jump,to_queue=False,data=data)
        for node in PortalManager.outs.get(self.name.get()):
            node.jump(data)

    def double_click(self):
        data = None
        self.run(self.after_jump,to_queue=False, data=data)
        for node in PortalManager.outs.get(self.name.get()):
            node.jump(data)

    def after_jump(self,data):
        self.out_port.push(data)

    def destroy(self) -> SObjectSerialized:
        PortalManager.ins.remove(self.name.get(),self)
        return super().destroy()
    
class OutPortalNode(Node):
    category = 'procedural'
    def build_node(self):
        self.shape.set('simple')
        if self.is_preview.get():
            self.label.set('Out Portal')
        self.name = self.add_attribute('name',StringTopic,editor_type='text')
        self.out_port = self.add_out_port('do',display_name='')
        self.css_classes.append('fit-content')
    
    def init_node(self):
        PortalManager.outs.append(self.name.get(),self)
        self.label.set(f'{self.name.get()}')
        self.name.on_set2.add_manual(self.on_name_set)
        
    def on_name_set(self, old, new):
        self.label.set(f'{new}')
        PortalManager.outs.remove(old,self)
        PortalManager.outs.append(new,self)

    def double_click(self):
        for node in PortalManager.outs.get(self.name.get()):
            node.jump(None)

    def jump(self,data):
        self.run(self.out_port.push,data=data)
    
    def destroy(self) -> SObjectSerialized:
        PortalManager.outs.remove(self.name.get(),self)
        return super().destroy()
    
class SleepNode(FunctionNode):
    category = 'procedural'
    inputs = ['start']
    outputs = ['done']

    def build_node(self):
        super().build_node()
        time_port = self.add_in_port('seconds',control_type=TextControl,display_name='time',text='1')
        self.shape.set('normal')
        self.label.set('Sleep')
        self.time_control = time_port.default_control

    def calculate(self, **inputs) -> Any:
        time.sleep(float(self.time_control.get_value()))
        return inputs['start']