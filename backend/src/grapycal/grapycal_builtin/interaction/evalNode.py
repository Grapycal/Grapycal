from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.sourceNode import SourceNode
from grapycal.sobjects.controls import TextControl

class EvalNode(SourceNode):
    '''

    Equivalent to Python's `eval` function. It evaluates the expression in the input text box and send out the result.

    To make it run, either send in a signal to the `run` input port, or double click on the node.

    :inputs:
        - run: send in a signal to evaluate the expression

    :outputs:
        - result: the result of the expression
    
    '''
    category = 'interaction'
    
    def build_node(self):
        super().build_node()
        self.out_port = self.add_out_port('')
        self.expr_control = self.add_control(TextControl,name='expr_control')
        self.label.set('Evaluate')
        self.shape.set('simple')
        self.expose_attribute(self.expr_control.text,'text',display_name='expression')

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('expr_control')

    def task(self):
        expression = self.expr_control.text.get()
        value = eval(expression,self.workspace.vars())
        for edge in self.out_port.edges:
            edge.push_data(value)