from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import SObject

class Editor(SObject):
    frontend_type = 'Editor'
    def create_node(self, node_type: type, **kwargs) -> Node:
        return self.add_child(node_type, is_preview=False, **kwargs)
    
    def create_edge(self, tail: OutputPort, head: InputPort) -> Edge:
        return self.add_child(Edge, is_preview=False, tail=tail, head=head)