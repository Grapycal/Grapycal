
from grapycal.sobjects.workspaceObject import WorkspaceObject
from grapycal.utils.io import file_exists, json_read, json_write
from grapycal.utils.logging import setup_logging
logger = setup_logging()

from typing import Any, Callable, Dict

import inspect
import threading
import objectsync
from objectsync.sobject import SObjectSerialized
import asyncio
import signal
from dacite import from_dict


from . import stdout_helper


from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.sobjects.sidebar import Sidebar

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

from grapycal import builtin_nodes

class Workspace:
    def __init__(self, port, host, path) -> None:
        self.path = path
        '''
        Enable stdout proxy for this process
        '''
        stdout_helper.enable_proxy(redirect_error=False)
        self.redirect = stdout_helper.redirect

        self._communication_event_loop: asyncio.AbstractEventLoop | None = None

        self.background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port,host,prebuild_kwargs={'workspace':self})

        self.do_after_transition = self._objectsync.do_after_transition

    def _communication_thread(self,event_loop_set_event: threading.Event):
        asyncio.run(self._async_communication_thread(event_loop_set_event))

    async def _async_communication_thread(self,event_loop_set_event: threading.Event):
        self._communication_event_loop = asyncio.get_event_loop()
        event_loop_set_event.set()
        await self._objectsync.serve()

    def run(self) -> None:
        print('Workspace running')
        event_loop_set_event = threading.Event()
        t = threading.Thread(target=self._communication_thread,daemon=True,args=[event_loop_set_event]) # daemon=True until we have a proper exit strategy

        t.start()

        event_loop_set_event.wait()

        self._objectsync.register(WorkspaceObject)
        self._objectsync.register(Sidebar)
        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)
        
        '''
        Register all built-in node types
        '''

        signal.signal(signal.SIGTERM, lambda sig, frame: self.exit()) #? Why this does not work?

        if file_exists(self.path):
            self.load_workspace(self.path)
        else:
            self.initialize_workspace()
            self.import_nodes(builtin_nodes)
            
        self._objectsync.on('ctrl+s',lambda: self.save_workspace(self.path),is_stateful=False)
    
        self.background_runner.run()

    def exit(self):
        print('exit')
        self.background_runner.exit()

    def get_communication_event_loop(self) -> asyncio.AbstractEventLoop:
        assert self._communication_event_loop is not None
        return self._communication_event_loop

    def create_preview_nodes(self, module):
        node_types = self.get_node_types_from_module(module)
        for node_type in node_types:
            if not node_type.category == 'hidden':
                self._objectsync.create_object(node_type,parent_id=self._workspace_object.sidebar.get_id(),is_preview=True)

    def import_nodes(self, module):
        node_types = self.get_node_types_from_module(module)
        for node_type in node_types:
            self._objectsync.register(node_type)

    def get_node_types_from_module(self, module) -> list[type[Node]]:
        node_types: list[type[Node]] = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Node) and obj != Node:
                node_types.append(obj)
        return node_types

    def create_node(self, node_type: type, **kwargs) -> Node:
        return self._objectsync.create_object(node_type, parent_id=self._workspace_object.get_id(), is_preview=False, **kwargs)
    
    def create_edge(self, tail: OutputPort, head: InputPort) -> Edge:
        return self._objectsync.create_object(Edge, parent_id=self._workspace_object.get_id(), is_preview=False, tail=tail, head=head)
    
    '''
    Save and load
    '''

    def initialize_workspace(self) -> None:
        node_libraries_used = [builtin_nodes] #TODO: Load from workspace_serialized
        for node_library in node_libraries_used:
            self.import_nodes(node_library)
        self._workspace_object = self._objectsync.create_object(WorkspaceObject, parent_id='root', is_preview=False)
        for node_library in node_libraries_used:
            self.create_preview_nodes(node_library)

    def save_workspace(self, path: str) -> None:
        workspace_serialized = self._workspace_object.serialize()
        data = {
            'client_id_count': self._objectsync.get_client_id_count(),
            'id_count': self._objectsync.get_id_count(),
            'workspace_serialized': workspace_serialized.to_dict(),
        }
        json_write(path, data)

    def load_workspace(self, path: str) -> None:
        data = json_read(path)
        self._objectsync.set_client_id_count(data['client_id_count'])
        self._objectsync.set_id_count(data['id_count'])
        workspace_serialized = from_dict(SObjectSerialized,data['workspace_serialized'])
        node_libraries_used = [builtin_nodes] #TODO: Load from workspace_serialized
        for node_library in node_libraries_used:
            self.import_nodes(node_library)
        self._workspace_object = self._objectsync.create_object(WorkspaceObject, parent_id='root', is_preview=False, serialized=workspace_serialized)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--path', type=str, default='workspace.json')
    args = parser.parse_args()

    workspace = Workspace(args.port,args.host,args.path)
    workspace.run()