from grapycal.utils.nodeGen import NoBuilitinFuncionGenerator, ModuleNodeGenerator, FunctionNodeGenerator, ClassNodeGenerator
# import requests
# import json
# import requests
# import bs4
# import io
# from io import BytesIO
# import PIL
# import numpy
# from PIL import Image
# import openai

# request_module_node = ModuleNodeGenerator(requests)
# request_module_node.generate()
# globals().update(request_module_node.node_types)
# json_module_node = ModuleNodeGenerator(json)
# json_module_node.generate()
# globals().update(json_module_node.node_types)
# bs4_module_node = ModuleNodeGenerator(bs4)
# bs4_module_node.generate()
# globals().update(bs4_module_node.node_types)
# beautifulsoup_node = ClassNodeGenerator(bs4.BeautifulSoup)
# beautifulsoup_node.generate()
# globals().update(beautifulsoup_node.node_types)
# BytesIO_node = ClassNodeGenerator(BytesIO, special=True)
# BytesIO_node.generate()
# globals().update(BytesIO_node.node_types)
# Image_node = ModuleNodeGenerator(Image)
# Image_node.generate()
# globals().update(Image_node.node_types)
# numpy_module_node = ModuleNodeGenerator(numpy)
# numpy_module_node.generate()
# globals().update(numpy_module_node.node_types)
# numpy_array_node = FunctionNodeGenerator(numpy.array)
# numpy_array_node.generate()
# globals().update(numpy_array_node.node_types)
# # opai_node = ModuleNodeGenerator(openai)
# openai_node = ClassNodeGenerator(openai.OpenAI, special=True)
# openai_node.generate()
# globals().update(openai_node.node_types)

# from qiskit import QuantumRegister, QuantumCircuit, Aer, execute
# quantumregister = ClassNodeGenerator(QuantumCircuit)
# quantumregister.generate()
# globals().update(quantumregister.node_types)

# # print(type(Aer))
# from qiskit import transpile
# simulator = Aer.get_backend('aer_simulator')
# simulator.__name__ = 'AerSimulator'
# # print(type(simulator))
# AerSimulator_node = ClassNodeGenerator(simulator)
# AerSimulator_node.generate()
# globals().update(AerSimulator_node.node_types)

# transpile_node = FunctionNodeGenerator(transpile)
# transpile_node.generate()
# globals().update(transpile_node.node_types)


# from qiskit.visualization import plot_histogram
# plot_histogram