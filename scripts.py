import os

DIRECTORY = "/tmp"
TIME_DURATION = 10

if __name__ == "__main__":
  max_thread_count = os.sysconf('SC_NPROCESSORS_ONLN')
  

  for i in range(2, 16):
    data_size = 1 << i

    os.system('./main -d ' + DIRECTORY + ' -c ' + str(1) + ' -s ' + str(data_size))

    for thread_count in range(4, max_thread_count + 1, 4):
      os.system('./main -d ' + DIRECTORY + ' -c ' + str(thread_count) + ' -s ' + str(data_size))
