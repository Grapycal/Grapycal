from grapycal.sobjects.node import Node


class EventNode(Node):
    category = 'procedural'

    def build_node(self):
        self.run_port = self.add_in_port('run')
        self.label.set('Event')
        self.shape.set('normal')

    def init_node(self):

        ...