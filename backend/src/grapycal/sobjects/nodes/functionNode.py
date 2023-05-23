from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node


class FunctionNode(Node):

    def pre_build(self, attribute_values, workspace):
        super().pre_build(attribute_values, workspace)
        self._calculated_data = 0

    def build(self):
        super().build()
        self.in_port = self.add_in_port('in')
        self.out_port =  self.add_out_port('out')
        self.label.set('f')
        self.shape.set('round')

    def edge_activated(self, edge: Edge):
        if self.in_port.is_all_edge_ready():
            self.activate()

    def activate(self):
        result = self.calculate([edge.get_data() for edge in self.in_port.edges])
        self._calculated_data = result

    def calculate(self, data):
        '''
        Override this method to change the function of the node.
        '''
        return data

    def input_edge_added(self, edge: Edge, port):
        if self.in_port.is_all_edge_ready():
            self.activate()

    def input_edge_removed(self, edge: Edge, port):
        if self.in_port.is_all_edge_ready():
            self.activate()

    def output_edge_added(self, edge: Edge, port):
        edge.push_data(self._calculated_data)