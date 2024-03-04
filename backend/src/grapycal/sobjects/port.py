import abc
from hmac import new
from msilib import Control
from typing import TYPE_CHECKING, Any, List, Literal
import typing
from grapycal.sobjects.controls.control import ValuedControl
from grapycal.sobjects.controls.nullControl import NullControl
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

T = typing.TypeVar('T', bound='ValuedControl')
class InputPort(Port, typing.Generic[T]):
    def build(self, control_type: type[T], name='port', max_edges=64, display_name=None,control_name=None, **control_kwargs):
        super().build(name, max_edges, display_name)
        self.is_input.set(1)
        if control_type is NullControl:
            control_name = None
        if control_name is not None:
            if control_name in self.node.controls:
                raise ValueError(f'Control with name {control_name} already exists')
        else:
            control_name = 'Control0'
            i=0
            while control_name in self.node.controls:
                i+=1
                control_name = f'Control{i}'

        new_control_id = f'{self.node.get_id()}_c_{control_name}'
        self.default_control = self.add_child(control_type, id=new_control_id, **control_kwargs)
        self.node.controls.add(control_name,self.default_control)

        # this topic affects css
        self.control_takes_label = self.add_attribute('control_takes_label', IntTopic, 0)
        if self.default_control.take_label(self.display_name.get()):
            self.control_takes_label.set(1)

    def init(self):
        super().init()
        self.on_activate = Action()
        self.use_default = len(self.edges) == 0 and not isinstance(self.default_control, NullControl)
        self.default_control.set_activation_callback(
            lambda *args,**kwargs: # so they can link the callback to Actions without worrying about redundant args
            self.activated_by_control(self.default_control))

    def add_edge(self, edge: 'Edge'):
        super().add_edge(edge)
        self.node.input_edge_added(edge, self)
        self.use_default = 0

    def remove_edge(self, edge: 'Edge'):
        super().remove_edge(edge)
        self.node.input_edge_removed(edge, self)
        self.use_default = len(self.edges) == 0 and not isinstance(self.default_control, NullControl)

    def is_all_edge_ready(self):
        return (self.use_default and self.default_control.value_ready()) or \
            (all(edge.is_data_ready() for edge in self.edges) and len(self.edges) > 0)

    def get_data(self):
        return [self.default_control.get_value()] if self.use_default else \
            [edge.get_data() for edge in self.edges]

    def get_one_data(self, allow_no_data=False) -> Any:
        if self.use_default:
            return self.default_control.get_value()
        elif allow_no_data and not self.is_all_edge_ready():
            return None
        return self.edges[0].get_data()

    def activated_by_edge(self, edge:'Edge'):
        try:
            self.default_control.set_with_value_from_edge(edge.peek_data())
        except Exception as e:
            # The control doesn't accept the value from the edge. We respect that and abandon the data.
            self.node.print_exception(e)
            edge.get_data() # to clear the data from the edge
            return
        self.activated(edge)

    def activated_by_control(self, control:'ValuedControl'):
        self.activated(control)

    def activated(self, source: 'Edge|ValuedControl'):
        self.on_activate.invoke(self, source)
        self.node.edge_activated(source, self)

    # TODO remove control from node when port is removed
        
    

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
