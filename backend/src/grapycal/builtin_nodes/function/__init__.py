from grapycal import Node, TextControl, ListTopic, ObjDictTopic
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from .math import *

class LambdaNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('Lambda')
        self.shape.set('normal')
        self.text_controls = self.add_attribute('text_controls',ObjDictTopic[TextControl])

        self.input_args = self.add_attribute('input_args',ListTopic,editor_type='list')
        self.output_names = self.add_attribute('outputs',ListTopic,editor_type='list')

    def init_node(self):
        self.input_args.on_insert.add_auto(self.on_input_arg_added)
        self.input_args.on_pop.add_auto(self.on_input_arg_removed)

        if self.is_new:
            self.input_args.insert('x')

        self.output_names.add_validator(ListTopic.unique_validator)
        self.output_names.on_insert.add_auto(self.on_output_added)
        self.output_names.on_pop.add_auto(self.on_output_removed)

        if self.is_new:
            self.output_names.insert('out')
            self.text_controls['out'].text.set('x')
    
    def on_input_arg_added(self, arg_name, position):# currently only support adding to the end
        self.add_in_port(arg_name,1,display_name = arg_name)

    def on_input_arg_removed(self, arg_name, position):
        self.remove_in_port(arg_name)

    def on_output_added(self, name, position):
        self.add_out_port(name,display_name = name)
        new_control = self.add_control(TextControl)
        self.text_controls[name]=new_control
        new_control.label.set(f'{name}= ')
        
    def on_output_removed(self, name, position):
        self.remove_out_port(name)
        self.text_controls.pop(name).remove()

    def input_edge_added(self, edge: Edge, port: InputPort):
        if edge.is_data_ready():    
            self.calculate()

    def edge_activated(self, edge: Edge, port: InputPort):
        self.calculate()

    def calculate(self):
        def task():
            arg_values = [port.edges[0].get_data() for port in self.in_ports.get()]
            for out_name, text_control in self.text_controls.get().items():
                expr = f'lambda {",".join(self.input_args)}: {text_control.text.get()}'
                y = eval(expr,self.workspace.vars())(*arg_values)
                self.get_out_port(out_name).push_data(y,retain=True)
        self.run(task)