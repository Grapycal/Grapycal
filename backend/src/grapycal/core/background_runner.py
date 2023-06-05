from collections import deque
from contextlib import contextmanager
from queue import Queue
from typing import Callable, Dict
import signal

class BackgroundRunner:
    def __init__(self):
        self._inputs: Queue = Queue()
        self._tasks: deque = deque()
        self._exit_flag = False
        self._exception_callback: Callable[[Exception], None] = lambda e: None

    def push(self, task: Callable):
        self._inputs.put((task, False))

    def push_front(self, task: Callable):
        self._inputs.put((task, True))

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
                # Queue.get() blocks signal.
                while len(self._tasks) == 0 or not self._inputs.empty():
                    inp = self._inputs.get(timeout=0.2)
                    if inp is None:
                        continue
                    task, is_front = inp
                    if is_front:
                        self._tasks.append(task)
                    else:
                        self._tasks.appendleft(task)

                print('got a task OAO')
                task_to_run = self._tasks.pop()
                task_to_run()

            except KeyboardInterrupt:
                print("runner catch keyboardinterrupt")

            except Exception as e:
                self._exception_callback(e)