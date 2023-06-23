from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort


class PrintNode(Node):
    frontend_type = 'TextOutputNode'
    category = 'interaction'
    def build(self):
        super().build()
        self.add_in_port('in',max_edges=1)
        self.label.set('')

        if self.is_preview.get():
            self.label.set('Hello world')


    def edge_activated(self, edge):
        data = edge.get_data()
        self.label.set(str(data))

    def input_edge_added(self, edge: Edge, port: InputPort):
        if edge.is_data_ready():
            data = edge.get_data()
            self.label.set(str(data))

    def input_edge_removed(self, edge: Edge, port: InputPort):
        self.label.set('')