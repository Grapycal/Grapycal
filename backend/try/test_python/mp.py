import multiprocessing as mp
from websockets import server

def task(num,nn):
    print('This is cpu core: ', num)
    print(nn)

if __name__=='__main__':
  cpu_count = mp.cpu_count()
  print("cpu_count: ", cpu_count)
  process_list = []
  for i in range(cpu_count):
    process_list.append(mp.Process(target = task, args = (i,server)))
    process_list[i].start()

  for i in range(cpu_count):
    process_list[i].join()