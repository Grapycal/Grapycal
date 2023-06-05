import asyncio
from concurrent.futures import thread
import io
import threading
from typing import Callable


class OutputStream:
    def __init__(self, on_flush:Callable[[str],None], hz=20):
        self._stream = io.StringIO()
        self._enable_flush = 0
        self._enable_flush_event = asyncio.Event()
        self._lock = threading.Lock()
        self._exit_flag = False
        self._on_flush = on_flush
        self._gap = 1/hz

    async def run(self):
        while True:
            if self._exit_flag:
                self._stream.close()
                return
            await self._enable_flush_event.wait()
            if self._exit_flag:
                self._stream.close()
                return
            while self._enable_flush > 0:
                if self._exit_flag:
                    self._stream.close()
                    return
                with self._lock:
                    # read
                    self._stream.seek(0)
                    data = self._stream.read()
                    # clear
                    self._stream.seek(0)
                    self._stream.truncate()

                self._on_flush(data)
                await asyncio.sleep(self._gap)

            with self._lock:
                # read
                self._stream.seek(0)
                data = self._stream.read()
                # clear
                self._stream.seek(0)
                self._stream.truncate()

            self._on_flush(data)

    def write(self, data):
        with self._lock:
            self._stream.write(data)

    def enable_flush(self):
        self._enable_flush += 1
        self._enable_flush_event.set()

    def disable_flush(self):
        self._enable_flush -= 1
        if self._enable_flush == 0:
            self._enable_flush_event.clear()

    def close(self):
        self._exit_flag = True
        self._enable_flush_event.set()
        print('output stream closed')

    