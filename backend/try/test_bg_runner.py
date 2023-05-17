from pdb import run
from grapycal.core.background_runner import BackgroundRunner
import threading
import time

runner = BackgroundRunner()

def count_to_ten():
    print('count_to_ten')
    for i in range(10):
        print(i)
        time.sleep(1)

def count_to_ten_at_least_5():
    print('count_to_ten')
    with runner.no_interrupt():
        for i in range(5):
            print(i)
            time.sleep(1)
    for i in range(5,10):
        print(i)
        time.sleep(1)

def app():
    print('app')

    runner.add_task(count_to_ten)
    time.sleep(3)
    runner.interrupt()

    runner.add_task(count_to_ten_at_least_5)
    time.sleep(3)
    runner.interrupt()
    time.sleep(3)
    runner.interrupt()

    runner.exit()

app_thread = threading.Thread(target=app, daemon=True)
app_thread.start()
runner.run()
