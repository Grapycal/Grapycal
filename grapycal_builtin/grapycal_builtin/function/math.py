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
    max_in_degree = [None]
    outputs = ['sum']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('+')
        self.label_offset.set(-.09)
        self.shape.set('round')

    def calculate(self, items):
        if len(items) == 0:
            summation = 0
        else:
            summation = items[0]
            for d in items[1:]:
                summation = summation + d #type: ignore
        return summation
    
class SubtractionNode(FunctionNode):
    '''
    Calculates sum(`B`) - sum(`A`).
    
    :inputs:
       - A: A set of values, `A`
       - B: A set of values, `B`
    
    :outputs:
        -  Difference: sum(`A`) - sum(`B`)
    '''
    category = 'function/math'
    inputs = ['a', 'b']
    max_in_degree = [None, None]
    outputs = ['a-b']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('-')
        self.label_offset.set(-.09)
        self.shape.set('round')

    def calculate(self, a,b):
        return sum(a) - sum(b)
    
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
    max_in_degree = [None]
    outputs = ['product']
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('*')
        self.label_offset.set(-.09)
        self.shape.set('round')

    def calculate(self, items):
        if len(items) == 0:
            product = 1
        else:
            product = items[0]
            for d in items[1:]:
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
    max_in_degree = [None,None]
    outputs = ['a/b']
    display_port_names = False
    
    def build_node(self):
        super().build_node()
        self.label.set('/')
        self.shape.set('round')

    def calculate(self, a, b):
        if len(a) == 0:
            nominator = 1
        else:
            nominator = a[0]
            for d in a[1:]:
                nominator *= d

        if len(b) == 0:
            denominator = 1
        else:
            denominator = b[0]
            for d in b[1:]:
                denominator *= d
        return nominator/denominator
                