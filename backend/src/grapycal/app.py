import signal
from typing import Any, Callable, Dict
import subprocess
import termcolor
import time

class GrapycalApp:
    def __init__(self, config:Dict[str,Any]) -> None:
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
        print(f'Listening on {self._config["host"]}:{self._config["port"]}')

        #TODO: Support multiple workspaces
        #TODO: Websocket multiplexing

        # Here simply start one workspace in background
        workspace = subprocess.Popen(['python', '-m', 'grapycal.core.workspace', '--port', str(self._config['port'])])
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

        print('Stopping workspace...')
        # IDK why workspace can't catch this signal before being killed
        workspace.send_signal(signal.SIGTERM)
        workspace.wait()
        print('Grapycal server terminated')
        return