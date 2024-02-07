import logging
logger = logging.getLogger(__name__)

from collections import deque
from contextlib import contextmanager
from queue import Queue
import queue
import traceback
from typing import Callable, Iterator
import signal
from .stdout_helper import orig_print

class BackgroundRunner:
    def __init__(self):
        self._inputs: Queue = Queue()
        self._queue: deque = deque()
        self._stack: deque = deque()
        self._exit_flag = False
        self._exception_callback: Callable[[Exception|KeyboardInterrupt], None]|None=None

    def push(self, task: Callable, to_queue: bool = True):
        self._inputs.put((task, to_queue))

    def push_to_queue(self, task: Callable):
        self._inputs.put((task, True))

    def push_to_stack(self, task: Callable):
        self._inputs.put((task, False))

    def interrupt(self):
        signal.raise_signal(signal.SIGINT)

    def clear_tasks(self):
        self._queue.clear()
        self._stack.clear()

    def set_exception_callback(self, callback: Callable[[Exception|KeyboardInterrupt], None]|None):
        self._exception_callback = callback

    def exit(self):
        self._exit_flag = True
        self.interrupt()

    @contextmanager
    def no_interrupt(self):
        def handler(signum, frame):
            logger.info("Cannot interrupt current task")

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
                while not self._inputs.empty() or (len(self._queue) == 0 and len(self._stack) == 0):
                    try:
                        inp = self._inputs.get(timeout=0.2)
                    except queue.Empty:
                        continue
                    task, push_to_queue = inp
                    if push_to_queue:
                        self._queue.appendleft(task)
                    else:
                        self._stack.append(task)


                # queue is prioritized
                if len(self._queue) > 0:
                    task_to_run = self._queue.pop()
                else:
                    task_to_run = self._stack.pop()

                if isinstance(task_to_run, Iterator):
                    try:
                        self._stack.append(task_to_run)
                        next(task_to_run)
                    except StopIteration:
                        self._stack.pop()
                else:
                    ret = task_to_run()
                    # if ret is a generator, push it to stack
                    if ret is not None:
                        self._stack.append(iter(ret))

            except KeyboardInterrupt as e:
                logger.info("Runner interrupted")
                if self._exception_callback is None:
                    orig_print('No exception callback',e)
                else:
                    self._exception_callback(e)

            except Exception as e:
                self.clear_tasks()
                if self._exception_callback is None:
                    orig_print('No exception callback',e)
                else:
                    self._exception_callback(e)