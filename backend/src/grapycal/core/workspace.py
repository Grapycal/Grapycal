import os
import time
import grapycal
from grapycal.extension.extensionManager import ExtensionManager
from grapycal.extension.utils import Clock
from grapycal.sobjects.controls.linePlotControl import LinePlotControl
from grapycal.sobjects.controls.threeControl import ThreeControl
from grapycal.sobjects.fileView import LocalFileView, RemoteFileView
from grapycal.sobjects.settings import Settings
from grapycal.sobjects.controls import *
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.workspaceObject import WebcamStream, WorkspaceObject
from grapycal.utils.httpResource import HttpResource
from grapycal.utils.io import file_exists, read_workspace, write_workspace

from grapycal.utils.logging import setup_logging
setup_logging()
import logging
logger = logging.getLogger('workspace')

from typing import Any, Dict

import threading
import objectsync
from objectsync.sobject import SObjectSerialized
import asyncio
import signal
from dacite import from_dict
import importlib.metadata


from grapycal.core import stdout_helper


from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort 
from grapycal.sobjects.sidebar import Sidebar

from grapycal.core.background_runner import BackgroundRunner
from grapycal.sobjects.node import Node

from grapycal.core import running_module

def deserialize_sort_key(x: SObjectSerialized) -> int:
    if x.type == 'Edge':
        return 1000000000 # Edges should be created after nodes
    if x.id.startswith('0_'):
        return int(x.id[2:])
    return 0

class Workspace:
    def __init__(self, port, host, path) -> None:
        self.path = path
        self.port = port
        self.host = host
        self.running_module = running_module
        ''''''

        '''
        Enable stdout proxy for this process
        '''
        stdout_helper.enable_proxy(redirect_error=False)
        self.redirect = stdout_helper.redirect

        self._communication_event_loop: asyncio.AbstractEventLoop | None = None

        self.background_runner = BackgroundRunner()

        self._objectsync = objectsync.Server(port,host,deserialize_sort_key=deserialize_sort_key)
        
        self._extention_manager = ExtensionManager(self._objectsync,self)

        self.do_after_transition = self._objectsync.do_after_transition

        self.clock = Clock(0.1)

        self.webcam: WebcamStream|None = None

        self.data_yaml = HttpResource('https://github.com/eri24816/grapycal_data/raw/main/data.yaml')

    def _communication_thread(self,event_loop_set_event: threading.Event):
        asyncio.run(self._async_communication_thread(event_loop_set_event))

    async def _async_communication_thread(self,event_loop_set_event: threading.Event):
        self._communication_event_loop = asyncio.get_event_loop()
        event_loop_set_event.set()
        try:
            await asyncio.gather(self._objectsync.serve(),self.clock.run())
        except OSError as e:
            if e.errno == 10048:
                logger.error(f'Port {self.port} is already in use. Maybe another instance of grapycal is running?')
                self.get_communication_event_loop().stop()
                # send signal to the main thread to exit
                os.kill(os.getpid(), signal.SIGTERM)
            else:
                raise e

    def run(self) -> None:

        event_loop_set_event = threading.Event()
        t = threading.Thread(target=self._communication_thread,daemon=True,args=[event_loop_set_event]) # daemon=True until we have a proper exit strategy

        t.start()
        event_loop_set_event.wait()

        self._extention_manager.start()

        self._objectsync.globals.workspace = self

        self._objectsync.register_service('exit', self.exit)

        self._objectsync.register(WorkspaceObject)
        self._objectsync.register(Editor)
        self._objectsync.register(Sidebar)
        self._objectsync.register(Settings)
        self._objectsync.register(LocalFileView)
        self._objectsync.register(RemoteFileView)
        self._objectsync.register(InputPort)
        self._objectsync.register(OutputPort)
        self._objectsync.register(Edge)

        self._objectsync.register(TextControl)
        self._objectsync.register(ButtonControl)
        self._objectsync.register(ImageControl)
        self._objectsync.register(ThreeControl)

        self._objectsync.register(WebcamStream)
        self._objectsync.register(LinePlotControl)
        
        '''
        Register all built-in node types
        '''

        signal.signal(signal.SIGTERM, lambda sig, frame: self.exit())

        if file_exists(self.path):
            logger.info(f'Found existing workspace file {self.path}. Loading.')
            self.load_workspace(self.path)
        else:
            logger.info(f'No workspace file found at {self.path}. Creating a new workspace to start with.')
            self.initialize_workspace()

        self.save_workspace(self.path)
            
        self._objectsync.on('ctrl+s',lambda: self.save_workspace(self.path),is_stateful=False)
        self._objectsync.on('open_workspace',self._open_workspace_callback,is_stateful=False)
    
        self.background_runner.run()

    def exit(self):
        logger.info('exit')
        self.background_runner.exit()

    def get_communication_event_loop(self) -> asyncio.AbstractEventLoop:
        assert self._communication_event_loop is not None
        return self._communication_event_loop
    
    '''
    Save and load
    '''         

    def initialize_workspace(self) -> None:
        self._objectsync.create_object(WorkspaceObject, parent_id='root')
        try:
            self._extention_manager.import_extension('grapycal_builtin')
        except ModuleNotFoundError:
            pass

    def save_workspace(self, path: str) -> None:
        workspace_serialized = self.get_workspace_object().serialize()

        metadata = {
            'version': grapycal.__version__,
            'extensions': self._extention_manager.get_extensions_info(), 
        }
        data = {
            'extensions': self._extention_manager.get_extention_names(), 
            'client_id_count': self._objectsync.get_client_id_count(),
            'id_count': self._objectsync.get_id_count(),
            'workspace_serialized': workspace_serialized.to_dict(),
        }
        write_workspace(path, metadata, data, compress=True)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logger.info(f'Workspace saved to {path} at {time_str}')

    def load_workspace(self, path: str) -> None:
        version,metadata,data = read_workspace(path)
        
        self._check_grapycal_version(version)
        if 'extensions' in metadata: # DEPRECATED: v0.9.0 and before has no extensions in metadata
            self._check_extensions_version(metadata['extensions'])

        self._objectsync.set_client_id_count(data['client_id_count'])
        self._objectsync.set_id_count(data['id_count'])
        workspace_serialized = from_dict(SObjectSerialized,data['workspace_serialized'])

        # DEPRECATED: The old format of attributes is [name, type, value, value].
        def resolve_deprecated_attr_format(obj: SObjectSerialized):
            for attr in obj.attributes:
                if attr.__len__() == 4:
                    attr.append(attr[3])
            for child in obj.children.values():
                resolve_deprecated_attr_format(child)
        resolve_deprecated_attr_format(workspace_serialized)

        for extension_name in data['extensions']:
            self._extention_manager.import_extension(extension_name,create_preview_nodes=False)

        self._objectsync.create_object(WorkspaceObject, parent_id='root', old=workspace_serialized, id=workspace_serialized.id)

        for extension_name in data['extensions']:
            self._extention_manager.create_preview_nodes(extension_name)

        self._objectsync.clear_history_inclusive()

    def _check_grapycal_version(self,version:str):
        # check if the workspace version is compatible with the current version
        workspace_version_tuple = tuple(map(int, version.split('.')))
        current_version_tuple = tuple(map(int, grapycal.__version__.split('.')))
        if current_version_tuple < workspace_version_tuple:
            logger.warning(f'Attempting to downgrade workspace from version {version} to {grapycal.__version__}. This may cause errors.')

    def _check_extensions_version(self,extensions_info):
        # check if all extensions version are compatible with the current version
        for extension_info in extensions_info:
            extension_version_tuple = tuple(map(int, extension_info['version'].split('.')))
            try:
                current_version_tuple = tuple(map(int, importlib.metadata.version(extension_info['name']).split('.')))
            except importlib.metadata.PackageNotFoundError:
                continue # ignore extensions that are not installed
            if current_version_tuple < extension_version_tuple:
                logger.warning(f'Attempting to downgrade extension {extension_info["name"]} from version {extension_info["version"]} to {importlib.metadata.version(extension_info["name"])}. This may cause errors.')


    def get_workspace_object(self) -> WorkspaceObject:
        # In case this called in self._objectsync.create_object(WorkspaceObject), 
        return self._objectsync.get_root_object().get_child_of_type(WorkspaceObject)
    
    def vars(self)->Dict[str,Any]:
        return self.running_module.__dict__
    
    def _open_workspace_callback(self,path,no_exist_ok=False):
        if not no_exist_ok:
            if not os.path.exists(path):
                raise Exception(f'File {path} does not exist')
        if not path.endswith('.grapycal'):
            raise Exception(f'File {path} does not end with .grapycal')
            
        pid = os.getpid()
        exit_message_file = f'grapycal_exit_message_{pid}'
        with open(exit_message_file,'w') as f:
            f.write(f'open {path}')
        self.exit()

    def add_task_to_event_loop(self,task):
        self._communication_event_loop.create_task(task)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--path', type=str, default='workspace.grapycal')
    args = parser.parse_args()

    workspace = Workspace(args.port,args.host,args.path)
    workspace.run()