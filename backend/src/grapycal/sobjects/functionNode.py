from typing import Any, List
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.sobjects.simpleNode import SimpleNode

class FunctionNode(SimpleNode):
    inputs = []
    input_edge_limit = []
    outputs = []

    def pre_build(self, attribute_values, workspace, is_preview:bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self._calculated_data = 0

        self._input_edge_limit = self.input_edge_limit[:]
        while len(self._input_edge_limit) < len(self.inputs):
            self._input_edge_limit.append(1)
        for i in range(len(self._input_edge_limit)):
            if self._input_edge_limit[i] is None:
                self._input_edge_limit[i] = 64

    def build(self):
        super().build()
        for name, max_edges in zip(self.inputs,self._input_edge_limit): #type: ignore
            self.add_in_port(name,max_edges)
        for name in self.outputs:
            self.add_out_port(name)

        self.label.set('f')
        self.shape.set('round')

    def edge_activated(self, edge: Edge, port):
        for port in self.in_ports:
            assert isinstance(port, InputPort)
            if not port.is_all_edge_ready():
                return
        self.activate()

    def run(self):
        inputs = []
        for port in self.in_ports:
            assert isinstance(port, InputPort)
            if port.max_edges.get() == 1:
                inputs.append(port.edges[0].get_data())
            else:
                inputs.append([edge.get_data() for edge in port.edges])

        result = self.calculate(inputs)
        self._calculated_data = result

        if len(self.out_ports) == 1:
            for edge in self.out_ports[0].edges:
                edge.push_data(result)
        else:
            for port, data in zip(self.out_ports, result):
                for edge in port.edges:
                    edge.push_data(data)


    def calculate(self, data: list[Any]):
        '''
        Override this method to change the function of the node.
        '''
        return data

    def input_edge_added(self, edge: Edge, port):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
        self.activate()

    def input_edge_removed(self, edge: Edge, port):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
        self.activate()

    def output_edge_added(self, edge: Edge, port):
        edge.push_data(self._calculated_data)