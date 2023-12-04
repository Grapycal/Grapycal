from grapycal.utils.nodeGen import MoudleNodeGenerator
import requests

requests_moudle = MoudleNodeGenerator(requests)
requests_moudle.generate()

globals().update(requests_moudle.node_types)