from grapycal import Node, Edge, InputPort

class IsEvenNode(Node):
    category = 'function'
    def build(self):
        self.label.set('IsEven')
        self.add_in_port('number')
        self.out_port = self.add_out_port('isEven')

    def edge_activated(self, edge: Edge, port: InputPort):
        result = edge.get_data() % 2 == 0
        for e in self.out_port.edges:
            e.push_data(result)


# class TestNode2(Node):
#     category = 'test'
#     def build(self):
#         self.add_out_port('out')
#         self.shape.set('simple')
#         self.label.set('ROS Topic')
        
#         self.add_control(TextControl)

# class TestNode3(Node):
#     category = 'test/1/1'
#     def build(self):
#         self.shape.set('round')
#         self.add_in_port('in')
#         self.label.set('<-')
#         self.add_control(TextControl).text.set('<-')