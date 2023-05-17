import subprocess
import sys
proc = subprocess.Popen(["python", "CallMyName.py "],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

proc.stdin.write(b"Alex\n")
proc.stdin.write(b"Jhon\n")
proc.stdin.close()
while proc.returncode is None:
    proc.poll()

print(proc.stdout.readline())
print(proc.stdout.readline())