from typing import Any, Dict, List
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic
class Node(SObject):
    frontend_type = 'Node'
    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace):
        super().pre_build(attribute_values)

        self.workspace = workspace
        
        self.shape = self.add_attribute('shape', StringTopic, 'block') # round, block, blockNamed, hideBody
        self.output = self.add_attribute('output', StringTopic, 'output')
        self.label = self.add_attribute('label', StringTopic, 'label')
        self.translation = self.add_attribute('translation', StringTopic, '0,0')
        self.is_preview = self.add_attribute('is_preview', IntTopic, 0)

        self.in_ports = self.add_attribute('in_ports', ObjListTopic)
        self.out_ports = self.add_attribute('out_ports', ObjListTopic)

        self.on('double_click', self.double_click)

    def build(self):
        pass


    def post_build(self):
        pass

    def add_in_port(self,name):
        port = self.add_child(InputPort)
        port.name.set(name)
        port.node = self
        self.in_ports.insert(port)
        return port

    def add_out_port(self,name):
        port = self.add_child(OutputPort)
        port.name.set(name)
        port.node = self
        self.out_ports.insert(port)
        return port
    
    def activate(self):
        pass

    def edge_activated(self, edge:Edge):
        pass

    def input_edge_added(self, edge:Edge, port:InputPort):
        pass

    def input_edge_removed(self, edge:Edge, port:InputPort):
        pass

    def output_edge_added(self, edge:Edge, port:OutputPort):
        pass

    def output_edge_removed(self, edge:Edge, port:OutputPort):
        pass

    def double_click(self):
        pass