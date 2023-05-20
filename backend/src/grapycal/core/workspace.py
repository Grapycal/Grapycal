import threading
import time
from typing import Any, Callable, Dict
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
import objectsync
import asyncio
import signal

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

class Workspace:
    def __init__(self, port, host) -> None:

        self._background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port,host,prebuild_kwargs={'workspace':self})
        self._objectsync.register(Node)
        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)

        e1=self._objectsync.create_object(Edge)
        n1=self._objectsync.create_object(Node)
        n2=self._objectsync.create_object(Node)
        e2 = self._objectsync.create_object(Edge)
        e1.tail.set(n1.out_ports[0])
        e1.head.set(n2.in_ports[0])
        e2.tail.set(n1.out_ports[0])
        e2.head.set(n2.in_ports[1])

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