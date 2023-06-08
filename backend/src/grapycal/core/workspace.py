
from grapycal.utils.logging import setup_logging
logger = setup_logging()

from typing import Any, Callable, Dict

import inspect
import threading
import objectsync
import asyncio
import signal

from . import stdout_helper

from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.sobjects.sidebar import Sidebar

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

from grapycal import builtin_nodes

class Workspace:
    def __init__(self, port, host) -> None:
        
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

        self._objectsync.register(Sidebar)
        self.sidebar = self._objectsync.create_object(Sidebar)
        
        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)
        
        '''
        Register all built-in node types
        '''
        self.import_nodes_from_module(builtin_nodes)


        signal.signal(signal.SIGTERM, lambda sig, frame: self.exit()) #? Why this does not work?
    
        self.background_runner.run()

    def exit(self):
        print('exit')
        self.background_runner.exit()

    def get_communication_event_loop(self) -> asyncio.AbstractEventLoop:
        assert self._communication_event_loop is not None
        return self._communication_event_loop

    def register_node_type(self, node_type: type[Node]):
        self._objectsync.register(node_type)
        if not node_type.category == 'hidden':
            self._objectsync.create_object(node_type,parent_id=self.sidebar.get_id(),is_preview=True)

    def import_nodes_from_module(self, module):
        added_node_types = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Node) and obj != Node:
                self._objectsync.register(obj)
                added_node_types.append(obj)
                
        for node_type in added_node_types:
            if not node_type.category == 'hidden':
                self._objectsync.create_object(node_type,parent_id=self.sidebar.get_id(),is_preview=True)

    def create_node(self, node_type: type, **kwargs) -> Node:
        return self._objectsync.create_object(node_type, parent_id='root', is_preview=False, **kwargs)
    
    def create_edge(self, tail: OutputPort, head: InputPort) -> Edge:
        return self._objectsync.create_object(Edge, parent_id='root', is_preview=False, tail=tail, head=head)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--host', type=str, default='localhost')
    args = parser.parse_args()

    workspace = Workspace(args.port,args.host)
    workspace.run()