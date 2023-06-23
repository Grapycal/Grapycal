from contextlib import contextmanager
import traceback
from typing import TYPE_CHECKING, Any, Dict, List
from grapycal.core.stdout_helper import orig_print
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

    def pre_build(self, attribute_values: Dict[str, Any] | None, workspace:'Workspace', is_preview:bool = False):
        self.workspace = workspace
        
        self.use_transform = self.add_attribute('use_transform', GenericTopic[bool], not isinstance(self.get_parent(), Node))
        self.display_ports = self.add_attribute('display_ports', GenericTopic[bool], not isinstance(self.get_parent(), Node))

        self.shape = self.add_attribute('shape', StringTopic, 'block') # round, block, blockNamed, hideBody
        self.output = self.add_attribute('output', StringTopic, '', is_stateful=False)
        self.label = self.add_attribute('label', StringTopic, '', is_stateful=False)
        self.label_offset = self.add_attribute('label_offset', FloatTopic, 0)
        self.translation = self.add_attribute('translation', StringTopic)
        self.is_preview = self.add_attribute('is_preview', IntTopic, 1 if is_preview else 0)
        self.category_ = self.add_attribute('category', StringTopic, self.category)

        self.in_ports:ObjListTopic[InputPort] = self.add_attribute('in_ports', ObjListTopic)
        self.out_ports:ObjListTopic[OutputPort] = self.add_attribute('out_ports', ObjListTopic)

        self.on('double_click', self.double_click, is_stateful=False)
        self.on('spawn', self._spawn , is_stateful=False)

        def print_output(data):
            self.output.set(self.output.get()+data) #TODO: optimize
        self._output_stream = OutputStream(print_output)
        self.workspace.get_communication_event_loop().create_task(self._output_stream.run())

    def build(self):
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
        #TODO: Remove all edges connected to this node

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

    #TODO: this records output from chatroom and objectsync too. Fix that.
    @contextmanager
    def redirect_output(self):
        '''
        Returns a context manager that redirects stdout to the node's output stream.
        '''
        from grapycal.core.stdout_helper import orig_print

        try:
            self._output_stream.enable_flush()
            with self.workspace.redirect(self._output_stream):
                yield
        finally:
            self._output_stream.disable_flush()

    def run_in_background(self,task):
        '''
        Run a task in the background thread.
        '''
        from grapycal.core.stdout_helper import orig_print
        def task_wrapper():
            self.workspace.background_runner.set_exception_callback(self._on_exception)
            with self.redirect_output():
                task()

        self.workspace.background_runner.push(task_wrapper)

    def run_in_foreground(self,task,run_after_transition=True):
        '''
        Run a task in the foreground thread.
        '''
        #TODO: run_after_transition
        if run_after_transition:
            def task_wrapper():
                try:
                    with self.redirect_output():
                        task()
                except Exception as e:
                    self._on_exception(e)
            self.workspace.do_after_transition(task_wrapper)
        else:
            try:
                with self.redirect_output():
                    task()
            except Exception as e:
                self._on_exception(e)

    def _on_exception(self, e):
        #TODO: Create error topic
        from grapycal.core.stdout_helper import orig_print
        orig_print('got error\n', traceback.format_exc(),'\n',''.join(traceback.format_stack()))

    '''
    User defined callbacks
    '''
    
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