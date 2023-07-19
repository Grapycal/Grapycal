from grapycal import Node, TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from .math import *

class LambdaNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('Lambda')
        self.shape.set('simple')
        self.add_in_port('input',1)
        self.out = self.add_out_port('output')
        self.text = self.add_control(TextControl)
        self.text.label.set('λ x:')
        self.text.text.set('x')

    def input_edge_added(self, edge: Edge, port: InputPort):
        self.calculate(edge.get_data())

    def edge_activated(self, edge: Edge, port: InputPort):
        self.calculate(edge.get_data())

    def calculate(self,x):
        def task():
            y = eval('lambda x: ' + self.text.text.get(),self.workspace.vars())(x)
            self.out.push_data(y,retain=True)
        self.run(task)