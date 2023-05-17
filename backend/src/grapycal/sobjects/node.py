from typing import Any, Dict
from objectsync import SObject, StringTopic, IntTopic

class Node(SObject):
    frontend_type = 'Node'
    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace):
        super().pre_build(attribute_values)

        self.workspace = workspace
        
        self.shape = self.add_attribute('shape', StringTopic, 'block') # round, block, blockNamed, hideBody
        self.output = self.add_attribute('output', StringTopic, 'output')
        self.label = self.add_attribute('label', StringTopic, 'label')
        self.pos = self.add_attribute('pos', StringTopic, '0,0')
        self.is_preview = self.add_attribute('is_preview', IntTopic, 0)

class TextNode(Node):
    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace):
        super().pre_build(attribute_values, workspace)

        self.in_port = 1