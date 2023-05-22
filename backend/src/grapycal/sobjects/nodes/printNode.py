from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort


class PrintNode(Node):
    frontend_type = 'TextOutputNode'
    def build(self):
        super().build()
        self.add_in_port('in')
        self.label.set('')

    def edge_activated(self, edge):
        data = edge.get_data()
        self.label.set(str(data))

    def input_edge_added(self, edge: Edge, port: InputPort):
        data = edge.get_data()
        self.label.set(str(data))

    def input_edge_removed(self, edge: Edge, port: InputPort):
        print('input_edge_removed')
        self.label.set('')