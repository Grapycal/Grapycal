from enum import Enum
from typing import Any
from grapycal.sobjects.port import Port
from objectsync import SObject, StringTopic, IntTopic, ObjTopic
from objectsync.sobject import SObjectSerialized



class Edge(SObject):
    frontend_type = 'Edge'

    def pre_build(self, attribute_values: dict[str, Any] | None, workspace):
        self.tail = self.add_attribute('tail', ObjTopic[Port])
        self.head = self.add_attribute('head', ObjTopic[Port])
        self.tail.on_set2 += self.on_tail_set
        self.head.on_set2 += self.on_head_set

        self._data = None
        self._activated = False
        self._data_ready = False
        self.reaquirable = True

    def on_tail_set(self, old_tail:Port, new_tail:Port):
        if old_tail:
            old_tail.remove_edge(self)
        if new_tail:
            new_tail.add_edge(self)

    def on_head_set(self, old_head:Port, new_head:Port):
        if old_head:
            old_head.remove_edge(self)
        if new_head:
            new_head.add_edge(self)
            if self._activated:
                new_head.node.edge_activated(self)

    def destroy(self) -> SObjectSerialized:
        if self.tail.get():
            self.tail.get().remove_edge(self)
        if self.head.get():
            self.head.get().remove_edge(self)
        return super().destroy()

    def get_data(self):

        if not self._data_ready:
            #TODO: aquire backward
            raise Exception('Data not available')
        self._activated = False
        if not self.reaquirable:
            self._data_ready = False
        return self._data
    
    def push_data(self, data):
        self._data = data
        self._activated = True
        self._data_ready = True
        if self.head.get():
            self.head.get().node.edge_activated(self)
    
    def is_activated(self):
        return self._activated
    
    def is_data_ready(self):
        return self._data_ready
