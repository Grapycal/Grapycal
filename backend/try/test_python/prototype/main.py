from contextlib import contextmanager
from queue import Queue
import signal
import threading
import time
from traceback import format_exc

# mock stuffs

def send_ws(data):
    print('send <',data)

def recv_ws():
    data = input()
    print('recv >',data)
    return data

def communicate_thread():
    while True:
        data = recv_ws()
        if data == 'int':
            signal.raise_signal(signal.SIGINT)
        else:
            task_queue.put(data)

class StateMachine:
    def __init__(self):
        self.state = 'init'
        self.lock = threading.Lock()
        self.transition = []

    @contextmanager
    def record(self):
        with self.lock:
            yield
            send_ws('transition: '+str(self.transition))
            self.transition = []

    def set_state(self, state):
        self.state = state
        self.transition.append(state)
        

# program

task_queue = Queue()
state_machine = StateMachine()

def node1():
    with state_machine.record():
        state_machine.set_state('node1 a')
        time.sleep(5)
        state_machine.set_state('node1 b')

def node2():
    with state_machine.record():
        state_machine.set_state('node1 a')
    time.sleep(5)
    with state_machine.record():
        state_machine.set_state('node1 b')

def main():
    t = threading.Thread(target=communicate_thread,daemon=True)
    t.start()
    while True:
        try:
            data = task_queue.get()
            print('processing:',data)
            if data == 'exit':
                break
            exec(data, globals())
        except KeyboardInterrupt:
            print("main thread catch keyboardinterrupt")
            pass
        except Exception as e:
            send_ws('error: '+ format_exc())

if __name__ == '__main__':
    main()

'''
usage: 
1. enter node1()
2. enter with state_machine.record(): state_machine.set_state('aaa')

import time
recv > import time
processing: import time
for i in range(1000): time.sleep(1); print(i) 
recv > for i in range(1000): time.sleep(1); print(i)
processing: for i in range(1000): time.sleep(1); print(i)
0
1
2
3
int
recv > int
main thread catch keyboardinterrupt

'''