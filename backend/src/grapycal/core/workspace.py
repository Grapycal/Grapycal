
from grapycal.extension.extensionManager import ExtensionManager
from grapycal.extension.utils import Clock
from ..sobjects.controls import *
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.workspaceObject import WorkspaceObject
from grapycal.utils.io import file_exists, json_read, json_write
from grapycal.utils.logging import setup_logging
logger = setup_logging()

from typing import Any, Dict

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

from . import running_module

class Workspace:
    def __init__(self, port, host, path) -> None:
        self.path = path
        self.running_module = running_module
        ''''''

        '''
        Enable stdout proxy for this process
        '''
        stdout_helper.enable_proxy(redirect_error=False)
        self.redirect = stdout_helper.redirect

        self._communication_event_loop: asyncio.AbstractEventLoop | None = None

        self.background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port,host)
        
        self._extention_manager = ExtensionManager(self._objectsync,self)

        self.do_after_transition = self._objectsync.do_after_transition

        self.clock = Clock(0.1)

    def _communication_thread(self,event_loop_set_event: threading.Event):
        asyncio.run(self._async_communication_thread(event_loop_set_event))

    async def _async_communication_thread(self,event_loop_set_event: threading.Event):
        self._communication_event_loop = asyncio.get_event_loop()
        event_loop_set_event.set()
        await asyncio.gather(self._objectsync.serve(),self.clock.run())

    def run(self) -> None:
        print('Workspace running')
        event_loop_set_event = threading.Event()
        t = threading.Thread(target=self._communication_thread,daemon=True,args=[event_loop_set_event]) # daemon=True until we have a proper exit strategy

        t.start()
        event_loop_set_event.wait()

        self._objectsync.globals.workspace = self

        self._objectsync.register_service('exit', self.exit)

        self._objectsync.register(WorkspaceObject)
        self._objectsync.register(Editor)
        self._objectsync.register(Sidebar)
        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)

        self._objectsync.register(TextControl)
        self._objectsync.register(ButtonControl)
        self._objectsync.register(ImageControl)
        
        '''
        Register all built-in node types
        '''

        signal.signal(signal.SIGTERM, lambda sig, frame: self.exit())

        if file_exists(self.path):
            self.load_workspace(self.path)
        else:
            self.initialize_workspace()
            
        self._objectsync.on('ctrl+s',lambda: self.save_workspace(self.path),is_stateful=False)
    
        self.background_runner.run()

    def exit(self):
        print('exit')
        self.background_runner.exit()

    def get_communication_event_loop(self) -> asyncio.AbstractEventLoop:
        assert self._communication_event_loop is not None
        return self._communication_event_loop
    
    '''
    Save and load
    '''         

    def initialize_workspace(self) -> None:
        self._objectsync.create_object(WorkspaceObject, parent_id='root')
        self._extention_manager.import_extension('grapycal_builtin')

    def save_workspace(self, path: str) -> None:
        workspace_serialized = self.get_workspace_object().serialize()
        data = {
            'extensions': self._extention_manager.get_extention_names(), 
            # Note: The extension field is intended to be on top so it can be easily retrieved by the extension management program.
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
        self._extention_manager.load_extensions(data['extensions'])
        self._objectsync.create_object(WorkspaceObject, parent_id='root', serialized=workspace_serialized, id=workspace_serialized.id)

    def get_workspace_object(self) -> WorkspaceObject:
        # In case this called in self._objectsync.create_object(WorkspaceObject), 
        return self._objectsync.get_root_object().get_child_of_type(WorkspaceObject)
    
    def vars(self)->Dict[str,Any]:
        return self.running_module.__dict__

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--path', type=str, default='workspace.grapycal')
    args = parser.parse_args()

    workspace = Workspace(args.port,args.host,args.path)
    workspace.run()