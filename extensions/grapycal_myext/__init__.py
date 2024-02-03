from grapycal import Node, Edge, InputPort
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.controls.buttonControl import ButtonControl
from grapycal.sobjects.controls.optionControl import OptionControl
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
        self.add_control(OptionControl,options=['a','bb','abc','cd'],value='a',label='option')
        self.opt = self.add_in_port(name='opt',control_type=OptionControl,options=['a','bb','abc','cd'],value='a')
                
    def edge_activated(self, edge:Edge, port:InputPort):
        self.out_port.push_data(self.opt.get_one_data())

    def double_click(self):
        self.out_port.push_data(self.in_port.get_one_data())

class BeforeNode(Node):
    category = 'function'

    def build_node(self):
        self.label.set('Select a fruit')
        self.option_control = self.add_option_control(options=['apple','banana'],value='apple',name='opt')
        self.out_port = self.add_out_port('out')

    def init_node(self):
        self.option_control.on_set += self.option_changed

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('opt')

    def option_changed(self,value:str):
        self.out_port.push_data(value)

class AfterNode(Node):
    category = 'function'

    def create(self):
        self.label.set('Select a fruit')
        self.option_control = self.add_option_control(options=['apple','banana'],value='apple',name='opt')
        self.out_port = self.add_out_port('out')
        self.option_control.on_set += self.option_changed

    def option_changed(self,value:str):
        self.out_port.push_data(value)
