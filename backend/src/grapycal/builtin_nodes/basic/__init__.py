from grapycal.builtin_nodes.textInputNode import TextInputNode
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import StringTopic

class EvalAssignNode(Node):

    def pre_build(self, attribute_values, workspace, is_preview:bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self.add_attribute('code', StringTopic, 'x')
        self.shape.set('frame')
    
    def build(self):
        super().build()
        self.in_port = self.add_in_port('in')
        self.out_port = self.add_out_port('out')
        self.add_child(TextInputNode)
