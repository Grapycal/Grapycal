from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from ..functionNode import FunctionNode

class AdditionNode(FunctionNode):
    category = 'function/math'

    inputs = ['in']
    input_edge_limit = [None]
    outputs = ['out']

    def build(self):
        super().build()
        self.label.set('+')
        self.label_offset.set(-.1)
        self.shape.set('round')
        self.primary_color.set('#00cc00')

    def calculate(self, data):
        data = data[0]
        if len(data) == 0:
            summation = 0
        else:
            summation = data[0]
            for d in data[1:]:
                summation += d #type: ignore
        return summation
    
class SubtractionNode(FunctionNode):
    category = 'function/math'
    inputs = ['in1', 'in2']
    input_edge_limit = [None, None]
    outputs = ['out']

    def build(self):
        super().build()
        self.label.set('-')
        self.label_offset.set(-.1)
        self.shape.set('round')
        self.primary_color.set('#00cc00')

    def calculate(self, data):
        return sum(data[0]) - sum(data[1])