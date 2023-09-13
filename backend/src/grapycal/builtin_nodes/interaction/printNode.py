from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort


class PrintNode(Node):
    '''
    Display the data received from the input edge.

    :inputs:
        - data: data to be displayed

    '''
    category = 'interaction'

    def build_node(self):
        self.add_in_port('',max_edges=1)
        self.text_control = self.add_control(TextControl, editable=False)
        self.label.set('Print')
        self.shape.set('simple')

    def edge_activated(self, edge, port):
        data = edge.get_data()
        self.text_control.text.set(str(data))

    def input_edge_added(self, edge: Edge, port: InputPort):
        if edge.is_data_ready():
            data = edge.get_data()
            self.text_control.text.set(str(data))

    def input_edge_removed(self, edge: Edge, port: InputPort):
        self.text_control.text.set('')