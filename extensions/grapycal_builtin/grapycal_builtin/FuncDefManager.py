from typing import TYPE_CHECKING, Dict, Iterable

from grapycal_builtin.utils import find_next_valid_name
from grapycal_torch.manager import ListDict

if TYPE_CHECKING:
    from grapycal_builtin.procedural.funcDef import FuncCallNode, FuncInNode, FuncOutNode

class FuncDefManager:
    calls: ListDict['FuncCallNode'] = ListDict()
    ins: Dict[str,'FuncInNode'] = {}
    outs: Dict[str,'FuncOutNode'] = {}

    @classmethod
    def next_func_name(cls,name:str):
        invalids = cls.ins.keys() | cls.outs.keys()
        return find_next_valid_name(name, invalids)