from grapycal.utils.nodeGen import NoBuilitinFuncionGenerator
import requests
import json

json_load_node = NoBuilitinFuncionGenerator(json.loads)
json_loads_node = NoBuilitinFuncionGenerator(json.loads)

json_load_node.generate()
json_loads_node.generate()

globals().update(json_load_node.node_types) 

