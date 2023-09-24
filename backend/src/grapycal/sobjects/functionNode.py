from typing import Any
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
class FunctionNode(Node):
    inputs = []
    input_edge_limit = []
    outputs = []
    display_port_names = True

    def build_node(self):
        self._input_edge_limit = self.input_edge_limit[:]
        while len(self._input_edge_limit) < len(self.inputs):
            self._input_edge_limit.append(1)
        for i in range(len(self._input_edge_limit)):
            if self._input_edge_limit[i] is None:
                self._input_edge_limit[i] = 64
        for name, max_edges in zip(self.inputs,self._input_edge_limit): #type: ignore
            display_name = name if self.display_port_names else ''
            self.add_in_port(name,max_edges,display_name=display_name)
        for name in self.outputs:
            display_name = name if self.display_port_names else ''
            self.add_out_port(name,display_name=display_name)

        self.label.set('f')
        self.shape.set('round')

    def edge_activated(self, edge: Edge, port):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
        self.run(self.task)

    def task(self):
        if self.destroyed:
            return
        inputs = []
        for port in self.in_ports:
            inputs.append([edge.get_data() for edge in port.edges])

        result = self.calculate(inputs)

        if result is None:
            return

        if len(self.out_ports) == 1:
            self.out_ports[0].push_data(result)
        else:
            for port, data in zip(self.out_ports, result):
                port.push_data(data)


    def calculate(self, inputs: list[Any]):
        '''
        Define the function of this node here.

        :param inputs: A list of lists. Each list contains the data from one input port. For example, if there is only one input port with two\
            edges connected, the value of inputs will be `[[data_from_edge_1, data_from_edge_2]]`.
        :return: A list of outputs. Each entry in the list will be pushed to one output port. For example, if there is only one output port,\
            the value of the return suold be `[data_to_port]`. If there are multiple edges connected to one output port,\
            they will all receive the same data.

        Examples::

            class SumNode(FunctionNode):
                inputs = ['items']
                outputs = ['sum']
                ...
                def calculate(self, inputs):
                    inp = inputs[0] # Retrieve the data from the input port
                    return [sum(inp)] # Return the sum of the data
        '''
        raise NotImplementedError

    def input_edge_added(self, edge: Edge, port):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
        self.run(self.task)

    def input_edge_removed(self, edge: Edge, port):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
        self.run(self.task)

    def remove(self):
        return super().remove()