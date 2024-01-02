from typing import Any
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort, Port
from objectsync import SObject, StringTopic, ObjTopic, IntTopic, DictTopic
class DVfunctionNode(Node):
    inputs = []
    max_in_degree = []
    outputs = []
    display_port_names = True
    default_value: list[dict] = []
    default_only: bool = False
    _default_value: list[str] = []
    def build_node(self):
        _key_options = []
        _value_options = []
        _default_value = []
        for dict_ in self.default_value:
            _key_options.extend(dict_.keys())
            _value_options.extend(dict_.values())
        self.inputs_attribute = self.add_attribute(
            'inputs_attribute', DictTopic, {}, 
            editor_type='dict',
            key_options=_key_options,value_options=_value_options,
            key_strict=self.default_only) # internal use only. data: {'name':str,'type':str}
        self._max_in_degree = self.max_in_degree[:]
        while len(self._max_in_degree) < len(self.inputs):
            self._max_in_degree.append(None)
        for i in range(len(self._max_in_degree)):
            if self._max_in_degree[i] is None:
                self._max_in_degree[i] = 1024
        for name, max_edges in zip(self.inputs,self._max_in_degree): #type: ignore
            display_name = name if self.display_port_names else ''
            self.add_in_port(name,max_edges,display_name=display_name)
        for name in self.outputs:
            display_name = name if self.display_port_names else ''
            self.add_out_port(name,display_name=display_name)

        self.label.set('f')
        self.shape.set('round')

    def init_node(self):
        self.inputs_attribute.on_add.add_auto(self.on_inputs_attribute_add)
        self.inputs_attribute.on_remove.add_auto(self.on_inputs_attribute_remove)

    def on_inputs_attribute_add(self, topic_name, _):
        self._default_value.append(topic_name)
        self.add_in_port(topic_name)
    
    def on_inputs_attribute_remove(self, topic_name):
        self._default_value.remove(topic_name)
        self.remove_in_port(topic_name)

    def check_ready(self):
        for port in self.in_ports:
            if port.edges:
                if not port.is_all_edge_ready():
                    return False
            else:
                if not port.get_name() in self._default_value:
                    return False
        return True

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_attributes('inputs_attribute')

    def edge_activated(self, edge: Edge, port):
        if not self.check_ready():
            return
        self.run(self.task)

    def task(self):
        if self.is_destroyed():
            return
        inputs = {}
        for port in self.in_ports:
            if port.max_edges.get() == 1:
                inputs[port.get_name()] = port.edges[0].get_data()
            else:
                inputs[port.get_name()] = [edge.get_data() for edge in port.edges]
        for key, value in self.inputs_attribute.get().items():
            if self.get_in_port(key).edges:
                continue
            inputs.update({key:eval(value)})
        result = self.calculate(**inputs)

        if result is None:
            return

        if len(self.out_ports) == 1:
            self.out_ports[0].push_data(result)
        else:
            for k,v in result.items():
                self.get_out_port(k).push_data(v)

    def calculate(self, **inputs)->Any:
        '''
        Define the function of this node here.

        :param **inputs: A dict of lists. Each dict entry is the data from one input port. For example, if there is only one input port named "in" with two\
            edges connected, the value of inputs will be `{'in':[data_from_edge_1, data_from_edge_2]}`.
        :return: A list of outputs. Each entry in the list will be pushed to one output port. For example, if there is only one output port,\
            the value of the return suold be `[data_to_port]`. If there are multiple edges connected to one output port,\
            they will all receive the same data.

        Examples::

            class SumNode(FunctionNode):
                inputs = ['items']
                outputs = ['sum']
                ...
                def calculate(self, items):
                    return {'sum':sum(items)} # Return the sum of the data
        '''
        raise NotImplementedError

    def input_edge_added(self, edge: Edge, port):
        if not self.check_ready():
            return
        self.run(self.task)

    def input_edge_removed(self, edge: Edge, port):
        if not self.check_ready():
            return
        self.run(self.task)

    def remove(self):
        return super().remove()