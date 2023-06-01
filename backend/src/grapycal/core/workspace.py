import inspect
import threading
import time
from typing import Any, Callable, Dict
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.sobjects.sidebar import Sidebar
import objectsync
import asyncio
import signal

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

from grapycal import builtin_nodes

class Workspace:
    def __init__(self, port, host) -> None:

        self._background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port,host,prebuild_kwargs={'workspace':self})

        self._objectsync.register(Sidebar)

        self.sidebar = self._objectsync.create_object(Sidebar)


        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)

        '''
        Register all node types here
        '''
        self.import_nodes_from_module(builtin_nodes)

        '''
        Create some nodes
        '''

    def communication_thread(self):
        asyncio.run(self._objectsync.serve())

    def run(self) -> None:
        print('Workspace running')
        t = threading.Thread(target=self.communication_thread,daemon=True) # daemon=True until we have a proper exit strategy
        t.start()

        signal.signal(signal.SIGTERM, lambda sig, frame: self.exit()) #? Why this does not work?
    
        self._background_runner.run()

    def exit(self):
        print('exit')
        self._background_runner.exit()

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