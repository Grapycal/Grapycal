import numpy
from grapycal import FunctionNode

class TrigonometricNode(FunctionNode):
    '''
    Calculate the sines of an array of values or one value. The array must be must NumPy arrays,

    :inputs:
        - values: an array of values or one value
        
    :outputs:
        - sin: sines of an array of values or one value
    '''
    category = 'numpy/operations/trigonometric functions'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('sin')
        self.option_control = self.add_option_control(options=['sin','cos','tan'],value='apple',name='opt')
        self.shape.set('round')

    def calculate(self, inp):
        return numpy.sin(inp)
    
    def option_changed(self,value:str):
        self.out_port.push(value)
class CosNode(FunctionNode):
    '''
    Calculate the cosines of an array of values or one value. The array must be must NumPy arrays,

    :inputs:
        - values: an array of values or one value
        
    :outputs:
        - cos: cosines of an array of values or one value
    '''
    category = 'numpy/operations/trigonometric functions'
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
class TanNode(FunctionNode):
    '''
    Calculate the tangents of an array of values or one value. The array must be must NumPy arrays,

    :inputs:
        - values: an array of values or one value
        
    :outputs:
        - tangents of an array of values or one value
    '''
    category = 'numpy/operations/trigonometric functions'
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
    '''Sizes an array of values. The array must be NumPy arrays,

    :inputs:
        - values: an array of values
    
    :outputs:
        - size: sizes of an array of values

    '''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('size')
        self.shape.set('simple')

    def calculate(self, inp):
        return 1
    
class SumNode(FunctionNode):
    '''sum of an array of values. The array must be NumPy arrays,
    
    :inputs:
        - values: an array of values.

    :outputs:
        - sum: sum of an array of values.
    '''
    catetory = 'numpy/operations'
    inputs = ['inp','axis']
    outputs = ['result']
    max_in_degree = [2]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('sum')
        self.shape.set('simple')

    def calculate(self, inp, axis=None):
        return numpy.sum(inp,axis=None)
class MeanNode(FunctionNode):
    '''mean of an array of values. The array must be NumPy arrays,

    :inputs:
        - values: an array of values.
    :outputs:
        - mean: mean of an array of values.
    '''
    catetory = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('mean')
        self.shape.set('simple')

    def calculate(self, inp):
        return inp.mean()
class MaxNode(FunctionNode):
    '''max of an array of values. The array must be NumPy arrays,

    :inputs:
        - values: an array of values.
    :outputs:
        - mean: mean of an array of values.
    '''
    catetory = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('max')
        self.shape.set('simple')

    def calculate(self, inp):
        return inp.max()
class MinNode(FunctionNode):
    '''min of an array of values. The array must be NumPy arrays,
    
    :inputs:
        - values: an array of values.
    :outputs:
        - min: min of an array of values.
    '''
    catetory = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('min')
        self.shape.set('simple')
    def calculate(self, inp):
        return inp.min()
    
class ArgmaxNode(FunctionNode):
    '''argmax of an array of values. The array must be NumPy arrays,

    :inputs:
        - values: an array of values.
    :outputs:
        - argmax: argmax of an array of values.
    '''
    catetory = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('argmax')
        self.shape.set('simple')

    def calculate(self, inp):
        return inp.argmax()
class ArgminNode(FunctionNode):
    '''argmin of an array of values. The array must be NumPy arrays,
    
    :inputs:
        - values: an array of values.
    :outputs:
        - argmin: argmin of an array of values.
    '''
    catetory = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('argmin')
        self.shape.set('simple')

    def calculate(self, inp):
        return inp.argmin()
class SquareNode(FunctionNode):
    '''square of an array of values. The array must be NumPy arrays, element wise operation

    :inputs:
        - values: an array of values.
    :outputs:
        - square: square of an array of values.
    '''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('^2')
        self.shape.set('simple')

    def calculate(self, inp):
        return inp**2
class SqrtNode(FunctionNode):
    '''sqrt of an array of values. The array must be NumPy arrays, element wise operation

    :inputs:
        - values: an array of values.
    :outputs:
        - sqrt: sqrt of an array of values. 
    '''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False
    def build_node(self):
        super().build_node()
        self.label.set('sqrt')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.sqrt(inp)
class ExpNode(FunctionNode):
    '''exp of an array of values. The array must be NumPy arrays, 
       element wise operation
    
    :inputs:
        - values: an array of values.
    :output:
        - exp: exp of an array of values.
    '''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('exp')
        self.shape.set('round')

    def calculate(self, inp):
        return numpy.exp(inp)
class LogNode(FunctionNode):
    '''log'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('log')
        self.shape.set('round')

    def calculate(self, inp):
        return numpy.log(inp)
class Log10Node(FunctionNode):
    '''log10'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('log10')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.log10(inp)
class Log2Node(FunctionNode):
    '''log2'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('log2')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.log2(inp)
class Log1pNode(FunctionNode):
    '''log1p'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = False

    def build_node(self):
        super().build_node()
        self.label.set('log1p')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.log1p(inp)
    
# class AbsNode(FunctionNode):
#     '''abs'''
#     category = 'numpy/operations'
#     inputs = ['inp']
#     outputs = ['result']
#     max_in_degree = [1]
#     display_port_names = True

#     def create(self):
#         super().create()
#         self.label.set('abs')
#         self.shape.set('simple')

#     def calculate(self, inp):
#         return numpy.abs(inp)
class SignNode(FunctionNode):
    '''sign'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('sign')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.sign(inp)
class CeilNode(FunctionNode):
    '''ceil'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('ceil')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.ceil(inp)

class FloorNode(FunctionNode):
    '''floor'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('floor')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.floor(inp)
class RoundNode(FunctionNode):
    '''round'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('round')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.round(inp)
class TruncNode(FunctionNode):
    '''trunc'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('trunc')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.trunc(inp)
class ClipNode(FunctionNode):
    '''clip'''
    category = 'numpy/operations'
    inputs = ['inp','a_min','a_max']
    outputs = ['result']
    max_in_degree = [1,1,1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('clip')
        self.shape.set('simple')

    def calculate(self, inp,a_min,a_max):
        return numpy.clip(inp,a_min,a_max)
class UniqueNode(FunctionNode):
    '''unique'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('unique')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.unique(inp)
class SortNode(FunctionNode):
    '''sort'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('sort')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.sort(inp)
class FlipNode(FunctionNode):
    '''flip'''
    category = 'numpy/operations'
    inputs = ['inp','axis']
    outputs = ['result']
    max_in_degree = [1,1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('flip')
        self.shape.set('simple')

    def calculate(self, inp,axis):
        return numpy.flip(inp,axis)
class FlipudNode(FunctionNode):
    '''flipud'''
    category = 'numpy/operations'
    inputs = ['inp']
    outputs = ['result']
    max_in_degree = [1]
    display_port_names = True

    def build_node(self):
        super().build_node()
        self.label.set('flipud')
        self.shape.set('simple')

    def calculate(self, inp):
        return numpy.flipud(inp)

