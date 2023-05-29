from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.nodes.functionNode import FunctionNode


class AdditionNode(FunctionNode):

    def build(self):
        super().build()
        self.label.set('+')
        self.shape.set('round')
        self.primary_color.set('#00cc00')
        self.category.set('function/basic')

    def calculate(self, data):
        if len(data) == 0:
            summation = 0
        else:
            summation = data[0]
            for d in data[1:]:
                summation += d #type: ignore
        for edge in self.out_port.edges:
            edge.push_data(summation)
        return summation

class MultiplicationNode(FunctionNode):

    def build(self):
        super().build()
        self.label.set('×')
        self.shape.set('round')
        self.primary_color.set('#00cc00')
        self.category.set('function/basic')

    def calculate(self, data):
        if len(data) == 0:
            product = 1
        else:
            product = data[0]
            for d in data[1:]:
                product *= d #type: ignore
        for edge in self.out_port.edges:
            edge.push_data(product)
        return product
    