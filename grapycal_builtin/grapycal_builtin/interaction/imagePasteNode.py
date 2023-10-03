import io
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort
from grapycal.sobjects.sourceNode import SourceNode
from grapycal import StringTopic
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class ImagePasteNode(SourceNode):
    category = 'interaction'

    def build_node(self):
        super().build_node()
        self.label.set('Paste Image')
        self.img = self.add_image_control(name='img')
        self.format = self.add_attribute('format',StringTopic,'torch',editor_type='options',options=['torch','numpy'])
        self.out_port = self.add_out_port('img')
        
    def init_node(self):
        super().init_node()
        self.format.add_validator(self.format_validator)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('img')

    def format_validator(self,format,_):
        if 'torch' in format:
            if not HAS_TORCH:
                return False
            return True
        if 'numpy' in format:
            if not HAS_NUMPY:
                return False
            return True
        return False
    
    def task(self):
        if not HAS_PIL:
            raise ImportError('PIL is not installed. Please install PIL to use this node.')
        image_bytes:bytes = self.img.get()
        # convert image to PIL
        img = Image.open(io.BytesIO(image_bytes))
        # comvert image to torch or numpy
        if self.format.get() == 'torch':
            img = torch.from_numpy(np.array(img))
            img = img.permute(2,0,1).to(torch.float32)/255
            if img.shape[0] == 4:
                img = img[:3]
        elif self.format.get() == 'numpy':
            img = np.array(img).astype(np.float32).transpose(2,0,1)/255
            if img.shape[0] == 4:
                img = img[:3]

        self.out_port.push_data(img)

class ImageDisplayNode(Node):
    category = 'interaction'
    def build_node(self):
        self.label.set('Display Image')
        self.shape.set('simple')
        self.img = self.add_image_control(name='img')
        self.add_in_port('tensor', 1)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('img')

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.update_image)

    def update_image(self):
        data = self.in_ports[0].edges[0].get_data()

        # if isinstance(data, Image.Image):
        #     data = np.array(data)

        if isinstance(data, torch.Tensor):
            data = data.detach().cpu().numpy()
            data = data.transpose(1,2,0)

        elif isinstance(data, np.ndarray):
            data = data.transpose(1,2,0)

        # use plt to convert to jpg
        buf = io.BytesIO()
        fig = plt.figure()
        try:
            plt.imshow(data)
            plt.axis('off')
            plt.savefig(buf,format='jpg',bbox_inches='tight', transparent="True", pad_inches=0)
        finally:
            plt.close(fig)
        self.img.set(buf)

    def input_edge_removed(self, edge: Edge, port: InputPort):
        self.img.set(None)
