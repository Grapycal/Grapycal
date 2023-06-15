from typing import Any
from grapycal.sobjects.functionNode import FunctionNode

class DivisionNode(FunctionNode):
    category = 'function/math'
    inputs = ['a', 'b']
    input_edge_limit = [1, 1]
    outputs = ['a/b']

    def calculate(self, data: list[Any]):
        return data[0] / data[1]
