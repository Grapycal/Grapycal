from typing import TYPE_CHECKING, Any, List
from grapycal.utils.misc import as_type
from objectsync import SObject, StringTopic, IntTopic

if TYPE_CHECKING:
    from grapycal.sobjects.node import Node
    from grapycal.sobjects.edge import Edge

class Port(SObject):
    frontend_type = 'Port'

    def build(self, name='port', max_edges=64, display_name=None):
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


class InputPort(Port):
    def build(self, name='port', max_edges=64, display_name=None):
        super().build(name, max_edges, display_name)
        self.is_input.set(1)

    def add_edge(self, edge:'Edge'):
        super().add_edge(edge)
        self.node.input_edge_added(edge, self)

    def remove_edge(self, edge:'Edge'):
        super().remove_edge(edge)
        self.node.input_edge_removed(edge, self)
        
    def is_all_edge_ready(self):
        return all(edge.is_data_ready() for edge in self.edges)
    
    def get_data(self):
        return [edge.get_data() for edge in self.edges]
    
    def get_one_data(self):
        return self.edges[0].get_data()

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

    def push_data(self, data:Any=None, retain: bool = False):
        '''
        Push data to all connected edges.
        If retain is True, the data will be pushed to all future edges when they're connected as well.
        '''
        if retain:
            self._retain = True
            self._retained_data = data
        for edge in self.edges:
            edge.push_data(data)

    def disable_retain(self):
        '''
        Disable retain mode.
        '''
        self._retain = False
        self._retained_data = None # Release memory
