from typing import Any
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
class FunctionNode(Node):
    inputs = []
    max_in_degree = []
    outputs = []
    display_port_names = True

    def build_node(self):
        self._max_in_degree = self.max_in_degree[:]
        while len(self._max_in_degree) < len(self.inputs):
            self._max_in_degree.append(None)
        for i in range(len(self._max_in_degree)):
            if self._max_in_degree[i] is None:
                self._max_in_degree[i] = 1024
        for name, max_edges in zip(self.inputs,self._max_in_degree): #type: ignore
            display_name = name if self.display_port_names else ''
            self.add_in_port(name,max_edges,display_name=display_name)
        for name in self.outputs:
            display_name = name if self.display_port_names else ''
            self.add_out_port(name,display_name=display_name)

        self.label.set('f')
        self.shape.set('round')

    def edge_activated(self, edge: Edge, port):
        for port in self._get_func_ins():
            if not port.is_all_edge_ready():
                return
        self.run(self.task)

    def task(self):
        if self.is_destroyed():
            return
        inputs = {}
        for port in self._get_func_ins():
            if port.max_edges.get() == 1:
                inputs[port.get_name()] = port.edges[0].get_data()
            else:
                inputs[port.get_name()] = [edge.get_data() for edge in port.edges]
        result = self.calculate(**inputs)

        if len(self._get_func_outs()) == 1:
            self._get_func_outs()[0].push_data(result)
        else:
            if result is None:
                return
            for k,v in result.items():
                self.get_out_port(k).push_data(v)

    def calculate(self, **inputs)->Any:
        '''
        Define the function of this node here.

        :param **inputs: A dict of lists. Each dict entry is the data from one input port. For example, if there is only one input port named "in" with two\
            edges connected, the value of inputs will be `{'in':[data_from_edge_1, data_from_edge_2]}`.
        :return: A list of outputs. Each entry in the list will be pushed to one output port. For example, if there is only one output port,\
            the value of the return suold be `[data_to_port]`. If there are multiple edges connected to one output port,\
            they will all receive the same data.

        Examples::

            class SumNode(FunctionNode):
                inputs = ['items']
                outputs = ['sum']
                ...
                def calculate(self, items):
                    return {'sum':sum(items)} # Return the sum of the data
        '''
        raise NotImplementedError

    def input_edge_added(self, edge: Edge, port):
        for port in self._get_func_ins():
            if not port.is_all_edge_ready():
                return
        self.run(self.task)

    def input_edge_removed(self, edge: Edge, port):
        for port in self._get_func_ins():
            if not port.is_all_edge_ready():
                return
        self.run(self.task)

    def remove(self):
        return super().remove()
    
    def _get_func_ins(self):
        res = []
        for port in self.in_ports:
            if port.get_name() in self.inputs:
                res.append(port)

        return res
    
    def _get_func_outs(self):
        res = []
        for port in self.out_ports:
            if port.get_name() in self.outputs:
                res.append(port)

        return res