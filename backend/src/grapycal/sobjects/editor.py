from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import SObject

class Editor(SObject):
    frontend_type = 'Editor'

    def init(self):
        # called by client
        self.register_service('create_edge',self.create_edge_service)

    def create_node(self, node_type: type, **kwargs) -> Node:
        return self.add_child(node_type, is_preview=False, **kwargs)
    
    def create_edge(self, tail: OutputPort, head: InputPort) -> Edge:
        # Check the tail and head have space for the edge
        if tail.is_full() or head.is_full():
            raise Exception('A port is full')
        return self.add_child(Edge, tail=tail, head=head)
    
    def create_edge_service(self, tail_id: str, head_id: str):
        tail = self._server.get_object(tail_id)
        head = self._server.get_object(head_id)
        assert isinstance(tail, OutputPort)
        assert isinstance(head, InputPort)
        self.create_edge(tail, head)
