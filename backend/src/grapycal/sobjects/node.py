from typing import TYPE_CHECKING, Any, Dict, List
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic, GenericTopic, FloatTopic

if TYPE_CHECKING:
    from grapycal.core.workspace import Workspace
    
class Node(SObject):
    frontend_type = 'Node'
    category = 'hidden'
    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace:'Workspace', is_preview:bool = False, display_ports:bool = True):
        self.workspace = workspace
        
        self.use_transform = self.add_attribute('use_transform', GenericTopic[bool], not isinstance(self.get_parent(), Node))
        self.display_ports = self.add_attribute('display_ports', GenericTopic[bool], not isinstance(self.get_parent(), Node))

        self.shape = self.add_attribute('shape', StringTopic, 'block') # round, block, blockNamed, hideBody
        self.output = self.add_attribute('output', StringTopic, 'output')
        self.label = self.add_attribute('label', StringTopic, '')
        self.label_offset = self.add_attribute('label_offset', FloatTopic, 0)
        self.translation = self.add_attribute('translation', StringTopic)
        self.is_preview = self.add_attribute('is_preview', IntTopic, 1 if is_preview else 0)
        self.category_ = self.add_attribute('category', StringTopic, self.category)

        self.in_ports:ObjListTopic[InputPort] = self.add_attribute('in_ports', ObjListTopic)
        self.out_ports:ObjListTopic[OutputPort] = self.add_attribute('out_ports', ObjListTopic)

        self.on('double_click', self.double_click, is_stateful=False)
        self.on('spawn', self.spawn , is_stateful=False)

    def build(self):
        print(f'Building {self}')
        pass

    def post_build(self):
        pass

    def spawn(self, client_id, translation):
        new_node = self.workspace.create_node(type(self))
        new_node.add_tag(f'spawned_by_{client_id}')
        new_node.translation.set(translation)

    def _on_parent_changed(self, old_parent_id, new_parent_id):
        super()._on_parent_changed(old_parent_id, new_parent_id)
        if isinstance(self.get_parent(), Node):
            self.use_transform.set(False)
            self.display_ports.set(False)
        else:
            self.use_transform.set(True)
            self.display_ports.set(True)

    def add_in_port(self,name,max_edges=64):
        port = self.add_child(InputPort,name=name,max_edges=max_edges)
        self.in_ports.insert(port)
        return port

    def add_out_port(self,name,max_edges=64):
        port = self.add_child(OutputPort,name=name,max_edges=max_edges)
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