from grapycal.sobjects.functionNode import FunctionNode

class AdditionNode(FunctionNode):
    category = 'function/math'

    inputs = ['in']
    input_edge_limit = [None]
    outputs = ['out']

    def build(self):
        super().build()
        self.label.set('+')
        self.label_offset.set(-.09)
        self.shape.set('round')

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
        self.label_offset.set(-.09)
        self.shape.set('round')

    def calculate(self, data):
        return sum(data[0]) - sum(data[1])
    
class MultiplicationNode(FunctionNode):
    category = 'function/math'
    inputs = ['in']
    input_edge_limit = [None]
    outputs = ['out']

    def build(self):
        super().build()
        self.label.set('*')
        self.label_offset.set(-.09)
        self.shape.set('round')

    def calculate(self, data):
        data = data[0]
        if len(data) == 0:
            product = 1
        else:
            product = data[0]
            for d in data[1:]:
                product *= d
        return product
    
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
                