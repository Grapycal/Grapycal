from calendar import c
from queue import Queue
import time
import os
import signal
import threading

old_print = print
class safe_print:
    def __init__(self):
        self.queue = Queue()
        self.thread = threading.Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def worker(self):
        while True:
            old_print(*self.queue.get())
            self.queue.task_done()

    def __call__(self, *args):
        self.queue.put(args)

print = safe_print()

def new_thread():
    try:
        print("new_thread_start")
        time.sleep(1)
        for i in range(100000000):
            print('new',i)
            time.sleep(1)

            signal.raise_signal(signal.SIGINT)

    except KeyboardInterrupt:
        print("new_thread catch keyboardinterrupt")
        pass

def signal_handler(signum, frame):
    print("can't interrupt when i<5")

#signal.signal(signal.SIGINT, signal_handler)
print(f'hi i am subprocess {os.getpid()}')
#os.kill(os.getpid(), signal.SIGINT)

t = threading.Thread(target=new_thread,daemon=True)
t.start()

for e in range(3):
    try:
        original_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal_handler)
        for i in range(100000000):
            if i>=5:
                # unregister signal handler
                signal.signal(signal.SIGINT, original_sigint_handler)
            print('main',e,i)
            time.sleep(1)
    except KeyboardInterrupt:
        print("main thread catch keyboardinterrupt")
        pass