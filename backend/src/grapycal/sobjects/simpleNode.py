import functools
from turtle import back
from typing import Any, Dict
from grapycal.core.workspace import Workspace
from grapycal.sobjects.node import Node


class SimpleNode(Node):
    '''
    A subclass of `Node` that provides higher level inferface for defining nodes.
    '''
    background = False

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