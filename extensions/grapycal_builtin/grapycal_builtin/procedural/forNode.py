from typing import Iterable
from grapycal import Node
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from grapycal.sobjects.sourceNode import SourceNode
from objectsync import IntTopic

class ForNode(Node):
    '''
    Iterate through an iterable object. Each iteration will push the next item to the ``item`` port.
    Double click to interrupt the iteration.
    '''
    category = 'procedural'

    def build_node(self):
        super().build_node()
        self.iterable_port = self.add_in_port('iterable')
        self.item_port = self.add_out_port('item')
        self.label.set('For')
        self.shape.set('simple')

    def init_node(self):
        super().init_node()
        self.iterator:Iterable|None = None

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.task)

    def task(self):
        self.iterator = iter(self.iterable_port.get_one_data()) #type: ignore
        self.run(self.next,to_queue=False)

    def next(self):
        if self.iterator is None:
            return
        try:
            item = next(self.iterator) #type: ignore
        except StopIteration:
            return
        self.run(self.next,to_queue=False)
        for edge in self.item_port.edges:
            edge.push_data(item)

    def double_click(self):
        self.iterator = None
        self.print('Iteration interrupted')

class RepeatNode(SourceNode):
    '''
    Shortcut for ``For`` node with ``range`` as iterable.
    '''
    category = 'procedural'

    def build_node(self):
        super().build_node()
        self.item_port = self.add_out_port('item')
        self.label.set('Repeat 10 times')
        self.shape.set('simple')
        self.times = self.add_attribute('times',IntTopic,editor_type='int',init_value=10)

    def init_node(self):
        super().init_node()
        self.iterator:Iterable|None = None
        self.times.on_set += lambda times: self.label.set(f'Repeat {times} times')

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.task)

    def task(self):
        self.iterator = iter(range(self.times.get()))
        self.run(self.next,to_queue=False)

    def next(self):
        if self.iterator is None:
            return
        try:
            item = next(self.iterator) #type: ignore
        except StopIteration:
            self.iterator = None
            return
        self.run(self.next,to_queue=False)
        for edge in self.item_port.edges:
            edge.push_data(item)

    def double_click(self):
        if self.iterator is None:
            super().double_click()
        else:
            self.iterator = None
            self.print('Iteration interrupted')
