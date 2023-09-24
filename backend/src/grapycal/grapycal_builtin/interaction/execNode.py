from grapycal.sobjects.sourceNode import SourceNode
from grapycal.sobjects.controls import TextControl

class ExecNode(SourceNode):
    '''
    Equivalent to Python's `exec` function. It executes the statements in the input text box.

    To make it run, either send in a signal to the `run` input port, or double click on the node.

    :inputs:
        - run: send in a signal to run the statements
        

    :outputs:
        - done: send out a signal when the statements are done
    '''
    category = 'interaction'

    def build_node(self):
        super().build_node()
        self.out_port = self.add_out_port('done')
        self.text_control = self.add_control(TextControl)
        self.label.set('Exec')
        self.shape.set('simple')
        self.expose_attribute(self.text_control.text,'text',display_name='statements')

    def task(self):
        stmt = self.text_control.text.get()
        exec(stmt,self.workspace.vars())
        self.out_port.push_data(None)