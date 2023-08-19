from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort

class ExecNode(Node):
    category = 'interaction'

    def build_node(self):
        self.in_port = self.add_in_port('')
        self.out_port = self.add_out_port('')
        self.text_control = self.add_control(TextControl)
        self.label.set('Exec')
        self.shape.set('simple')
        self.expose_attribute(self.text_control.text,'text',display_name='statements')

    def init(self):
        super().init()
        self.has_value = False
        self.value = None

    def task(self):
        stmt = self.text_control.text.get()
        exec(stmt,self.workspace.vars())
        self.has_value = True

    def double_click(self):
        self.run(self.task)

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.task)