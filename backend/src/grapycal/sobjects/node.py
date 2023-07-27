from contextlib import contextmanager
import traceback
from typing import TYPE_CHECKING, Any, Callable, Dict, List, TypeVar
from grapycal.core.stdout_helper import orig_print
from grapycal.sobjects.controls.control import Control
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.utils.io import OutputStream
from grapycal.utils.misc import as_type
from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic, GenericTopic, FloatTopic, Topic
from objectsync.sobject import SObjectSerialized, WrappedTopic

if TYPE_CHECKING:
    from grapycal.core.workspace import Workspace
    
class Node(SObject):
    frontend_type = 'Node'
    category = 'hidden'

    def build(self,is_preview=False,**build_node_args):
        
        self.shape = self.add_attribute('shape', StringTopic, 'normal') # normal, simple, round
        self.shape.add_validator(lambda _,x,__: x in ['normal', 'simple', 'round'])
        self.output = self.add_attribute('output', ListTopic, [], is_stateful=False)
        self.label = self.add_attribute('label', StringTopic, 'Node', is_stateful=False)
        self.label_offset = self.add_attribute('label_offset', FloatTopic, 0)
        self.translation = self.add_attribute('translation', StringTopic)
        self.is_preview = self.add_attribute('is_preview', IntTopic, 1 if is_preview else 0)
        self.category_ = self.add_attribute('category', StringTopic, self.category)
        self.exposed_attributes = self.add_attribute('exposed_attributes', ListTopic, [])

        # for inspector
        self.type_topic = self.add_attribute('type', StringTopic, self.get_type_name())

        self.in_ports:ObjListTopic[InputPort] = self.add_attribute('in_ports', ObjListTopic)
        self.out_ports:ObjListTopic[OutputPort] = self.add_attribute('out_ports', ObjListTopic)

        self.controls:ObjListTopic[Control] = self.add_attribute('controls', ObjListTopic)

        '''
        Let user override build_node method instead of build method so that they don't have to call super().build(args) in their build method.
        '''
        self.build_node(**build_node_args)

    def build_node(self):
        '''
        Create attributes, ports, and controls here.
        
        Note: 
            This method will not be called when the object is being restored. The child objects will be restored automatically instead of
        running this method again.
        '''

    def init(self):
        '''
        This method is called after the node is built and its ports and controls are created. Use this method if you want to do something after
        the node is built.
        '''
        self.workspace:Workspace = self._server.globals.workspace
        
        from grapycal.sobjects.editor import Editor # import here to avoid circular import
        parent = self.get_parent()
        if isinstance(parent, Editor):
            self.editor = parent
        else:
            self.editor = None

        self.on('double_click', self.double_click, is_stateful=False)
        self.on('spawn', self._spawn , is_stateful=False)

        def print_output(data):
            self.output.insert(['output',data])

        self._output_stream = OutputStream(print_output)
        self._output_stream.set_event_loop(self.workspace.get_communication_event_loop())
        self.workspace.get_communication_event_loop().create_task(self._output_stream.run())

    def _spawn(self, client_id, translation):
        '''
        Called when a client wants to spawn a node.
        '''
        new_node = self.workspace.get_workspace_object().main_editor.get().create_node(type(self))
        new_node.add_tag(f'spawned_by_{client_id}') # So the client can find the node it spawned and make it follow the mouse
        new_node.translation.set(translation)

    def destroy(self) -> SObjectSerialized:
        '''
        Called when the node is destroyed. You can override this method to do something before the node is destroyed.
        Overrided methods should call return super().destroy() at the end.
        '''
        #TODO: Remove all edges connected to this node

        self._output_stream.close()
        return super().destroy()

    def add_in_port(self,name:str,max_edges=64,display_name=None):
        '''
        Add an input port to the node.
        '''
        port = self.add_child(InputPort,name=name,max_edges=max_edges,display_name=display_name)
        self.in_ports.insert(port)
        return port

    def add_out_port(self,name:str,max_edges=64,display_name=None):
        '''
        Add an output port to the node.
        '''
        port = self.add_child(OutputPort,name=name,max_edges=max_edges,display_name=display_name)
        self.out_ports.insert(port)
        return port
    
    T = TypeVar('T', bound=Control)
    def add_control(self,control_type:type[T],**kwargs) -> T:
        '''
        Add a control to the node.
        '''
        control = self.add_child(control_type,**kwargs)
        self.controls.insert(control)
        return control
    
    # Wrap the SObject.addattribute() to make shorthand of exposing attributes after adding them.
    T1 = TypeVar("T1", bound=Topic|WrappedTopic)
    def add_attribute(
        self, topic_name:str, topic_type: type[T1], init_value=None, is_stateful=True,
        editor_type:str|None=None, editor_args:dict|None=None, display_name:str|None=None
        ) -> T1: 
        
        attribute = super().add_attribute(topic_name, topic_type, init_value, is_stateful)
        if editor_type is not None:
            assert not isinstance(attribute, WrappedTopic), 'Cannot expose a wrapped topic'
            self.expose_attribute(attribute,editor_type,editor_args,display_name)
        return attribute
    
    def expose_attribute(self,attribute:Topic,editor_type,editor_args=None,display_name=None):
        '''
        Expose an attribute to the editor.
        Args:
            - attribute: The attribute to expose.

            - editor_type: The type of the editor to use. Can be ``text`` or ``list``.

        '''
        if editor_args is None:
            editor_args = {}
        name = attribute.get_name()
        if display_name is None:
            display_name = name.split('/')[-1]
        editor_args['type'] = editor_type
        self.exposed_attributes.insert({
            'name':name,
            'display_name':display_name,
            'editor_args':editor_args
        })

    '''
    Run tasks in the background or foreground, redirecting stdout to the node's output stream.
    '''

    @contextmanager
    def _redirect_output(self):
        '''
        Returns a context manager that redirects stdout to the node's output stream.
        '''

        try:
            self._output_stream.enable_flush()
            with self.workspace.redirect(self._output_stream):
                yield
        finally:
            self._output_stream.disable_flush()

    def _run_in_background(self,task:Callable[[],None],to_queue=True):
        '''
        Run a task in the background thread.
        '''
        def task_wrapper():
            self.workspace.background_runner.set_exception_callback(self._on_exception)
            with self._redirect_output():
                task()

        self.workspace.background_runner.push(task_wrapper,to_queue=to_queue)
        
    def _run_directly(self,task:Callable[[],None]):
        '''
        Run a task in the current thread.
        '''
        try:
            with self._redirect_output():
                task()
        except Exception as e:
            self._on_exception(e)

    def run(self,task:Callable[[],None],background=True,to_queue=True):
        '''
        Run a task in the node's context i.e. the stdout and errors will be redirected to the node's output attribute and be displayed in front-end.

        Args:
            - task: The task to run.

            - background: If set to True, the task will be scheduled to run in the background thread. Otherwise, it will be run in the current thread immediately.
            
            - to_queue: This argument is used only when `background` is True. If set to True, the task will be pushed to the :class:`.BackgroundRunner`'s queue.\
            If set to False, the task will be pushed to its stack. See :class:`.BackgroundRunner` for more details.
        '''
        if background:
            self._run_in_background(task,to_queue)
        else:
            self._run_directly(task)

    def _on_exception(self, e):
        message = ''.join(traceback.format_exc())
        self.output.insert(['error',message])

    '''
    Node events
    '''
    
    def edge_activated(self, edge:Edge, port:InputPort):
        '''
        Called when an edge on an input port is activated.
        '''
        pass

    def input_edge_added(self, edge:Edge, port:InputPort):
        '''
        Called when an edge is added to an input port.
        '''
        pass

    def input_edge_removed(self, edge:Edge, port:InputPort):
        '''
        Called when an edge is removed from an input port.
        '''
        pass

    def output_edge_added(self, edge:Edge, port:OutputPort):
        '''
        Called when an edge is added to an output port.
        '''
        pass

    def output_edge_removed(self, edge:Edge, port:OutputPort):
        '''
        Called when an edge is removed from an output port.
        '''
        pass

    def double_click(self):
        '''
        Called when the node is double clicked by an user.
        '''
        pass