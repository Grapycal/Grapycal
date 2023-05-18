from typing import Any
from objectsync import SObject, StringTopic, IntTopic

class Port(SObject):
    frontend_type = 'Port'
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        self.name = self.add_attribute('name', StringTopic, 'port name')

class InputPort(Port):
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        super().pre_build(attribute_values, workspace)
        self.add_attribute('is_input', IntTopic, 1)

class OutputPort(Port):
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        super().pre_build(attribute_values, workspace)
        self.add_attribute('is_input', IntTopic, 0)


