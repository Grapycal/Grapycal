from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort

class ExecNode(Node):
    category = 'interaction'

    def build_node(self):
        self.out_port = self.add_out_port('')
        self.text_control = self.add_control(TextControl)
        self.label.set('Exec')
        self.shape.set('simple')

    def init(self):
        super().init()
        self.has_value = False
        self.value = None

    def activate(self):
        stmt = self.text_control.text.get()
        exec(stmt,self.workspace.vars())
        self.has_value = True

    def double_click(self):
        self.activate()

    def output_edge_added(self, edge: Edge, port: OutputPort):
        if self.has_value:
            edge.push_data(self.value)