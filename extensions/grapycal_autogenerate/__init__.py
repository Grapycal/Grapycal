from grapycal.utils.nodeGen import NoBuilitinFuncionGenerator, ModuleNodeGenerator, FunctionNodeGenerator, ClassNodeGenerator
import requests
import json
import requests
import bs4
import io
from io import BytesIO
import PIL
import numpy
from PIL import Image

request_module_node = ModuleNodeGenerator(requests)
request_module_node.generate()
globals().update(request_module_node.node_types)
json_module_node = ModuleNodeGenerator(json)
json_module_node.generate()
globals().update(json_module_node.node_types)
bs4_module_node = ModuleNodeGenerator(bs4)
bs4_module_node.generate()
globals().update(bs4_module_node.node_types)
beautifulsoup_node = ClassNodeGenerator(bs4.BeautifulSoup)
beautifulsoup_node.generate()
globals().update(beautifulsoup_node.node_types)
BytesIO_node = ClassNodeGenerator(BytesIO, special=True)
BytesIO_node.generate()
globals().update(BytesIO_node.node_types)
Image_node = ModuleNodeGenerator(Image)
Image_node.generate()
globals().update(Image_node.node_types)
numpy_module_node = ModuleNodeGenerator(numpy)
numpy_module_node.generate()
globals().update(numpy_module_node.node_types)
numpy_array_node = FunctionNodeGenerator(numpy.array)
numpy_array_node.generate()
globals().update(numpy_array_node.node_types)