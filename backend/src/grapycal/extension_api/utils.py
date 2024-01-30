from contextlib import contextmanager
from typing import Callable, Dict, List
from objectsync import Topic


class Bus:
    '''
    Syncronizes all topics attached to it
    '''
    @contextmanager
    def lock(self):
        self._lock = True
        yield
        self._lock = False

    def __init__(self):
        self._topics:List[Topic] = []
        self._callbacks:Dict[Topic,Callable] = {}
        self._lock = False

    def add(self, topic:Topic):
        if len(self._topics):
            topic.set(self._topics[0].get())
        self._topics.append(topic)
        callback = lambda value: self._change(topic,value)
        topic.on_set += callback
        self._callbacks[topic] = callback

    def __add__(self, topic:Topic):
        self.add(topic)
        return self

    def remove(self, topic:Topic):
        self._topics.remove(topic)
        topic.on_set -= self._callbacks[topic]
        del self._callbacks[topic]

    def __sub__(self, topic:Topic):
        self.remove(topic)
        return self

    def _change(self, source:Topic, value):
        if self._lock:
            return
        with self.lock():
            for topic in self._topics:
                if topic.get() == value or topic == source:
                    continue
                topic.set(value)
    
    def __len__(self):
        return len(self._topics)