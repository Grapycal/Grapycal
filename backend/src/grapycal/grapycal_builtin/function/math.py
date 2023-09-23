from grapycal.sobjects.functionNode import FunctionNode

class AdditionNode(FunctionNode):
    '''
    Adds a set of values together. The values can be of any addable type, such as numbers, NumPy arrays,
    PyTorch tensors, or strings.

    :inputs:
        - values: a set of values
        
    :outputs:
        - sum: sum of all values
    '''
    category = 'function/math'

    inputs = ['items']
    input_edge_limit = [None]
    outputs = ['sum']
    display_port_names = False

    def build_node(self):
        super().build_node()
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
                summation = summation + d #type: ignore
        return summation
    
class SubtractionNode(FunctionNode):
    '''
    Calculates sum(`B`) - sum(`A`).
    
    :inputs:
       - A: A set of values, `A`
       - B: A set of values, `B`
    
    :outputs:
        -  Difference: sum(`B`) - sum(`A`)
    '''
    category = 'function/math'
    inputs = ['a', 'b']
    input_edge_limit = [None, None]
    outputs = ['a-b']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('-')
        self.label_offset.set(-.09)
        self.shape.set('round')

    def calculate(self, data):
        return sum(data[0]) - sum(data[1])
    
class MultiplicationNode(FunctionNode):
    '''
    Multiplies a set of values together. The values can be of any multipliable type, such as numbers, NumPy arrays, or
    PyTorch tensors.

    :inputs:
        - values: a set of values
    
    :outputs:
        - product: product of all values
    '''
    category = 'function/math'
    inputs = ['items']
    input_edge_limit = [None]
    outputs = ['product']
    display_port_names = False

    def build_node(self):
        super().build_node()
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
                product = product * d
        return product
    
class DivisionNode(FunctionNode):
    '''
    Calculates product(`B`) / product(`A`).
    
    :inputs:
        - A: A set of values, `A`
        - B: A set of values, `B`

    :outputs:
        -  Quotient: product(`B`) / product(`A`)
    '''
    category = 'function/math'
    inputs = ['a', 'b']
    input_edge_limit = [None,None]
    outputs = ['a/b']
    display_port_names = False
    
    def build_node(self):
        super().build_node()
        self.label.set('/')
        self.shape.set('round')

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
                