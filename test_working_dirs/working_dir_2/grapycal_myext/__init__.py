import io
from typing import Any, Dict
from grapycal import Node, Edge, InputPort, TextControl, ButtonControl
from grapycal.core.workspace import Workspace
from grapycal.sobjects.controls.imageControl import ImageControl
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort

import matplotlib
matplotlib.use('agg') # use non-interactive backend
import matplotlib.pyplot as plt

class ImageDisplayNode(Node):
    category = 'interaction'
    def build_node(self):
        self.label.set('imshow')
        self.shape.set('simple')
        self.img = self.add_control(ImageControl)
        self.add_in_port('image')

    def edge_activated(self, edge: Edge, port: InputPort):
        data = edge.get_data()
        # use plt to convert to jpg
        buf = io.BytesIO()
        fig = plt.figure()
        plt.imshow(data)
        plt.savefig(buf,format='jpg')
        plt.close(fig)
        self.img.set_image(buf)

class IsEvenNode(Node):
    category = 'function'

    def build_node(self):
        self.label.set('IsEven')
        self.add_in_port('number')
        self.out_port = self.add_out_port('isEven')
        self.text = self.add_control(TextControl)
        self.button = self.add_control(ButtonControl, label='Test')
        
    def init(self):
        super().init()
        self.i=1
        self.button.on_click += self.button_clicked

    def button_clicked(self):
        self.i += 1
        self.text.text.set(f'IsEven {self.i}')

    def edge_activated(self, edge: Edge, port: InputPort):
        result = edge.get_data() % 2 == 0
        for e in self.out_port.edges:
            e.push_data(result)


class CounterNode(Node):
    category = 'function'
    def build_node(self, is_preview=False, **build_node_args):
        self.text = self.add_control(TextControl)
        self.text.text.set('0')
        self.add_control(ButtonControl, label='Add').on_click += self.button_clicked
        self.add_in_port('set')
        self.add_out_port('get')

    def init(self):
        super().init()
        self.i=0

    def button_clicked(self):
        self.i += 1
        self.text.text.set(str(self.i))

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