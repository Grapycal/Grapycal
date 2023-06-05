import time
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
        # with self.redirect_output():
        #     print(f'1_Adding {data} = {summation}')
        def task_long():
            print(f'L1_Adding {data} = {summation}')
            time.sleep(1)
            print(f'L2_Adding {data} = {summation}')
            time.sleep(1)
            print(f'L3_Adding {data} = {summation}')
        def task_short():
            print(f'S1_Adding {data} = {summation}')
            time.sleep(0.1)
            print(f'S2_Adding {data} = {summation}')
            time.sleep(0.1)
            print(f'S3_Adding {data} = {summation}')
        self.run_in_background(task_long)
        task_short()
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