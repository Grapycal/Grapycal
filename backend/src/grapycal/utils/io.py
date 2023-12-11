import gzip
import logging

import grapycal
logger = logging.getLogger(__name__)

import json
import asyncio
import io
import threading
from typing import Any, Callable, Tuple

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

from functools import partial
def write_workspace(path:str,metadata,data:Any,compress=False):
    if not compress:
        open_func = partial(open,path,'w',encoding='utf-8')
    else:
        open_func = partial(gzip.open,path,'wt')

    with open_func() as f:
        f.write(grapycal.__version__+'\n')
        json.dump(metadata,f)
        f.write('\n')
        json.dump(data,f)

def read_workspace(path,metadata_only=False) -> Tuple[str,Any,Any]:
    # see if first two bytes are 1f 8b
    with open(path,'rb') as f:
        magic_number = f.read(2)
    if magic_number == b'\x1f\x8b':
        open_func = partial(gzip.open,path,'rt')
    else:
        open_func = partial(open,path,'r',encoding='utf-8')

    with open_func() as f:

        # DEPRECATED: v0.9.0 and before has no version number and metadata
        try:
            version = f.readline().strip()
            metadata = json.loads(f.readline())
        except json.decoder.JSONDecodeError:
            f.seek(0)
            version = '0.9.0'
            metadata = {}
            data = json.loads(f.read()) if not metadata_only else None
            return version, metadata, data
        
        f.seek(0)
        version = f.readline().strip()
        metadata = json.loads(f.readline())
        data = json.loads(f.readline()) if not metadata_only else None
    return version, metadata, data

    
def file_exists(path):
    try:
        with open(path,'r') as f:
            return True
    except FileNotFoundError:
        return False