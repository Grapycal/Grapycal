from typing import Any, Dict, List
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import SObject, StringTopic, IntTopic, ListTopic

class Node(SObject):
    frontend_type = 'Node'
    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace):
        super().pre_build(attribute_values)

        self.workspace = workspace
        
        self.shape = self.add_attribute('shape', StringTopic, 'block') # round, block, blockNamed, hideBody
        self.output = self.add_attribute('output', StringTopic, 'output')
        self.label = self.add_attribute('label', StringTopic, 'label')
        self.translation = self.add_attribute('translation', StringTopic, '0,0')
        self.is_preview = self.add_attribute('is_preview', IntTopic, 0)

        self.attr_in_ports = self.add_attribute('in_ports', ListTopic, [])
        self.in_ports: List[InputPort] = []

    def build(self):
        # add a port
        self.add_in_port('in')

    def post_build(self):
        pass

    def add_in_port(self,name):
        port = self.add_child(InputPort)
        port.name.set(name)

class TextNode(Node):
    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace):
        super().pre_build(attribute_values, workspace)

        self.in_port = 1