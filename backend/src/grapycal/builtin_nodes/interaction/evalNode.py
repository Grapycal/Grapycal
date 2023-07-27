from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort

class EvalNode(Node):
    category = 'interaction'
    
    def build_node(self):
        self.out_port = self.add_out_port('')
        self.expr_control = self.add_control(TextControl)
        self.label.set('Eval')
        self.shape.set('simple')
        self.expose_attribute(self.expr_control.text,'text',display_name='expression')

    def init(self):
        super().init()
        self.has_value = False
        self.value = None

    def task(self):
        expression = self.expr_control.text.get()
        self.value = eval(expression,self.workspace.vars())
        self.has_value = True
        for edge in self.out_port.edges:
            edge.push_data(self.value)

    def double_click(self):
        self.run(self.task)

    def output_edge_added(self, edge: Edge, port: OutputPort):
        if self.has_value:
            edge.push_data(self.value)