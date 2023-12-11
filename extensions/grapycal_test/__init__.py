import enum
import io
import json
from typing import Any, Dict, List
from grapycal import Node, Edge, InputPort, TextControl, ButtonControl, IntTopic, FunctionNode, SetTopic, StringTopic, ListTopic, DictTopic
from grapycal.core.workspace import Workspace
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.imageControl import ImageControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from objectsync.sobject import SObjectSerialized
import websockets
from websockets.sync.client import connect
from grapycal.sobjects.DVfunctionNode import DVfunctionNode

class TestNode(FunctionNode):
    category = 'test'
    default_ports = []
    def build_node(self):
        self.label.set('testing')
        self.send_port = self.add_in_port('send')
        self.recv_port = self.add_out_port('recv')
        self.subs_info = self.add_attribute('subs_info', DictTopic, {}, editor_type='dict',key_options=['aaa0','aab'],value_options=['vads,asde'],key_strict=True) # internal use only. data: {'name':str,'type':str}
        # self.subsciptions = self.add_attribute('subsciptions', ListTopic, [], editor_type='list') # for user to manipulate
        
    def init_node(self):

        # def link_subsciptions_to_subs_info():
        #     self.subsciptions.on_insert.add_auto(lambda topic_name,_: self.subs_info.add(topic_name, self.subscription_type.get()))
        #     self.subsciptions.on_pop.add_auto(lambda topic_name,_: self.subs_info.pop(topic_name))
        # self._server.do_after_transition(link_subsciptions_to_subs_info)

        self.subs_info.on_add.add_auto(self.on_subscription_add1)
        self.subs_info.on_remove.add_auto(self.on_subscription_remove1)

    def on_subscription_add1(self, topic_name, topic_value):
        # self.ports_value.update({topic_name:topic_value})
        self.default_ports.append(topic_name)
        self.add_in_port(topic_name)

    def on_subscription_remove1(self, topic_name):
        # self.ports_value.pop(topic_name)
        self.default_ports.remove(topic_name)
        self.remove_in_port(topic_name)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('subs_info')

    def calculate(self, **kwargs):
        for key, value in self.subs_info.get().items():
            if self.get_in_port(key).edges:
                continue
            kwargs.update({key:eval(value)})

        print(self.default_ports)
        print(self.subs_info.get())
        print('calculate')
        return kwargs
import requests
class DefaultTestNode(DVfunctionNode):
    category = 'test'
    default_value = [{'a':1,'b':2,'c':3}]
    default_only = False
    def build_node(self):
        super().build_node()
        self.label.set('default testing')
        self.shape.set('normal')
        self.send_port = self.add_in_port('test')
        self.recv_port = self.add_out_port('b')
        self.inputs_attribute.add('ccccc', '<requests.get>')
        self._default_value.append('ccccc')
        self.add_in_port('ccccc')

    def calculate(self, **kwargs):
        return kwargs