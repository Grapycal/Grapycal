from grapycal import Node, Edge, InputPort

class IsEvenNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('IsEven')
        self.add_in_port('number')
        self.out_port = self.add_out_port('isEven')

    def edge_activated(self, edge: Edge, port: InputPort):
    
            # Compute the result
            result = edge.get_data() % 2 == 0
    
            # Feed the result to each edge connected to the output port
            self.out_port.push_data(result)