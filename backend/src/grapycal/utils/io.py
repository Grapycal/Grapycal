import logging
logger = logging.getLogger(__name__)

import json
import asyncio
import io
import threading
from typing import Any, Callable

class OutputStream:
    def __init__(self, on_flush:Callable[[str],None], hz=20):
        self._stream = io.StringIO()
        self._enables = 0
        self._enable_flush_event = asyncio.Event()
        self._lock = threading.Lock()
        self._exit_flag = False
        self._on_flush = on_flush
        self._gap = 1/hz

    def set_event_loop(self, event_loop):
        self._event_loop = event_loop

    async def run(self):
        self._event_loop = asyncio.get_running_loop()
        while True:
            if self._exit_flag:
                self._stream.close()
                return
            await self._enable_flush_event.wait()
            if self._exit_flag:
                self._stream.close()
                return
            while self._enables > 0:
                if self._exit_flag:
                    self._stream.close()
                    return
                # read
                self._stream.seek(0)
                data = self._stream.read()
                # clear
                self._stream.seek(0)
                self._stream.truncate()
                self._on_flush(data)
                await asyncio.sleep(self._gap)

            self._enable_flush_event.clear()

            # read
            self._stream.seek(0)
            data = self._stream.read()
            # clear
            self._stream.seek(0)
            self._stream.truncate()
            self._on_flush(data)

    def write(self, data):
        # Is stream thread safe?
        # locking makes deadlock
        self._stream.write(data)

    def flush(self): # dummy
        return
    
    def enable_flush(self):
        self._event_loop.call_soon_threadsafe(self._enable_flush)
        
    def _enable_flush(self):
        self._enables += 1
        self._enable_flush_event.set()

    def disable_flush(self):
        self._event_loop.call_soon_threadsafe(self._disable_flush)

    def _disable_flush(self):
        self._enables -= 1

    def close(self):
        self._exit_flag = True
        self._enable_flush_event.set()

def json_write(path:str,data:Any):
    with open(path,'w') as f:
        json.dump(data,f,indent=4)

def json_read(path):
    with open(path,'r') as f:
        return json.load(f)
    
def file_exists(path):
    try:
        with open(path,'r') as f:
            return True
    except FileNotFoundError:
        return False