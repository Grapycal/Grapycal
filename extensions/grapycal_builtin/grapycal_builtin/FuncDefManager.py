from typing import TYPE_CHECKING, Dict, Iterable

from grapycal import CommandCtx
from grapycal_builtin.utils import ListDict, find_next_valid_name

if TYPE_CHECKING:
    from grapycal_builtin.procedural.funcDef import FuncCallNode, FuncInNode, FuncOutNode
    from grapycal_builtin import GrapycalBuiltin

class FuncDefManager:
    def __init__(self,ext:'GrapycalBuiltin') -> None:
        self.calls: ListDict['FuncCallNode'] = ListDict()
        self.ins: Dict[str,'FuncInNode'] = {}
        self.outs: Dict[str,'FuncOutNode'] = {}
        self.ext: 'GrapycalBuiltin' = ext

    def next_func_name(self,name:str):
        invalids = self.ins.keys() | self.outs.keys()
        return find_next_valid_name(name, invalids)

    def add_in(self, name:str, node:'FuncInNode'):
        if not self.ext.has_command(f'Call: {name}'):
            self.ext.register_command(f'Call: {name}', lambda ctx: self._create_call(ctx,name))
        self.ins[name] = node

    def remove_in(self, name:str):
            del self.ins[name]
            if name not in self.outs:
                self.ext.unregister_command(f'Call: {name}')

    def add_out(self, name:str, node:'FuncOutNode'):
        if not self.ext.has_command(f'Call: {name}'):
            self.ext.register_command(f'Call: {name}', lambda ctx: self._create_call(ctx,name))
        self.outs[name] = node
        
    def remove_out(self, name:str):
        del self.outs[name]
        if name not in self.ins:
            self.ext.unregister_command(f'Call: {name}')

    def _create_call(self, ctx:CommandCtx, name:str):
        from grapycal_builtin.procedural.funcDef import FuncCallNode # avoid circular import
        self.ext.create_node(FuncCallNode, ctx.mouse_pos, name=name)
