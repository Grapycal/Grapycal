from typing import Any, Dict
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.activeNode import SourceNode
from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import StringTopic, ListTopic

class VariableNode(SourceNode):
    '''
    
    VariableNode stores a variable in the workspace. It can be used to store data for later use.

    :inputs:
        - run: send in a signal to actively output the variable's value
        - set: set the variable's value

    :outputs:
        - get: get the variable's value

    '''
    category = 'data'
    
    def build_node(self):
        super().build_node()
        self.in_port = self.add_in_port('set',1)
        self.out_port = self.add_out_port('get')
        self.variable_name = self.add_control(TextControl,name='variable_name')
        self.label.set('Variable')
        self.shape.set('simple')

    def init_node(self):
        super().init_node()
        self.value = None
        self.has_value = False

    def recover_from_version(self, version: str, old: NodeInfo):
        super().recover_from_version(version, old)
        self.recover_controls('variable_name')

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.in_port:
            self.workspace.vars()[self.variable_name.text.get()] = edge.get_data()

    def task(self):
        self.value = self.workspace.vars()[self.variable_name.text.get()]
        self.has_value = True
        for edge in self.out_port.edges:
            edge.push_data(self.value)

class SplitNode(Node):
    '''
    SplitNode is used to get items from a list or a dictionary using keys.
    It is equivalent to `data[key]` in Python.

    Multiple keys can be used at the same time. Each value will be sent to a corresponding output port.

    :inputs:
        - list/dict: the list or dictionary to be split

    :outputs:
        - value1: the value of the first key
        - value2: the value of the second key
        etc.
    '''
    category = 'data'

    def build_node(self):
        self.in_port = self.add_in_port('list/dict',1)
        self.label.set('Split')
        self.shape.set('normal')
        self.keys = self.add_attribute('keys', ListTopic, editor_type='list')

    def init_node(self):
        self.keys.on_insert.add_auto(self.add_key)
        self.keys.on_pop.add_auto(self.remove_key)

    def add_key(self, key, position):
        self.add_out_port(key)

    def remove_key(self, key, position):
        self.remove_out_port(key)

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.task)

    def input_edge_added(self, edge: Edge, port: InputPort):
        self.run(self.task)

    def task(self):
        data = self.in_port.get_one_data()
        for out_port in self.out_ports:
            key = out_port.name.get()
            out_port.push_data(eval(f'_data[{key}]',self.workspace.vars(),{'_data':data}))

        