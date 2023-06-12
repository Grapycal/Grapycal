import os
import shutil
import signal
import sys
from typing import Any, Callable, Dict
import subprocess
import termcolor
import time

class GrapycalApp:
    def __init__(self, config) -> None:
        self._config = config

    def run(self) -> None:
        print(
            termcolor.colored(r'''
               ______                                  __
              / ____/________ _____  __  ___________ _/ /
             / / __/ ___/ __ `/ __ \/ / / / ___/ __ `/ / 
            / /_/ / /  / /_/ / /_/ / /_/ / /__/ /_/ / /  
            \____/_/   \__,_/ .___/\__, /\___/\__,_/_/   
                           /_/    /____/
                                           ''','red') + termcolor.colored('0.1.0', 'grey'))
        print()
        print('Starting Grapycal server...')
        print(f'Listening on {self._config.host}:{self._config.port}')

        if not os.path.exists('./.grapycal'):
            os.mkdir('./.grapycal')
        if not os.path.exists('./.grapycal/extensions'):
            os.mkdir('./.grapycal/extensions')
            
        self.clean_unused_fetched_extensions()

        #TODO: Support multiple workspaces
        #TODO: Websocket multiplexing

        # Here simply start one workspace in background
        workspace = subprocess.Popen([sys.executable,'-m', 'grapycal.core.workspace', '--port', str(self._config['port']), '--host', self._config['host']])
        while True:
            break_flag = False
            try:
                while True:
                    time.sleep(31415926)
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
        # IDK why workspace can't catch this signal before being killed
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
        for dir in self.get_direct_sub_folders('./.grapycal/extensions'):
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
    
    def get_direct_sub_folders(self, path: str) -> list[str]:
        return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path,f))]


