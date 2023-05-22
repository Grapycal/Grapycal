from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node


class AdditionNode(Node):

    def pre_build(self, attribute_values, workspace):
        super().pre_build(attribute_values, workspace)
        self._calculated_data = 0

    def build(self):
        super().build()
        self.in_port = self.add_in_port('in')
        self.out_port =  self.add_out_port('out')
        self.label.set('+')
        self.shape.set('round')

    def edge_activated(self, edge: Edge):
        if self.in_port.is_all_edge_ready():
            self.activate()

    def activate(self):
        data = [edge.get_data() for edge in self.in_port.edges]
        if len(data) == 0:
            summation = 0
        else:
            summation = data[0]
            for d in data[1:]:
                summation += d #type: ignore
        for edge in self.out_port.edges:
            edge.push_data(summation)
        self._calculated_data = summation

    def input_edge_added(self, edge: Edge, port):
        if self.in_port.is_all_edge_ready():
            self.activate()

    def input_edge_removed(self, edge: Edge, port):
        if self.in_port.is_all_edge_ready():
            self.activate()

    def output_edge_added(self, edge: Edge, port):
        edge.push_data(self._calculated_data)
        print('push data', self._calculated_data)