from grapycal import Node
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort


class ListNode(Node):
    category = 'data'
    def build_node(self):
        self.label.set('List (0)')
        self.run_port = self.add_in_port('run')
        self.set_port = self.add_in_port('set')
        self.append_port = self.add_in_port('append')
        self.get_port = self.add_out_port('get')

    def init_node(self):
        self.data = []

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.run_port:
            edge.get_data()
            self.get_port.push_data(self.data)
        elif port == self.set_port:
            data = edge.get_data()
            if data is None:
                self.data = []
                self.label.set('List (0)')
            else:
                self.data = data
                self.label.set(f'List ({len(data)})')
        elif port == self.append_port:
            self.data.append(edge.get_data())
            self.label.set(f'List ({len(self.data)})')

