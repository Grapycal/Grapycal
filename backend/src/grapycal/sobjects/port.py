from typing import TYPE_CHECKING, Any, List
from objectsync import SObject, StringTopic, IntTopic

if TYPE_CHECKING:
    from grapycal.sobjects.node import Node
    from grapycal.sobjects.edge import Edge

class Port(SObject):
    frontend_type = 'Port'
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace, name='port', max_edges=64):
        self.name = self.add_attribute('name', StringTopic, 'port name')
        self.max_edges = self.add_attribute('max_edges', IntTopic, max_edges)
    
        self.edges: List[Edge] = []
        self.node: Node
    
    def add_edge(self, edge):
        if len(self.edges) >= self.max_edges.get():
            raise Exception('Max edges reached')
        self.edges.append(edge)
    
    def remove_edge(self, edge):
        if edge not in self.edges:
            return
        self.edges.remove(edge)


class InputPort(Port):
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace, name='in', max_edges=64):
        super().pre_build(attribute_values, workspace, name, max_edges)
        self.add_attribute('is_input', IntTopic, 1)

    def add_edge(self, edge):
        super().add_edge(edge)
        self.node.input_edge_added(edge, self)

    def remove_edge(self, edge):
        super().remove_edge(edge)
        self.node.input_edge_removed(edge, self)
        
    def is_all_edge_ready(self):
        return all(edge.is_data_ready() for edge in self.edges)

class OutputPort(Port):
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace, name='out', max_edges=64):
        super().pre_build(attribute_values, workspace, name, max_edges)
        self.add_attribute('is_input', IntTopic, 0)

    def add_edge(self, edge):
        super().add_edge(edge)
        self.node.output_edge_added(edge, self)

    def remove_edge(self, edge):
        super().remove_edge(edge)
        self.node.output_edge_removed(edge, self)


