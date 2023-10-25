import os
import shutil
import signal
import sys
from typing import Any, Callable, Dict
import subprocess
from .utils.file import get_direct_sub_folders
import termcolor
import time
from importlib.metadata import version as get_version

class GrapycalApp:
    """
    The backend server

    :param usersettings.Settings config: the configuration for server
    """
    def __init__(self, config) -> None:
        self._config = config

    def run(self) -> None:
        """
        Server main loop
        """
        version = get_version('grapycal')
        print(
            termcolor.colored(r'''
               ______                                  __
              / ____/________ _____  __  ___________ _/ /
             / / __/ ___/ __ `/ __ \/ / / / ___/ __ `/ / 
            / /_/ / /  / /_/ / /_/ / /_/ / /__/ /_/ / /  
            \____/_/   \__,_/ .___/\__, /\___/\__,_/_/   
                           /_/    /____/
                                           ''','red') + termcolor.colored('v'+version, 'grey'))
        print()
        print('Starting Grapycal server...')

        if not os.path.exists('./.grapycal'):
            os.mkdir('./.grapycal')
        if not os.path.exists('./.grapycal/extensions'):
            os.mkdir('./.grapycal/extensions')
            
        self.clean_unused_fetched_extensions()

        #TODO: Support multiple workspaces
        #TODO: Websocket multiplexing

        workspace = None
        # Here simply start one workspace in background
        while True:
            break_flag = False
            try:
            
                # Start webpage server
                if not self._config['no_serve_webpage']:
                    webpage_path = os.path.join(os.path.dirname(__file__),'webpage')
                    print(f'Strating webpage server at localhost:9001 from {webpage_path}')
                    subprocess.Popen([sys.executable,'-m', 'http.server','9001'],start_new_session=True,cwd=webpage_path)

                while True: # Restart workspace when it exits. Convenient for development

                    # Start workspace
                    print(f'Starting workspace {self._config["path"]}')
                    print(f'Host: {self._config["host"]}')
                    print(f'Port: {self._config["port"]}')
                    workspace = subprocess.Popen([sys.executable,'-m', 'grapycal.core.workspace',
                        '--port', str(self._config['port']),
                        '--host', self._config['host'],
                        '--path', self._config['path']],start_new_session=True)
                    
                    while True:
                        time.sleep(1)
                        if workspace.poll() is not None:
                            print('Workspace exited with code',workspace.poll())
                            break

                    if not self._config['restart']:
                        break

            except KeyboardInterrupt:
                print('Shutting down Grapycal server will force kill all workspaces. Press Ctrl+C again to confirm.')
                try:
                    time.sleep(3)
                except KeyboardInterrupt:
                    break_flag = True
                else:
                    print('Resumed')
            if break_flag:
                break

        print('Stopping workspaces...')
        if workspace:
            workspace.send_signal(signal.SIGTERM)
            workspace.wait()
        self.clean_unused_fetched_extensions()
        print('Grapycal server terminated')
        return
    
    def clean_unused_fetched_extensions(self):
        used_extensions = []
        for f in os.listdir('.'):
            if f.endswith('.grapycal') and not f.startswith('.'):
                used_extensions += self.parse_extensions_from_workspace(f)
        for dir in get_direct_sub_folders('./.grapycal/extensions'):
            if dir not in used_extensions:
                shutil.rmtree(f'./.grapycal/extensions/{dir}')
                
    def parse_extensions_from_workspace(self,workspace_path: str) -> list[str]:
        extensions_field = ''
        pre_match = '{"extensions":['
        with open(workspace_path,'r') as f:
            while len(pre_match) > 0:
                char = f.read(1)
                if char == ' ' or char == '\n':
                    continue
                assert char == pre_match[0], f'Expected {pre_match[0]} but got {char}'
                pre_match = pre_match[1:]
            while True:
                char = f.read(1)
                if char == ' ' or char == '\n' or char == '"':
                    continue
                if char == ']':
                    break
                extensions_field += char
        return extensions_field.split(',')


