from grapycal import command
from grapycal.extension.extension import SlashCommandCtx
from .interaction import *
from .data import *
from .function import *
from .procedural import *
from .container import *

del FunctionNode, SourceNode, Node

from grapycal import Extension

class GrapycalBuiltin(Extension):

    @command('Create function')
    def create_function(self,ctx:SlashCommandCtx):
        x = ctx.mouse_pos[0]
        y = ctx.mouse_pos[1]

        name = FuncDefManager.next_func_name('Function')

        in_node = self.create_node(FuncInNode, [x-150, y], name=name)
        out_node = self.create_node(FuncOutNode, [x+150, y], name=name)
        tail = in_node.get_out_port('x')
        head = out_node.get_in_port('y')
        self.create_edge(tail, head)

        self.create_node(FuncCallNode, [x-150, y+100], name=name)