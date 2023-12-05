from grapycal.utils.nodeGen import MoudleNodeGenerator, FunctionNodeGenerator, ClassNodeGenerator
import requests

# requests_moudle = MoudleNodeGenerator(requests)
# requests_moudle.generate()



# globals().update(requests_moudle.node_types)
# 
# requests_get_node = FunctionNodeGenerator(requests.get)
# print(requests_get_node.node_types)
# globals().update(requests_get_node.node_types)
requests_get_node = FunctionNodeGenerator(requests.get)
requests_get_node.generate()
globals().update(requests_get_node.node_types)

import time
time_time_node = FunctionNodeGenerator(time.time)
time_time_node.generate()
globals().update(time_time_node.node_types)

time_sleep_node = FunctionNodeGenerator(time.sleep)
time_sleep_node.generate()
globals().update(time_sleep_node.node_types)

print_node = FunctionNodeGenerator(print)
print_node.generate()
globals().update(print_node.node_types)

import datetime

datetime_datetime_node = ClassNodeGenerator(datetime.datetime)
datetime_datetime_node.generate()
globals().update(datetime_datetime_node.node_types)