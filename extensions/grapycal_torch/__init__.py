import asyncio
from pathlib import Path
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
from grapycal_torch.manager import ConfManager, MNManager, NetManager
from .basic import *
from .cnn import *
from .activation import *
from .tensor_operations import *
from .tensor import *
from .optimizerNode import *
from .transform import *
from .dataloader import *
from .normalize import *
from .loss import *
from .generative import *
from .networkDef import *
from .settings import *
from .configureNode import *


import torch
from torch import nn
import torchvision
from torchvision import transforms

from grapycal import Node, Edge, InputPort, Extension, command, CommandCtx

import io
import matplotlib

matplotlib.use("agg")  # use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

class GrapycalTorch(Extension):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mn = MNManager()
        self.net = NetManager(self)
        self.conf = ConfManager()

    @command('Create network')
    def create_network(self,ctx:CommandCtx):
        x = ctx.mouse_pos[0]
        y = ctx.mouse_pos[1]

        name = self.net.next_name('Network')

        in_node = self.create_node(NetworkInNode, [x-150, y], name=name)
        out_node = self.create_node(NetworkOutNode, [x+150, y], name=name)
        tail = in_node.get_out_port('x')
        head = out_node.get_in_port('y')
        self.create_edge(tail, head)

        self.create_node(NetworkCallNode, [x-150, y+100], name=name)

class MnistDatasetNode(SourceNode):
    category = "torch/dataset"

    def build_node(self):
        super().build_node()
        self.label.set("MNIST Dataset")
        self.out = self.add_out_port("MNIST Dataset")

    def task(self):
        ds = torchvision.datasets.mnist.MNIST("data", download=True)
        self.out.push_data(ds)


import aiofiles



class ImageDataset(torch.utils.data.Dataset): # type: ignore
    """
    Loads all images from a directory into memory
    """

    def __init__(self, directory: str, transform=None, max_size=None):
        super().__init__()
        self.directory = directory
        self.transform = transform
        if self.transform is None:
            # to tensor and minus 0.5 and crop to 208*176
            self.transform = transforms.Compose(
                [
                    transforms.ToTensor(),
                    transforms.Lambda(lambda x: x - 0.5),
                    transforms.Lambda(lambda x: x[:, 5:-5, 1:-1]),
                ]
            )
        self.max_size = max_size
        self.images = asyncio.run(self.load_images())

    async def load_images(self):
        # concurrent loading from disk using aiofiles
        async def load_image(path):
            async with aiofiles.open(path, "rb") as f:
                return plt.imread(io.BytesIO(await f.read()), format="jpg")

        tasks = []
        n = 0
        for path in Path(self.directory).iterdir():
            if path.is_file():
                tasks.append(load_image(path))
                n += 1
                if self.max_size is not None and n >= self.max_size:
                    print("Loaded", n, "images")
                    break
        return await asyncio.gather(*tasks)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = self.images[idx]
        if self.transform:
            img = self.transform(img)
        return img


class ImageDatasetNode(SourceNode):
    """
    Loads images from a directory
    """

    category = "torch/dataset"

    def build_node(self):
        super().build_node()
        self.label.set("Image Dataset")
        self.out = self.add_out_port("Image Dataset")
        self.dir = self.add_text_control("", "folder", name="folder")
        self.max_size = self.add_text_control("", "max_size", name="max_size")

    def init_node(self):
        super().init_node()
        self.ds = None

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls("folder", "max_size")

    def task(self):
        if self.ds is None or self.ds.directory != self.dir.get():
            self.ds = ImageDataset(self.dir.get(), max_size=int(self.max_size.get()))

        self.out.push_data(self.ds)


class EmaNode(Node):
    """
    Exponential moving average
    """

    category = "torch/transform"

    def build_node(self):
        super().build_node()
        self.label.set("EMA")
        self.reset_port = self.add_in_port("reset")
        self.in_port = self.add_in_port("input")
        self.out_port = self.add_out_port("output")
        self.alpha = self.add_attribute("alpha", FloatTopic, 0.9, editor_type="float")

    def init_node(self):
        super().init_node()
        self.ema = None

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.reset_port:
            self.ema = None
            return
        if port == self.in_port:
            self.run(self.task, data=edge.get_data())

    def task(self, data):
        if self.ema is None:
            self.ema = data
        else:
            self.ema = self.alpha.get() * data + (1 - self.alpha.get()) * self.ema
        self.out_port.push_data(self.ema)


class AverageNode(Node):
    """
    Average
    """

    category = "torch/transform"

    def build_node(self):
        super().build_node()
        self.label.set("Average")
        self.reset_port = self.add_in_port("reset")
        self.in_port = self.add_in_port("input")
        self.out_port = self.add_out_port("output")

    def init_node(self):
        super().init_node()
        self.sum = 0
        self.num = 0

    def edge_activated(self, edge: Edge, port: InputPort):
        if port == self.reset_port:
            self.sum = 0
            self.num = 0
            return
        if port == self.in_port:
            self.run(self.task, data=edge.get_data())

    def task(self, data):
        self.sum += data
        self.num += 1
        self.out_port.push_data(self.sum / self.num)


del ModuleNode, SimpleModuleNode, Node, SourceNode, FunctionNode
