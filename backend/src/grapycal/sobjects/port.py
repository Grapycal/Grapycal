from typing import TYPE_CHECKING, Any, List
from objectsync import SObject, StringTopic, IntTopic

if TYPE_CHECKING:
    from grapycal.sobjects.node import Node
    from grapycal.sobjects.edge import Edge

class Port(SObject):
    frontend_type = 'Port'
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        self.name = self.add_attribute('name', StringTopic, 'port name')
    
        self.edges: List[Edge] = []
        self.node: Node
    
    def add_edge(self, edge):
        self.edges.append(edge)
    
    def remove_edge(self, edge):
        self.edges.remove(edge)


class InputPort(Port):
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        super().pre_build(attribute_values, workspace)
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
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        super().pre_build(attribute_values, workspace)
        self.add_attribute('is_input', IntTopic, 0)

    def add_edge(self, edge):
        super().add_edge(edge)
        self.node.output_edge_added(edge, self)

    def remove_edge(self, edge):
        super().remove_edge(edge)
        self.node.output_edge_removed(edge, self)


