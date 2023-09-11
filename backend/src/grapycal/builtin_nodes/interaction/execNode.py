from grapycal.sobjects.activeNode import ActiveNode
from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort

class ExecNode(ActiveNode):
    category = 'interaction'

    def build_node(self):
        super().build_node()
        self.out_port = self.add_out_port('')
        self.text_control = self.add_control(TextControl)
        self.label.set('Exec')
        self.shape.set('simple')
        self.expose_attribute(self.text_control.text,'text',display_name='statements')

    def task(self):
        stmt = self.text_control.text.get()
        exec(stmt,self.workspace.vars())
        self.out_port.push_data(None)