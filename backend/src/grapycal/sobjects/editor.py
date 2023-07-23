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
        return self.add_child(Edge, tail=tail, head=head)
    
    def create_edge_service(self, tail_id: str, head_id: str):
        # We should not use add_child here because it does not record the creation as a transition
        self._server.create_object(Edge,self._id,tail = self._server.get_object(tail_id), head = self._server.get_object(head_id)) # type: ignore