from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort


class PrintNode(Node):
    category = 'interaction'
    def pre_build(self, attribute_values, workspace, is_preview:bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self.label.set('print')
        self.shape.set('simple')

    def build(self):
        super().build()
        self.add_in_port('',max_edges=1)
        self.text_control = self.add_control(TextControl, editable=False)

    def edge_activated(self, edge, port):
        data = edge.get_data()
        self.text_control.text.set(str(data))

    def input_edge_added(self, edge: Edge, port: InputPort):
        if edge.is_data_ready():
            data = edge.get_data()
            self.text_control.text.set(str(data))

    def input_edge_removed(self, edge: Edge, port: InputPort):
        self.text_control.text.set('')