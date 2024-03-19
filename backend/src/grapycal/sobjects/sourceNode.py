from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from grapycal.sobjects.node import Node
class SourceNode(Node):
    '''
    Inherit from this class to conveniently create a node that can be a source of the graph (can be activated by the user.)
    This type of node can be activated by double clicking the node or by sending a signal the run port on the node.
    '''
    def build_node(self):
        super().build_node()
        self.run_port = self.add_in_port('run')

    def init_node(self):
        super().init_node()
        self.run_port.on_activate += self.on_activate
    
    def task(self):
        '''
        Define the task of this node here. 
        By default, this method will be called when double clicking the node or when the run port on the node
          is activated (if there is one).
        '''
        pass

    def double_click(self):
        self.run(self.task)

    def on_activate(self,port:InputPort):
        self.run_port.get_all() # clear data_ready so UI looks resonable 
        self.run(self.task)