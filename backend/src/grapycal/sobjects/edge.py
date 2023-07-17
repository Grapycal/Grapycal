from enum import Enum
from typing import Any
from grapycal.sobjects.port import InputPort, OutputPort, Port
from objectsync import SObject, StringTopic, IntTopic, ObjTopic
from objectsync.sobject import SObjectSerialized



class Edge(SObject):
    frontend_type = 'Edge'

    def build(self, tail:OutputPort|None = None, head:InputPort|None = None):
        self.tail = self.add_attribute('tail', ObjTopic[OutputPort], tail)
        self.head = self.add_attribute('head', ObjTopic[InputPort], head)

    def init(self):
        
        self._data = None
        self._activated = False
        self._data_ready = False
        self.reaquirable = True

        self.tail.on_set2 += self.on_tail_set
        self.head.on_set2 += self.on_head_set

        self.on_tail_set(None, self.tail.get())
        self.on_head_set(None, self.head.get())


    def on_tail_set(self, old_tail:Port|None, new_tail:Port|None):
        if old_tail:
            old_tail.remove_edge(self)
        if new_tail:
            new_tail.add_edge(self)

    def on_head_set(self, old_head:Port|None, new_head:InputPort|None):
        if old_head:
            old_head.remove_edge(self)
        if new_head:
            new_head.add_edge(self)
            if self._activated:
                new_head.node.edge_activated(self, new_head)

    def destroy(self) -> SObjectSerialized:
        if self.tail.get():
            self.tail.get().remove_edge(self)
        if self.head.get():
            self.head.get().remove_edge(self)
        return super().destroy()

    def get_data(self)->Any:

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
        head = self.head.get()
        if head:
            head.node.edge_activated(self, head)
    
    def is_activated(self):
        return self._activated
    
    def is_data_ready(self):
        return self._data_ready
