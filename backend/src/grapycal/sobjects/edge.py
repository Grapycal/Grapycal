from typing import Any
from objectsync import SObject, StringTopic, IntTopic, ObjTopic

class Edge(SObject):
    frontend_type = 'Edge'
    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        self.tail = self.add_attribute('tail', ObjTopic)
        self.head = self.add_attribute('head', ObjTopic)