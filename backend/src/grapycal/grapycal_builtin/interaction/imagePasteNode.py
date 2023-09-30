from grapycal.sobjects.sourceNode import SourceNode

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

class ImagePasteNode(SourceNode):
    category = 'Interaction'

    def build_node(self):
        self.img = self.add_image_control()

