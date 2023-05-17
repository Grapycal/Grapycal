import threading
import time
from typing import Any, Callable, Dict
import objectsync
import asyncio
import signal

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

class Workspace:
    def __init__(self, port) -> None:

        self._background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port,prebuild_kwargs={'workspace':self})
        self._objectsync.register(Node)

        self._objectsync.create_object(Node)
        self._objectsync.create_object(Node)

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
    args = parser.parse_args()

    workspace = Workspace(args.port)
    workspace.run()