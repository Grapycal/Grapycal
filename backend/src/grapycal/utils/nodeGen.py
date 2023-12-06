from grapycal import FunctionNode
import inspect
import re
from typing import Any, Callable
from types import ModuleType

import requests
requests.get


def doc_prettify(doc: str) -> str:
    if doc is None:
        return ''
    doc = re.sub(r':(.*?):', r'**\1**', doc)
    doc = doc.replace("\*", "*")
    doc = doc.replace('\n', '<br>')
    doc = doc.replace('    ', '')
    doc = doc.replace('  ', '')
    doc = doc.replace('\t', '')
    return doc

import time
type(time)


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

class FunctionNodeGenerator():
    def __init__(self, func: Callable[..., Any], func_name: str | None = None, doc: str | None = None,
                 category: str | None = None, in_ports: list[str] | None = None,
                 out_ports: list[str] | None = None, max_in_degree: list[int] | None = None,
                 shape: str | None = None, css_classes: list[str] | None = None,
                 display_port_names: bool = True):
        self.func = func
        self.func_name = func_name
        self.doc = doc
        self.category = category
        self.in_ports = in_ports
        self.out_ports = out_ports
        self.max_in_degree = max_in_degree
        self.shape = shape
        self.css_classes = css_classes
        self.node_types = dict()
        self.display_port_names = display_port_names
        self.initial_values()

    def initial_values(self):
        if self.func_name is None:
            self.func_name = self.func.__name__
        if self.category is None:
            if self.func.__module__ == 'builtins':
                self.category = 'builtins/extentions/function'
            else:
                self.category = self.func.__module__
        if self.max_in_degree is None:
            self.max_in_degree = []
            _modify_max_in_degree = True
        else:
            _modify_max_in_degree = False
        if self.in_ports is None:
            self.in_ports = []
            try:
                signature = inspect.signature(self.func)
                params_values = signature.parameters.values()
                for param in params_values:
                    if param.default == inspect.Parameter.empty:
                        if param.kind == inspect.Parameter.VAR_POSITIONAL:
                            self.in_ports.append('*' + param.name)
                            if _modify_max_in_degree:
                                self.max_in_degree.append(64)
                        elif param.kind == inspect.Parameter.VAR_KEYWORD:
                            self.in_ports.append('**' + param.name)
                            if _modify_max_in_degree:
                                self.max_in_degree.append(1)
                        else:
                            self.in_ports.append(param.name)
                            if _modify_max_in_degree:
                                self.max_in_degree.append(1)
            except:
                self.in_ports = ['*args', '**kwargs']
                if _modify_max_in_degree:
                    self.max_in_degree = [64, 1]
        if self.out_ports is None:
            self.out_ports = ['return']
        if self.shape is None:
            self.shape = 'simple'
        if self.css_classes is None:
            self.css_classes = ['fit-content']
        if self.doc is None:
            self.doc = doc_prettify(self.func.__doc__) or 'Sorry, no docstring for this function.'
    def generate(self):
        _func = self.func
        _func_name = self.func_name
        _class_name = self.func_name + 'Node'
        _class_node_type_name = _class_name
        _doc = self.doc
        _category = self.category
        _in_ports = self.in_ports
        _max_in_degree = self.max_in_degree
        _out_ports = self.out_ports
        _shape = self.shape
        _css_classes = self.css_classes
        _display_port_names = self.display_port_names

        class _Node(FunctionNode):
            category = _category
            inputs = _in_ports
            outputs = _out_ports
            max_in_degree = _max_in_degree
            display_port_names = _display_port_names

            def build_node(self):
                super().build_node()
                self.label.set(_func_name)
                self.shape.set(_shape)
                for css_class in _css_classes:
                    self.css_classes.append(css_class)

            def calculate(self, **kwargs):
                kwargs_key = None
                args_key = None
                kwargs_in_kwargs = {}
                args_in_kwargs = []
                for key, value in kwargs.items():
                    if '**' in key:
                        kwargs_in_kwargs = value
                        kwargs_key = key
                    elif '*' in key:
                        args_in_kwargs = value
                        args_key = key
                    else:
                        pass
                if kwargs_key:
                    del kwargs[kwargs_key]
                if args_key:
                    del kwargs[args_key]

                return _func(*args_in_kwargs, **kwargs, **kwargs_in_kwargs)
            
        _Node.__name__ = _class_name
        _Node.__doc__ = _doc
        self.node_types[_class_node_type_name] = _Node

class ClassNodeGenerator():
    def __init__(self, cls: Callable[..., Any], cls_name: str | None = None, doc: str | None = None,
                 category: str | None = None, in_ports: list[str] | None = None,
                 out_ports: list[str] | None = None, max_in_degree: list[int] | None = None,
                 shape: str | None = None, css_classes: list[str] | None = None,
                 display_port_names: bool = True, special = False):
        self.cls = cls
        self.cls_name = cls_name
        self.doc = doc
        self.category = category
        self.in_ports = in_ports
        self.out_ports = out_ports
        self.max_in_degree = max_in_degree
        self.shape = shape
        self.css_classes = css_classes
        self.node_types = dict()
        self.display_port_names = display_port_names
        self.special = special
        self.initial_values()
    
    def initial_values(self):
        if self.cls_name is None:
            self.cls_name = self.cls.__name__
        if self.category is None:
            if self.cls.__module__ == 'builtins':
                self.category = 'builtins/extentions/class'
            else:
                self.category = self.cls.__module__
        if self.max_in_degree is None:
            self.max_in_degree = []
            _modify_max_in_degree = True
        else:
            _modify_max_in_degree = False
        if self.in_ports is None:
            self.in_ports = []
            try:
                signature = inspect.signature(self.cls)
                params_values = signature.parameters.values()
                print(params_values)
                for param in params_values:
                    if param.default == inspect.Parameter.empty:
                        if param.kind == inspect.Parameter.VAR_POSITIONAL:
                            self.in_ports.append('*' + param.name)
                            if _modify_max_in_degree:
                                self.max_in_degree.append(64)
                        elif param.kind == inspect.Parameter.VAR_KEYWORD:
                            self.in_ports.append('**' + param.name)
                            if _modify_max_in_degree:
                                self.max_in_degree.append(1)
                        else:
                            self.in_ports.append(param.name)
                            if _modify_max_in_degree:
                                self.max_in_degree.append(1)
                    else:
                        if self.special:
                            self.in_ports.append(param.name)
                            if _modify_max_in_degree:
                                self.max_in_degree.append(1)
                        
                    # else:
                    #     self.in_ports.append(param.name)
                    #     if _modify_max_in_degree:
                    #         self.max_in_degree.append(1)
                        # self.in_ports.append('*args')
                        # self.max_in_degree.append(64)
                        # self.in_ports.append('**kwargs')
                        # self.max_in_degree.append(1)
                        # break
            except:
                self.in_ports = ['*args', '**kwargs']
                if _modify_max_in_degree:
                    self.max_in_degree = [64, 1]
        if self.out_ports is None:
            self.out_ports = ['{}-object'.format(self.cls_name)]
        if self.shape is None:
            self.shape = 'simple'
        if self.css_classes is None:
            self.css_classes = ['fit-content']
        if self.doc is None:
            self.doc = doc_prettify(self.cls.__doc__) or 'Sorry, no docstring for this function.'
    def generate(self):
        _cls = self.cls
        _cls_name = self.cls_name
        _class_name = self.cls_name + 'Node'
        _class_node_type_name = _class_name
        _doc = self.doc
        _category = self.category
        _in_ports = self.in_ports
        _max_in_degree = self.max_in_degree
        _out_ports = self.out_ports
        _shape = self.shape
        _css_classes = self.css_classes
        _display_port_names = self.display_port_names

        class _Node(FunctionNode):
            category = _category
            inputs = _in_ports
            outputs = _out_ports
            max_in_degree = _max_in_degree
            display_port_names = _display_port_names

            def build_node(self):
                super().build_node()
                self.label.set(_cls_name)
                self.shape.set(_shape)
                for css_class in _css_classes:
                    self.css_classes.append(css_class)

            def calculate(self, **kwargs):
                kwargs_key = None
                args_key = None
                kwargs_in_kwargs = {}
                args_in_kwargs = []
                for key, value in kwargs.items():
                    if '**' in key:
                        kwargs_in_kwargs = value
                        kwargs_key = key
                    elif '*' in key:
                        args_in_kwargs = value
                        args_key = key
                    else:
                        pass
                if kwargs_key:
                    del kwargs[kwargs_key]
                if args_key:
                    del kwargs[args_key]

                return _cls(*args_in_kwargs, **kwargs, **kwargs_in_kwargs)
            
        _Node.__name__ = _class_name
        _Node.__doc__ = _doc
        self.node_types[_class_node_type_name] = _Node

class NoBuilitinFuncionGenerator:
    def __init__(self, func: Callable[..., Any], func_name: str | None = None, doc: str | None = None,
                 category: str | None = None, in_ports: list[str] | None = None,
                 out_ports: list[str] | None = None, max_in_degree: list[int] | None = None,
                 shape: str | None = None, css_classes: list[str] | None = None,
                 display_port_names: bool = True):
        
        # assert inspect.isbuiltin(func) == False, 'This function is a builtin function, please use FunctionNodeGenerator instead.'
        # assert inspect.isfunction(func) == True, 'This function is not a function, please use others NodeGenerator instead.'

        self.func = func
        self.func_name = func_name
        self.doc = doc
        self.category = category
        self.in_ports = in_ports
        self.out_ports = out_ports
        self.max_in_degree = max_in_degree
        self.shape = shape
        self.css_classes = css_classes
        self.node_types = dict()
        self.display_port_names = display_port_names
        self.initial_values()

    def initial_values(self):
        if self.func_name is None:
            self.func_name = self.func.__name__
        if self.category is None:
            self.category = self.func.__module__
        if self.max_in_degree is None:
            self.max_in_degree = []
            _modify_max_in_degree = True
        else:
            _modify_max_in_degree = False
        if self.in_ports is None:
            self.in_ports = []
            signature = inspect.signature(self.func)
            params_values = signature.parameters.values()
            for param in params_values:
                if param.default == inspect.Parameter.empty:
                    if param.kind == inspect.Parameter.VAR_POSITIONAL:
                        self.in_ports.append('*' + param.name)
                        if _modify_max_in_degree:
                            self.max_in_degree.append(64)
                    elif param.kind == inspect.Parameter.VAR_KEYWORD:
                        self.in_ports.append('**' + param.name)
                        if _modify_max_in_degree:
                            self.max_in_degree.append(1)
                    else:
                        self.in_ports.append(param.name)
                        if _modify_max_in_degree:
                            self.max_in_degree.append(1)
        if self.out_ports is None:
            self.out_ports = ['return']
        if self.shape is None:
            self.shape = 'simple'
        if self.css_classes is None:
            self.css_classes = ['fit-content']
        if self.doc is None:
            self.doc = doc_prettify(self.func.__doc__) or 'Sorry, no docstring for this function.'

    def generate(self):
        _func = self.func
        _func_name = self.func_name
        _class_name = self.func_name + 'Node'
        _class_node_type_name = _class_name
        _doc = self.doc
        _category = self.category
        _in_ports = self.in_ports
        _max_in_degree = self.max_in_degree
        _out_ports = self.out_ports
        _shape = self.shape
        _css_classes = self.css_classes
        _display_port_names = self.display_port_names

        class _Node(FunctionNode):
            category = _category
            inputs = _in_ports
            outputs = _out_ports
            max_in_degree = _max_in_degree
            display_port_names = _display_port_names

            def build_node(self):
                super().build_node()
                self.label.set(_func_name)
                self.shape.set(_shape)
                for css_class in _css_classes:
                    self.css_classes.append(css_class)

            def calculate(self, **kwargs):
                kwargs_key = None
                args_key = None
                kwargs_in_kwargs = {}
                args_in_kwargs = []
                for key, value in kwargs.items():
                    if '**' in key:
                        kwargs_in_kwargs = value
                        kwargs_key = key
                    elif '*' in key:
                        args_in_kwargs = value
                        args_key = key
                    else:
                        pass
                if kwargs_key:
                    del kwargs[kwargs_key]
                if args_key:
                    del kwargs[args_key]

                return _func(*args_in_kwargs, **kwargs, **kwargs_in_kwargs)
            
        _Node.__name__ = _class_name
        _Node.__doc__ = _doc
        self.node_types[_class_node_type_name] = _Node

class ModuleNodeGenerator(object):
    def __init__(self, module: ModuleType, routins: list[Any] | None = None, classes: list[Any] | None = None,
                 vars: list[Any] | None = None,
                 detect_private_function: bool | None = False, detect_reserved_function: bool | None = None,
                 detect_static_vars: bool | None = False, detect_private_vars: bool | None = None,
                 detect_reserved_vars: bool | None = False) -> None:
            self.module = module
            self.routins = routins
            self.classes = classes
            self.vars = vars
            self.detect_private_function = detect_private_function
            self.detect_reserved_function = detect_reserved_function
            self.detect_static_vars = detect_static_vars
            self.detect_private_vars = detect_private_vars
            self.detect_reserved_vars = detect_reserved_vars

            self.node_types = dict()

            self.detect_routuns_and_classes()

    def detect_routuns_and_classes(self):
        if self.routins is None:
            self.routins = []
            for _routins in inspect.getmembers(self.module, inspect.isroutine):
                if self.detect_private_function == False and _routins[0].startswith('_'):
                    continue
                if self.detect_reserved_function == False and _routins[0].startswith('__'):
                    continue
                self.routins.append(_routins)
        if self.classes is None:
            self.classes = []
            for _class in inspect.getmembers(self.module, inspect.isclass):
                if self.detect_private_function == False and _class[0].startswith('_'):
                    continue
                if self.detect_reserved_function == False and _class[0].startswith('__'):
                    continue
                self.classes.append(_class)
        if self.vars is None and self.detect_static_vars:
            self.vars = []
            for _vars in vars(self.module):
                if self.detect_static_vars == False and _vars.startswith('_'):
                    continue
                if self.detect_private_vars == False and _vars.startswith('__'):
                    continue
                self.vars.append(_vars)
            

    def generate(self):
        for _routin in self.routins:
            try:
                print('Generating node for function: {}'.format(_routin[0]))
                _func_node = NoBuilitinFuncionGenerator(_routin[1], _routin[0])
                _func_node.generate()
                self.node_types.update(_func_node.node_types)
                print('Generated node for function: {}'.format(_routin[0]))
            except Exception as e:
                print('Failed to generate node for function: {}'.format(_routin[0]))
                print('Error: {}'.format(e))
        for _class in self.classes:
            try:
                print('Generating node for class: {}'.format(_class[0]))
                _class_node = ClassNodeGenerator(_class[1], _class[0])
                _class_node.generate()
                self.node_types.update(_class_node.node_types)
                print('Generated node for class: {}'.format(_class[0]))
            except Exception as e:
                print('Failed to generate node for class: {}'.format(_class[0]))
                print('Error: {}'.format(e))
                
        # for _var in self.vars:
        #     _var_node = FunctionNodeGenerator(getattr(self.module, _var), _var)
        #     _var_node.generate()
        #     self.node_types.update(_var_node.node_types)