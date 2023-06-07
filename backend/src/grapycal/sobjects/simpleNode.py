import functools
from typing import Any, Dict
from grapycal.core.workspace import Workspace
from grapycal.sobjects.node import Node


class SimpleNode(Node):
    '''
    An easy to use Node class that can be used to create custom nodes.
    '''
    def pre_build(self, *args, **kwargs):
        super().pre_build(*args, **kwargs)
        self.background = True

    def run(self):
        pass

    def activate(self, *args, **kwargs):
        run = functools.partial(self.run, *args, **kwargs)
        if not self.background:
            self.run_in_foreground(run)
        else:
            self.run_in_background(run)

    def double_click(self):
        super().double_click()
        self.activate()