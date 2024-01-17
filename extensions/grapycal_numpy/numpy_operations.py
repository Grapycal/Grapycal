import numpy
from grapycal import FunctionNode

class SinNode(FunctionNode):
    '''sin'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('sin')
        self.shape.set('round')

    def calculate(self, inp):
        return numpy.sin(inp)
    
class CosNode(FunctionNode):
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('cos')
        self.shape.set('round') # round normal(larger rectangle) simple(smaller rectangle)

    def calculate(self, inp):
        return numpy.cos(inp)

class SizeNode(FunctionNode):
    catetory = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('size')
        self.shape.set('simple') # round normal(larger rectangle) simple(smaller rectangle)

    def calculate(self, inp):
        return inp.size
class SumNode(FunctionNode):
    catetory = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('sum')
        self.shape.set('simple') # round normal(larger rectangle) simple(smaller rectangle)

    def calculate(self, inp):
        return inp.sum()