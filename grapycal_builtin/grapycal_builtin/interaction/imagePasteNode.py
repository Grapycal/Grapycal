import io
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort
from grapycal.sobjects.sourceNode import SourceNode
from grapycal import StringTopic, FloatTopic
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
        self.cmap = self.add_attribute('cmap',StringTopic,'gray',editor_type='options',
            options=['gray','viridis','plasma','inferno','magma','cividis','Greys','Purples','Blues','Greens','Oranges','Reds','YlOrBr','YlOrRd','OrRd','PuRd','RdPu','BuPu','GnBu','PuBu','YlGnBu','PuBuGn','BuGn','YlGn','binary','gist_yarg','gist_gray','gray','bone','pink','spring','summer','autumn','winter','cool','Wistia','hot','afmhot','gist_heat','copper','PiYG','PRGn','BrBG','PuOr','RdGy','RdBu','RdYlBu','RdYlGn','Spectral','coolwarm','bwr','seismic','twilight','twilight_shifted','hsv','Pastel1','Pastel2','Paired','Accent','Dark2','Set1','Set2','Set3','tab10','tab20','tab20b','tab20c','flag','prism','ocean','gist_earth','terrain','gist_stern','gnuplot','gnuplot2','CMRmap','cubehelix','brg','gist_rainbow','rainbow','jet','nipy_spectral','gist_ncar'])
        self.vmin = self.add_attribute('vmin',FloatTopic,0,editor_type='float')
        self.vmax = self.add_attribute('vmax',FloatTopic,1,editor_type='float')
        self.slice = self.add_text_control(label='slice: ',name='slice',text=':')
        self.in_port = self.add_in_port('data', 1)

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('img')
        self.restore_attributes('cmap')

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.update_image,data = self.in_port.get_one_data())

    def find_valid_slice(self,data:np.ndarray)->str|None:
        if data.ndim == 2:
            return ':'
        if data.ndim == 3 and data.shape[0] in [1,3]:
            return ':'
        if data.ndim >=3 and data.shape[-3] == 3:
            return ('0,' * (data.ndim - 3)) [:-1]
        if data.ndim >=3:
            return ('0,' * (data.ndim - 2)) [:-1]
        return None
    
    def preprocess_data(self,data):
        if HAS_TORCH and isinstance(data, torch.Tensor):
            data = data.detach().cpu().numpy()

        if HAS_NUMPY and isinstance(data, np.ndarray):
            # Ignore all dimensions with size 1 (except last 2 dimensions)
            while data.ndim > 2 and data.shape[0] == 1:
                data = data[0]
            # Let user specify which image to display
            slice_string = self.slice.text.get()

            unsliced_data = data
            try:
                data = eval(f'unsliced_data[{slice_string}]',globals(),locals())
            except:
                self.slice.text.set(':')
                pass
            # If 3 dimensions, transpose to (H,W,C)
            if data.ndim == 3 and (data.shape[0] == 3 or data.shape[0] == 1):
                data = data.transpose(1,2,0)
            elif data.ndim == 2:
                pass
            else:
                slice_string = self.find_valid_slice(unsliced_data)
                if slice_string is None:
                    raise ValueError(f'Cannot display image with shape {data.shape}')
                data = eval(f'unsliced_data[{slice_string}]',globals(),locals())
                self.slice.text.set(slice_string)

        return data

    def update_image(self,data):
        data = self.preprocess_data(data)
        
        # use plt to convert to jpg
        buf = io.BytesIO()
        fig = plt.figure()
        try:
            plt.imshow(data,cmap=self.cmap.get())
            plt.axis('off')
            plt.savefig(buf,format='jpg',bbox_inches='tight', transparent="True", pad_inches=0)
        finally:
            plt.close(fig)
        self.img.set(buf)

    def input_edge_removed(self, edge: Edge, port: InputPort):
        self.img.set(None)
