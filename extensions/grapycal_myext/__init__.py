from grapycal import Node, Edge, InputPort
from grapycal.sobjects.controls.buttonControl import ButtonControl
from grapycal.sobjects.controls.textControl import TextControl

class IsEvenNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('IsEven')
        self.add_in_port('number')
        self.out_port = self.add_out_port('isEven')

    def edge_activated(self, edge: Edge, port: InputPort):
    
            # Compute the result
            result = edge.get_data() % 2 == 0
    
            # Feed the result to each edge connected to the output port
            self.out_port.push_data(result)

class TestDefaultNode(Node):
    category = 'procedural'

    def build_node(self):
        super().build_node()
        self.label.set('Test default')
        self.shape.set('normal')
        self.in_port = self.add_in_port(
            'test_in', control_type = TextControl
        )
        self.add_in_port(
            'trigger', control_type = ButtonControl
        )
        self.add_text_control('str', 'control_label')
        self.out_port = self.add_out_port('test_out')

    def edge_activated(self, edge:Edge, port:InputPort):
        self.out_port.push_data(self.in_port.get_one_data())

    def double_click(self):
        self.out_port.push_data(self.in_port.get_one_data())