import threading
import time
from typing import Any, Callable, Dict
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.nodes.additionNode import AdditionNode
from grapycal.sobjects.nodes.printNode import PrintNode
from grapycal.sobjects.nodes.textInputNode import TextInputNode
from grapycal.sobjects.port import InputPort, OutputPort
from grapycal.sobjects.nodes.textOutputNode import TextOutputNode
from grapycal.sobjects.sidebar import Sidebar
import objectsync
import asyncio
import signal

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

class Workspace:
    def __init__(self, port, host) -> None:

        self._background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port,host,prebuild_kwargs={'workspace':self})

        self._objectsync.register(Sidebar)

        self._objectsync.register(AdditionNode)
        self._objectsync.register(TextOutputNode)
        self._objectsync.register(PrintNode)
        self._objectsync.register(TextInputNode)
        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)

        self._objectsync.create_object(Sidebar)

        self._objectsync.create_object(TextInputNode)
        self._objectsync.create_object(TextInputNode)
        self._objectsync.create_object(TextInputNode)
        self._objectsync.create_object(PrintNode)
        self._objectsync.create_object(PrintNode)
        self._objectsync.create_object(PrintNode)
        self._objectsync.create_object(AdditionNode)
        self._objectsync.create_object(AdditionNode)
        self._objectsync.create_object(AdditionNode)

    def communication_thread(self):
        asyncio.run(self._objectsync.serve())

    def run(self) -> None:
        # while(True):
        #     import time
        #     time.sleep(1)
        #     print('workspace running')
        print('Workspace running')
        t = threading.Thread(target=self.communication_thread,daemon=True) # daemon=True until we have a proper exit strategy
        t.start()

        signal.signal(signal.SIGTERM, lambda sig, frame: self.exit()) #? Why this does not work?
    
        self._background_runner.run()

    def exit(self):
        print('exit')
        self._background_runner.exit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--host', type=str, default='localhost')
    args = parser.parse_args()

    workspace = Workspace(args.port,args.host)
    workspace.run()