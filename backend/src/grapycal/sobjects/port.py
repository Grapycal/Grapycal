import abc
from msilib import Control
from typing import TYPE_CHECKING, Any, List
import typing
from grapycal.sobjects.controls.control import ValuedControl
from objectsync import SObject, StringTopic, IntTopic

from grapycal.utils.misc import Action

if TYPE_CHECKING:
    from grapycal.sobjects.node import Node
    from grapycal.sobjects.edge import Edge


class Port(SObject):
    frontend_type = 'Port'

    def build(self, name='port', max_edges=64, display_name=None):
        self.node: Node = self.get_parent() # type: ignore
        self.name = self.add_attribute('name', StringTopic, name)
        self.display_name = self.add_attribute('display_name', StringTopic, name if display_name is None else display_name)
        self.max_edges = self.add_attribute('max_edges', IntTopic, max_edges)
        self.is_input = self.add_attribute('is_input', IntTopic, 0)

    def init(self):
        self.edges: List[Edge] = []
        self.node: Node = self.get_parent() # type: ignore
    
    def add_edge(self, edge:'Edge'):
        if len(self.edges) >= self.max_edges.get():
            raise Exception('Max edges reached')
        self.edges.append(edge)
    
    def remove_edge(self, edge:'Edge'):
        if edge not in self.edges:
            return
        self.edges.remove(edge)

    def is_full(self):
        return len(self.edges) >= self.max_edges.get()

    def get_name(self):
        return self.name.get()


class InputPort(Port):
    def build(self, control_type: type[ValuedControl], name='port', max_edges=64, display_name=None,control_name=None, **control_kwargs):
        super().build(name, max_edges, display_name)
        self.is_input.set(1)
        if control_name is not None:
            if control_name in self.node.controls:
                raise ValueError(f'Control with name {control_name} already exists')
        else:
            control_name = 'Control0'
            i=0
            while control_name in self.node.controls:
                i+=1
                control_name = f'Control{i}'

        self.default_control = self.add_child(control_type, **control_kwargs)
        self.node.controls.add(control_name,self.default_control)

        # this topic affects css
        self.control_takes_label = self.add_attribute('control_takes_label', IntTopic, 0)
        if self.default_control.take_label(self.display_name.get()):
            self.control_takes_label.set(1)

    def init(self):
        super().init()
        self.on_activate = Action()
        self.use_default = len(self.edges) == 0
        self.default_control.set_activation_callback(
            lambda *args,**kwargs: # so they can link the callback to Actions without caring about redundant args
            self.edge_activated(self.default_control))

    def add_edge(self, edge: 'Edge'):
        super().add_edge(edge)
        self.node.input_edge_added(edge, self)
        self.use_default = 0

    def remove_edge(self, edge: 'Edge'):
        super().remove_edge(edge)
        self.node.input_edge_removed(edge, self)
        self.use_default = len(self.edges) == 0

    def is_all_edge_ready(self):
        return (self.use_default and self.default_control.value_ready()) or \
            all(edge.is_data_ready() for edge in self.edges)

    def get_data(self):
        return [self.default_control.get_value()] if self.use_default else \
            [edge.get_data() for edge in self.edges]

    def get_one_data(self, allow_no_data=False) -> Any:
        if self.use_default:
            return self.default_control.get_value()
        elif allow_no_data and not self.is_all_edge_ready():
            return None
        return self.edges[0].get_data()

    def edge_activated(self, edge:'Edge|ValuedControl'):
        self.on_activate.invoke(self, edge)
        self.node.edge_activated(edge, self)
    

class OutputPort(Port):
    def build(self, name='port', max_edges=64, display_name=None):
        super().build(name, max_edges, display_name)
        self.is_input.set(0)

    def init(self):
        super().init()
        self._retain = False
        self._retained_data = None

    def add_edge(self, edge:'Edge'):
        super().add_edge(edge)
        if self._retain:
            edge.push_data(self._retained_data)
        self.node.output_edge_added(edge, self)

    def remove_edge(self, edge:'Edge'):
        super().remove_edge(edge)
        self.node.output_edge_removed(edge, self)

    def push_data(self, data:Any=None,label:str|None=None, retain: bool = False):
        '''
        Push data to all connected edges.
        If retain is True, the data will be pushed to all future edges when they're connected as well.
        '''
        if retain:
            self._retain = True
            self._retained_data = data
        for edge in self.edges:
            edge.push_data(data,label=label)

    def disable_retain(self):
        '''
        Disable retain mode.
        '''
        self._retain = False
        self._retained_data = None # Release memory
