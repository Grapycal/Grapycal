from typing import Iterable
from grapycal.sobjects.node import Node

class ForNode(Node):
    category = 'procedural'

    def build_node(self):
        self.iterable_port = self.add_in_port('iterable',max_edges=1)
        self.run_port = self.add_in_port('run')
        self.item_port = self.add_out_port('item')
        self.label.set('For')
        self.shape.set('normal')

    def init(self):
        self.iterator:Iterable|None = None

    def edge_activated(self, edge, port):
        if port == self.run_port:
            self.start()

    def double_click(self):
        self.start()

    def start(self):
        self.iterator = iter(self.iterable_port.edges[0].get_data()) #type: ignore
        self.run(self.next,to_queue=False)

    def next(self):
        try:
            item = next(self.iterator) #type: ignore
        except StopIteration:
            return
        for edge in self.item_port.edges:
            edge.push_data(item)
        self.run(self.next,to_queue=False)
