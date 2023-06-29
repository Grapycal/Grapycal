from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort


class ForNode(Node):
    category = 'procedural'
    def pre_build(self, attribute_values, workspace, is_preview:bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self.label.set('for')
        self.shape.set('normal')
        self.iterable = None

    def build(self):
        super().build()
        self.iterable_port = self.add_in_port('iterable',max_edges=1)
        self.run_port = self.add_in_port('run')
        self.item_port = self.add_out_port('item')

    def edge_activated(self, edge, port):
        if port == self.run_port:
            self.iterable = self.iterable_port.edges[0].get_data()
            #self.item
