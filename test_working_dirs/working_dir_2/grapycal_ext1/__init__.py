from typing import Any
from grapycal.sobjects.functionNode import FunctionNode

class DivisionNode(FunctionNode):
    category = 'function/math'
    inputs = ['a', 'b']
    input_edge_limit = [None,None]
    outputs = ['a/b']
    
    def build(self):
        super().build()
        self.label.set('/')

    def calculate(self, data):
        nominators = data[0]
        denominators = data[1]
        if len(nominators) == 0:
            nominator = 1
        else:
            nominator = nominators[0]
            for d in nominators[1:]:
                nominator *= d

        if len(denominators) == 0:
            denominator = 1
        else:
            denominator = denominators[0]
            for d in denominators[1:]:
                denominator *= d
        return nominator/denominator
                