import io
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from grapycal.sobjects.sourceNode import SourceNode
from grapycal.sobjects.controls import TextControl
from grapycal import ListTopic

import ast

from objectsync import StringTopic
# exec that prints correctly
def exec_(script,globals=None, locals=None,print_=None):
    stmts = list(ast.iter_child_nodes(ast.parse(script)))
    if stmts == []:
        return
    if isinstance(stmts[-1], ast.Expr):
        if len(stmts) > 1:
            ast_module = ast.parse("")
            ast_module.body=stmts[:-1]
            exec(compile(ast_module, filename="<ast>", mode="exec"), globals, locals)
        last = eval(compile(ast.Expression(body=stmts[-1].value), filename="<ast>", mode="eval"), globals, locals)
        if last is not None and print_ is not None:
            print_(last)
        return last
    else:    
        exec(script, globals, locals)

class ExecNode(SourceNode):
    '''
    Equivalent to Python's `exec` function. It executes the statements in the input text box.

    To make it run, either send in a signal to the `run` input port, or double click on the node.

    :inputs:
        - run: send in a signal to run the statements
        - *inputs: You can add any variable of inputs to the node and 
                    Click the (+) in the inspector to plus the name of the variable.

    :outputs:
        - done: send out a signal when the statements are done
        - *outputs: You can add any variable of outputs to the node.
                    Click the (+) in the inspector to plus the name of the variable.
    '''
    category = 'interaction'

    def build_node(self,text=''):
        super().build_node()
        self.out_port = self.add_out_port('done')
        self.text_control = self.add_text_control(name='text')
        self.label.set('Execute')
        self.shape.set('simple')
        self.css_classes.append('fit-content')
        self.output_control = self.add_text_control('',readonly=True,name='output_control')
        self.inputs = self.add_attribute('inputs',ListTopic,[],editor_type='list')
        self.outputs = self.add_attribute('outputs',ListTopic,[],editor_type='list')
        self.print_last_expr = self.add_attribute('print last expr',StringTopic,editor_type='options',options=['yes','no'],init_value='yes')
        self.icon_path.set('python')

        if self.is_new:
            self.text_control.set(text)
        else:
            for name in self.inputs:
                self.add_input(name,None)
            for name in self.outputs:
                self.add_output(name,None)

    def init_node(self):
        super().init_node()
        self.inputs.on_insert.add_auto(self.add_input)
        self.inputs.on_pop.add_auto(self.pop_input)
        self.outputs.on_insert.add_auto(self.add_output)
        self.outputs.on_pop.add_auto(self.pop_output)

    def add_input(self, name,_):
        self.add_in_port(name,1)

    def pop_input(self, name,_):
        self.remove_in_port(name)

    def add_output(self, name,_):
        self.add_out_port(name)

    def pop_output(self, name,_):
        self.remove_out_port(name)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('text','output_control')
        self.restore_attributes('inputs','outputs')

    def edge_activated(self, edge: Edge, port: InputPort):
        super().edge_activated(edge, port)
        if port == self.run_port:
            return
        for name in self.inputs:
            port = self.get_in_port(name)
            if not port.is_all_ready():
                return
        self.run(self.task)

    def task(self):
        self.output_control.set('')
        stmt = self.text_control.text.get()
        for name in self.inputs:
            port = self.get_in_port(name)
            if port.is_all_ready():
                self.workspace.vars().update({name:port.get()})
        self.workspace.vars().update({'print':self.print,'self':self})
        try:
            result = exec_(stmt,self.workspace.vars(),print_=self.print if self.print_last_expr.get()=='yes' else None)
        except Exception as e:
            self.print_exception(e,-3)
            return
        self.out_port.push(result)
        for name in self.outputs:
            self.get_out_port(name).push(self.workspace.vars()[name])

    def print(self, *args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        self.output_control.set(self.output_control.get()+contents)
        