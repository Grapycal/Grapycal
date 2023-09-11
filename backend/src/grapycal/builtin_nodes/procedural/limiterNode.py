import time
from grapycal import FloatTopic, IntTopic, Node
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from threading import Lock


class LimiterNode(Node):
    category = 'procedural'

    def build_node(self):
        super().build_node()
        self.label.set('Limiter')
        self.shape.set('simple')
        self.in_port = self.add_in_port('in')
        self.out_port = self.add_out_port('out')
        self.reduce_factor = self.add_attribute('reduce_factor', IntTopic, 10, editor_type='int')
        self.time_span = self.add_attribute('time_span', FloatTopic, 0.2, editor_type='float')

    def init_node(self):
        super().init_node()
        self.value = None
        self.has_value = False
        self.lock = Lock()
        self.counter = 0
        self.last_push_time = 0
        self.workspace.clock.on_tick += (self.tick)

    def edge_activated(self, edge: Edge, port: InputPort):
        with self.lock:
            self.value = edge.get_data()
            self.counter += 1
            self.has_value = True
            if self.counter == self.reduce_factor.get():
                self.counter = 0
                self.last_push_time = time.time()   
                self.has_value = False
                self.out_port.push_data(self.value)
                self.value = None

    def tick(self):
        if not self.has_value:
            return
        with self.lock:
            if self.value is not None and time.time() - self.last_push_time > self.time_span.get():
                self.counter = 0
                self.last_push_time = time.time()   
                self.has_value = False
                self.out_port.push_data(self.value)
                self.value = None
        
