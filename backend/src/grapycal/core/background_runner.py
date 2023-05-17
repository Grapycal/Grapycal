from contextlib import contextmanager
from email import contentmanager
from queue import Queue
from typing import Callable, Dict
import signal

class BackgroundRunner:
    def __init__(self):
        self._tasks: Queue[Callable] = Queue()
        self._exit_flag = False
        self._exception_callback: Callable[[Exception], None] = lambda e: None

    def add_task(self, task: Callable):
        self._tasks.put(task)

    def interrupt(self):
        signal.raise_signal(signal.SIGINT)

    def set_exception_callback(self, callback: Callable[[Exception], None]):
        self._exception_callback = callback

    def exit(self):
        self._exit_flag = True

    @contextmanager
    def no_interrupt(self):
        def handler(signum, frame):
            print("no_interrupt: continue")

        original_sigint_handler = signal.getsignal(signal.SIGINT)
        try:
            signal.signal(signal.SIGINT, handler)
            yield
        finally:
            signal.signal(signal.SIGINT, original_sigint_handler)

    def run(self):
        while True:
            if self._exit_flag:
                break
            try:
                task = None

                # Queue.get() blocks signal.
                while task is None:
                    task = self._tasks.get(timeout=0.2)

                print('got a task OAO')
                task()

            except KeyboardInterrupt:
                print("runner catch keyboardinterrupt")

            except Exception as e:
                self._exception_callback(e)