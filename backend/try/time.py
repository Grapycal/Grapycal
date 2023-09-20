N = int(1e3)

# start timer
import time
start = time.time_ns()
a=0
for i in range(N):
    time.sleep(0.0002)
# end timer
end = time.time_ns()
print((end-start)/10**9)
