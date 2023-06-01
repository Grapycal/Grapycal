from grapycal.builtin_nodes.textInputNode import TextInputNode
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import StringTopic

class EvalAssignNode(Node):
    category = 'interaction'
    def pre_build(self, attribute_values, workspace, is_preview:bool = False):
        super().pre_build(attribute_values, workspace, is_preview)
        self.shape.set('frame')
    
    def build(self):
        super().build()
        self.in_port = self.add_in_port('in')
        self.out_port = self.add_out_port('out')

        self.text_input_port = self.add_in_port('text_input')
        self.text_input = self.add_child(TextInputNode)
        #self.create_edge(self.text_input.out_port, self.text_input_port)
        self.get_parent().add_child(Edge, tail=self.text_input.out_port, head=self.text_input_port)

        print(self.text_input_port.edges,'qwq')

    def activate(self):
        super().activate()
        expression = self.text_input_port.edges[0].get_data()
        assert isinstance(expression, str)
        value = eval(expression)
        for edge in self.out_port.edges:
            edge.push_data(value)

    def double_click(self):
        self.activate()