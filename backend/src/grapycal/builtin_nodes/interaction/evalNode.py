from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.activeNode import ActiveNode
from grapycal.sobjects.controls import TextControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort

class EvalNode(ActiveNode):
    category = 'interaction'
    
    def build_node(self):
        super().build_node()
        self.out_port = self.add_out_port('')
        self.expr_control = self.add_control(TextControl,name='expr_control')
        self.label.set('Eval')
        self.shape.set('simple')
        self.expose_attribute(self.expr_control.text,'text',display_name='expression')

    def recover_from_version(self, version: str, old: NodeInfo):
        super().recover_from_version(version, old)
        self.recover_controls('expr_control')

    def task(self):
        expression = self.expr_control.text.get()
        self.value = eval(expression,self.workspace.vars())
        for edge in self.out_port.edges:
            edge.push_data(self.value)