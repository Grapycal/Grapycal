from typing import Any, List
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.sobjects.node import Node
class ActiveNode(Node):

    def build_node(self):
        super().build_node()
        self.control = self.add_in_port('control')

    def init_node(self):
        super().init_node()
        self.control.on_activate += self.on_control_activate
    
    def task(self):
        '''
        You can define the task of this node here. 
        By default, this method will be called when double clicking the node or when the control port on the node
          is activated (if there is one).
        '''
        pass

    def double_click(self):
        self.run(self.task)

    def on_control_activate(self, edge:Edge, port:InputPort):
        self.run(self.task)