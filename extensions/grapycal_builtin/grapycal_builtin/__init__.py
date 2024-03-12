from grapycal import slash_command
from grapycal.extension.extension import SlashCommandCtx
from .interaction import *
from .data import *
from .function import *
from .procedural import *
from .container import *

del FunctionNode, SourceNode, Node

from grapycal import Extension

class GrapycalBuiltin(Extension):
    @slash_command('create function')
    def create_function(self,ctx:SlashCommandCtx):
        self.create_node(FuncInNode, ctx.mouse_pos)

# from grapycal import Extension