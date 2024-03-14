from grapycal import command
from grapycal import CommandCtx
from .interaction import *
from .data import *
from .function import *
from .procedural import *
from .container import *

del FunctionNode, SourceNode, Node

from grapycal import Extension

class GrapycalBuiltin(Extension):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.func_def_manager = FuncDefManager(self)

    @command('Create function')
    def create_function(self,ctx:CommandCtx):
        x = ctx.mouse_pos[0]
        y = ctx.mouse_pos[1]

        name = self.func_def_manager.next_func_name('Function')

        in_node = self.create_node(FuncInNode, [x-150, y], name=name)
        out_node = self.create_node(FuncOutNode, [x+150, y], name=name)
        tail = in_node.get_out_port('x')
        head = out_node.get_in_port('y')
        self.create_edge(tail, head)

        self.create_node(FuncCallNode, [x-150, y+100], name=name)