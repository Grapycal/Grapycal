import os
import signal
import sys
import subprocess
import time

p = subprocess.Popen(["python", "sub.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("pid", p.pid)
time.sleep(1)
p.terminate()
print("a")

print(p.communicate()[0].decode("utf-8"))
print(p.communicate()[0].decode("utf-8"))
print("b")
print(p.communicate()[1].decode("utf-8"))
p.wait()