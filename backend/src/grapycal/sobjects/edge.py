from enum import Enum
from typing import Any
from grapycal.sobjects.port import InputPort, OutputPort, Port
from objectsync import SObject, StringTopic, IntTopic, ObjTopic
from objectsync.sobject import SObjectSerialized

try:
    import torch
    HAS_TORCH = True
except:
    HAS_TORCH = False

class Edge(SObject):
    frontend_type = 'Edge'

    def build(self, tail:OutputPort|None = None, head:InputPort|None = None):
        self.tail = self.add_attribute('tail', ObjTopic[OutputPort], tail)
        self.head = self.add_attribute('head', ObjTopic[InputPort], head)
        self.label = self.add_attribute('label', StringTopic, is_stateful=False)

    def init(self):
        
        self._data = None
        self._activated = False
        self._data_ready = False
        self.reaquirable = False

        self.tail.on_set2 += self.on_tail_set
        self.head.on_set2 += self.on_head_set

        self.on_tail_set(None, self.tail.get())
        self.on_head_set(None, self.head.get())


    def on_tail_set(self, old_tail:Port|None, new_tail:Port|None):
        if old_tail:
            old_tail.remove_edge(self)
        if new_tail:
            new_tail.add_edge(self)
        self.label.set('')

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
            raise Exception('Data not available')
        self._activated = False
        if not self.reaquirable:
            self._data_ready = False
        return self._data
    
    def push_data(self, data, label:str|None=None):
        self._data = data
        self._activated = True
        self._data_ready = True
        if label:
            self.label.set(label)
        else:
            label = ''
            if HAS_TORCH:
                if isinstance(data, torch.Tensor):
                    label = str(list(data.shape)) if list(data.shape)!=[] else 'scalar'
            self.label.set(label)

        head = self.head.get()
        if head:
            head.edge_activated(self)

        self._activated = False

    def set_label(self, label):
        self.label.set(label)
    
    def is_activated(self):
        return self._activated
    
    def is_data_ready(self):
        return self._data_ready
