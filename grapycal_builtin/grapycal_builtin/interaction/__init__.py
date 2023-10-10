from .printNode import *
from .evalNode import *
from .execNode import *
from .imagePasteNode import *

class LabelNode(Node):
    category = 'interaction'
    def build_node(self):
        self.shape.set('simple')
        self.css_classes.append('fit-content')
        self.expose_attribute(self.label, editor_type='text')
