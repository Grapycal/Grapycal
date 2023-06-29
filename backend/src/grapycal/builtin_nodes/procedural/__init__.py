from typing import Iterable
from grapycal.sobjects.node import Node


class ForNode(Node):
    category = 'procedural'
    def pre_build(self, attribute_values, workspace, is_preview:bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self.label.set('For')
        self.shape.set('normal')
        self.iterator:Iterable|None = None

    def build(self):
        super().build()
        self.iterable_port = self.add_in_port('iterable',max_edges=1)
        self.run_port = self.add_in_port('run')
        self.item_port = self.add_out_port('item')

    def edge_activated(self, edge, port):
        if port == self.run_port:
            self.iterator = iter(self.iterable_port.edges[0].get_data()) #type: ignore
            self.run_in_background(self.next,to_queue=False)

    def next(self):
        try:
            item = next(self.iterator) #type: ignore
        except StopIteration:
            return
        for edge in self.item_port.edges:
            edge.push_data(item)
        self.run_in_background(self.next,to_queue=False)