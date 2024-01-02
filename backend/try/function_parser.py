import json
import inspect

normal_funcion = json.loads

from typing import Callable, Any

def function_analyzer(func: Callable) -> list:
    signature = inspect.signature(func)
    parameters = signature.parameters
    
    analyzed_params = []
    
    for param_name, param in parameters.items():
        param_info = {'name': param_name, 'required': param.default == inspect.Parameter.empty}
        if param.default != inspect.Parameter.empty:
            param_info['default'] = param.default
        analyzed_params.append(param_info)
    
    return analyzed_params

result = function_analyzer(normal_funcion)
print(result)