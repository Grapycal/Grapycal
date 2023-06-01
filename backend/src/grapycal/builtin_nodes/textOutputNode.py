from grapycal.sobjects.node import Node


class TextOutputNode(Node):
    frontend_type = 'TextOutputNode'
    category = 'interaction'
    def build(self):
        super().build()
        self.add_in_port('in')
        self.label.set('')

    def edge_activated(self, edge):
        data = edge.get_data()
        print('edge activated', data)
        self.label.set(data)