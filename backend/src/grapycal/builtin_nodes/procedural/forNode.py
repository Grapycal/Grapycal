from typing import Iterable
from grapycal.sobjects.activeNode import SourceNode
from grapycal.sobjects.node import Node

class ForNode(SourceNode):
    category = 'procedural'

    def build_node(self):
        super().build_node()
        self.item_port = self.add_out_port('item')
        self.label.set('For')
        self.shape.set('normal')

    def init_node(self):
        super().init_node()
        self.iterator:Iterable|None = None

    def task(self):
        self.iterator = iter(self.run_port.get_one_data()) #type: ignore
        self.run(self.next,to_queue=False)

    def next(self):
        try:
            item = next(self.iterator) #type: ignore
        except StopIteration:
            return
        for edge in self.item_port.edges:
            edge.push_data(item)
        self.run(self.next,to_queue=False)
