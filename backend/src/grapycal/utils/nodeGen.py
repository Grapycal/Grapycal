from grapycal import FunctionNode
import inspect
import re

class MoudleNodeGenerator():
    def __init__(self, cls, func_name = None):
        self.cls = cls
        self.class_name = cls.__name__
        self.category = '{}'.format(self.class_name)
        self.node_types = {}

    
    def generate(self):
        all_functions = dir(self.cls)
        filtered_functions = [func for func in all_functions if re.match(r'^[^_].*(?<![\\_]{2})$', func) and callable(getattr(self.cls, func))]
        for func in filtered_functions:
            if func in ['globals', 'hasattr', 'hash', 'help']:
                continue
            try:
                print('Generating node for function: {}'.format(func))
                print(self.cls)
                try:
                    _func_implement = getattr(self.cls, func)
                except:
                    continue
                self._node_class_generator(_func_implement)
                print('Generated node for function: {}'.format(func))
            except Exception as e:
                print('Failed to generate node for function: {}, Error => {}'.format(func, e))
        
    def _node_class_generator(
        self,
        func,
        in_ports = ['*args', '**kwargs'],
        out_ports = ['return'],
        shape = 'simple',
        css_classes = ['fit-content'],
    ):
        unsuport_built_in_function = False
        unsuport_built_in_function_name = False
        required_params = []     
        try:
            signature = inspect.signature(func)
            params_values = signature.parameters.values()
        except:
            unsuport_built_in_function = True
        
        try:
            func.__name__
        except:
            unsuport_built_in_function_name = True

        if unsuport_built_in_function_name:
            return

        # if not params_values:
        #     return
        class _Node(FunctionNode):
            category = self.category
            if unsuport_built_in_function:
                inputs = ['*args', '**kwargs']
            elif in_ports != ['*args', '**kwargs']:
                inputs = in_ports
            else:
                for param in params_values:
                    if param.default == inspect.Parameter.empty:
                        if param.kind == inspect.Parameter.VAR_POSITIONAL:
                            required_params.append('*' + param.name)
                        elif param.kind == inspect.Parameter.VAR_KEYWORD:
                            required_params.append('**' + param.name)
                        else:
                            required_params.append(param.name)
                inputs = required_params
            max_in_degree = [1] * len(inputs)
            outputs = out_ports
            display_port_names = True

            def build_node(self):
                super().build_node()
                self.label.set(func.__name__)
                self.shape.set(shape)
                self.__doc__ = func.__doc__ or 'Sorry, no docstring for this function.'
                for css_class in css_classes:
                    self.css_classes.append(css_class)

            def calculate(self, **kwargs):
                kwargs_key = None
                args_key = None
                print(kwargs)
                for key, value in kwargs.items():
                    if '**' in key:
                        kwargs_in_kwargs = value
                        kwargs_key = key
                    elif '*' in key:
                        args_in_kwargs = value
                        args_key = key
                    else:
                        kwargs_in_kwargs = {}
                        args_in_kwargs = []
                if kwargs_key:
                    del kwargs[kwargs_key]
                if args_key:
                    del kwargs[args_key]
                return func(*args_in_kwargs, **kwargs, **kwargs_in_kwargs)
            
        _Node.__name__ = func.__name__ + 'Node'
        # globals()[func.__name__] = _Node
        self.node_types[func.__name__] = _Node