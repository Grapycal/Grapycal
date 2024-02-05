import random
from typing import Any
from grapycal.sobjects.port import InputPort, OutputPort, Port
from objectsync import SObject, StringTopic, ObjTopic, IntTopic
from objectsync.sobject import SObjectSerialized

try:
    import torch
    HAS_TORCH = True
except:
    HAS_TORCH = False

try :
    import numpy as np
    HAS_NUMPY = True
except:
    HAS_NUMPY = False

class Edge(SObject):
    frontend_type = 'Edge'

    def build(self, tail:OutputPort|None = None, head:InputPort|None = None):
        self.tail = self.add_attribute('tail', ObjTopic[OutputPort], tail)
        self.head = self.add_attribute('head', ObjTopic[InputPort], head)
        self.label = self.add_attribute('label', StringTopic, is_stateful=False)
        self.data_ready_topic = self.add_attribute('data_ready',IntTopic,1,is_stateful=False) # 0 for running, other for not running

    def init(self):                
        self._data = None
        self._activated = False
        self._data_ready = False
        self.reaquirable = False

        self.data_ready_topic.set(1) # prevent a restored edge to show data ready

        self.tail.on_set2 += self.on_tail_set
        self.head.on_set2 += self.on_head_set

        self.on_tail_set(None, self.tail.get())
        self.on_head_set(None, self.head.get())
        

    def on_tail_set(self, old_tail:Port|None, new_tail:Port|None):
        if old_tail:
            old_tail.remove_edge(self)
        if new_tail is None:
            self.remove()
            raise Exception(f'{self} tail cannot be None')
        if new_tail:
            new_tail.add_edge(self)
        self.label.set('')

    def on_head_set(self, old_head:Port|None, new_head:InputPort|None):
        if old_head:
            old_head.remove_edge(self)
        if new_head is None:
            self.remove()
            raise Exception(f'{self} head cannot be None')
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
            with self._server.record(): # aquire a lock to prevent calling set while destroying
                if not self.is_destroyed():
                    self.data_ready_topic.set(random.randint(0,10000))
        return self._data
    
    def peek_data(self)->Any:
        if not self._data_ready:
            raise Exception('Data not available')
        return self._data
    
    def push_data(self, data, label:str|None=None):
        self._data = data
        self._activated = True
        self._data_ready = True
        with self._server.record(): # aquire a lock to prevent calling set while destroying
            if self.is_destroyed():
                return
            self.data_ready_topic.set(0)
        if label:
            self.label.set(label)
        else:
            label = ''
            if HAS_TORCH and isinstance(data, torch.Tensor):
                label = str(list(data.shape)) if list(data.shape)!=[] else 'scalar'
            elif HAS_NUMPY and isinstance(data, np.ndarray):
                label = str(list(data.shape)) if list(data.shape)!=[] else 'scalar'

            self.label.set(label)

        head = self.head.get()
        if head:
            head.activated_by_edge(self)

        self._activated = False

    def set_label(self, label):
        self.label.set(label)
    
    def is_activated(self):
        return self._activated
    
    def is_data_ready(self):
        return self._data_ready
