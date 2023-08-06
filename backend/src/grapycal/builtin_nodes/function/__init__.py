from grapycal import Node, TextControl, ListTopic
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from .math import *

class LambdaNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('Lambda')
        self.shape.set('simple')
        self.add_in_port('input',1,display_name = '')
        self.out = self.add_out_port('output',display_name = '')
        self.text = self.add_control(TextControl)
        self.text.label.set('λ x:')
        self.text.text.set('x')

        self.expose_attribute(self.text.text,'text',display_name='expression')

        self.input_args = self.add_attribute('input args',ListTopic,editor_type='list')
        self.input_args.on_insert += self.on_input_arg_added
        self.input_args.on_pop += self.on_input_arg_removed

    def on_input_arg_added(self, arg_name, position):
        assert position == len(self.input_args)-1 # currently only support adding to the end
        assert arg_name not in arg_name
        self.add_in_port(arg_name,1,display_name = arg_name)

    def on_input_arg_removed(self, arg_name, position):
        self.remove_in_port(arg_name)

    def input_edge_added(self, edge: Edge, port: InputPort):
        if edge.is_data_ready():    
            self.calculate(edge.get_data())

    def edge_activated(self, edge: Edge, port: InputPort):
        self.calculate(edge.get_data())

    def calculate(self,x):
        def task():
            y = eval('lambda x: ' + self.text.text.get(),self.workspace.vars())(x)
            self.out.push_data(y,retain=True)
        self.run(task)