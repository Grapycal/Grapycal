from contextlib import contextmanager
import io
from typing import TYPE_CHECKING, Any, Dict, List
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.utils.io import OutputStream
from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic, GenericTopic, FloatTopic
from objectsync.sobject import SObjectSerialized

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
        self.output = self.add_attribute('output', StringTopic, 'output') # , is_stateful=False
        self.label = self.add_attribute('label', StringTopic, '')
        self.label_offset = self.add_attribute('label_offset', FloatTopic, 0)
        self.translation = self.add_attribute('translation', StringTopic)
        self.is_preview = self.add_attribute('is_preview', IntTopic, 1 if is_preview else 0)
        self.category_ = self.add_attribute('category', StringTopic, self.category)

        self.in_ports:ObjListTopic[InputPort] = self.add_attribute('in_ports', ObjListTopic)
        self.out_ports:ObjListTopic[OutputPort] = self.add_attribute('out_ports', ObjListTopic)

        self.on('double_click', self.double_click, is_stateful=False)
        self.on('spawn', self._spawn , is_stateful=False)

        self._output_stream = OutputStream(lambda out: self.output.set(self.output.get()+out))
        self.workspace.get_communication_event_loop().create_task(self._output_stream.run())

    def build(self):
        print(f'Building {self}')
        pass

    def post_build(self):
        pass

    def _spawn(self, client_id, translation):
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

    def destroy(self) -> SObjectSerialized:
        self._output_stream.close()
        return super().destroy()

    def add_in_port(self,name,max_edges=64):
        port = self.add_child(InputPort,name=name,max_edges=max_edges)
        self.in_ports.insert(port)
        return port

    def add_out_port(self,name,max_edges=64):
        port = self.add_child(OutputPort,name=name,max_edges=max_edges)
        port.node = self
        self.out_ports.insert(port)
        return port

    '''
    Run tasks in the background or foreground, redirecting stdout to the node's output stream.
    '''

    @contextmanager
    def redirect_output(self):
        '''
        Returns a context manager that redirects stdout to the node's output stream.
        '''
        redirect_ = self.workspace.redirect(self._output_stream)
        try:
            self._output_stream.enable_flush()
            redirect_.__enter__()
            yield
        finally:
            redirect_.__exit__(None, None, None)
            self._output_stream.disable_flush()

    def run_in_background(self,task):
        '''
        Run a task in the background thread.
        '''
        def task_wrapper():
            with self.redirect_output():
                task()
        self.workspace._background_runner.push(task_wrapper)

    def run_in_foreground(self,task):
        '''
        Run a task in the foreground thread.
        '''
        with self.redirect_output():
            task()

    '''
    User defined callbacks
    '''
    
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