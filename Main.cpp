#include <iostream>
#include <cstdio>
#include <cstring>
#include <thread>
#include <vector>
#include <unistd.h>
#include <getopt.h>

void Usage(FILE *out) {
  fprintf(out,
          "Command line options : main <options> \n"
          "   -h --help              :  print help message \n"
          "   -d --directory         :  directory \n"
          "   -t --time_duration     :  time duration \n"
          "   -s --data_size         :  data size \n"
          "   -c --thread_count      :  thread count \n"
  );
}

static struct option opts[] = {
    { "directory", optional_argument, NULL, 'd' },
    { "time_duration", optional_argument, NULL, 't' },
    { "data_size", optional_argument, NULL, 's' },
    { "thread_count", optional_argument, NULL, 'c' },
    { NULL, 0, NULL, 0 }
};

struct Config {
  std::string directory_ = "/tmp";
  uint64_t time_duration_ = 10;
  uint64_t data_size_ = 8;
  uint64_t thread_count_ = 1;
};

void ParseArgs(int argc, char* argv[], Config &config) {
  
  while (1) {
    int idx = 0;
    int c = getopt_long(argc, argv, "hd:t:s:c:", opts, &idx);

    if (c == -1) break;

    switch (c) {
      case 'd': {
        config.directory_ = std::string(optarg);
        break;
      }
      case 't': {
        config.time_duration_ = (uint64_t)atoi(optarg);
        break;
      }
      case 's': {
        config.data_size_ = (uint64_t)atoi(optarg);
        break;
      }
      case 'c': {
        config.thread_count_ = (uint64_t)atoi(optarg);
        break;
      }
      case 'h': {
        Usage(stderr);
        exit(EXIT_FAILURE);
        break;
      }
      default: {
        fprintf(stderr, "Unknown option: -%c-", c);
        Usage(stderr);
        exit(EXIT_FAILURE);
        break;
      }
    }
  }
}

bool is_running = false;
uint64_t *operation_counts = nullptr;

struct FileHandler {
  FILE *file_;
  int fd_;
};

FileHandler *file_handlers = nullptr;

void PerformWriteThread(const Config &config, size_t thread_id) {

  FILE *file = file_handlers[thread_id].file_;
  int fd = file_handlers[thread_id].fd_;

  char *data = new char[config.data_size_];
  memset(data, 0, config.data_size_);

  uint64_t operation_count = 0;
  while (true) {
    if (is_running == false) {
      break;
    }
    fwrite(data, 1, config.data_size_, file);
    fsync(fd);
    ++operation_count;
  }
  operation_counts[thread_id] = operation_count;

  delete[] data;
  data = nullptr;
}

void PerformWrite(const Config &config) {

  operation_counts = new uint64_t[config.thread_count_];

  file_handlers = new FileHandler[config.thread_count_];

  for (size_t i = 0; i < config.thread_count_; ++i) {

    std::string filename = config.directory_ + "/test" + std::to_string(i);
    
    // std::cout << "filename : " << filename << std::endl;
    
    auto file = fopen(filename.c_str(), "wb");
    if (file == nullptr) {
      fprintf(stderr, "file open failed!\n");
      exit(EXIT_FAILURE);
    }

    auto fd = fileno(file);
    if (fd == -1) {
      fprintf(stderr, "invalid file descriptor!\n");
      exit(EXIT_FAILURE);
    }

    file_handlers[i].file_ = file;
    file_handlers[i].fd_ = fd;

  }

  is_running = true;
  std::vector<std::thread> worker_threads;
  for (size_t i = 0; i < config.thread_count_; ++i) {
    worker_threads.push_back(std::move(std::thread(PerformWriteThread, config, i)));
  }
  std::this_thread::sleep_for(std::chrono::seconds(config.time_duration_));
  is_running = false;
  for (size_t i = 0; i < config.thread_count_; ++i) {
    worker_threads.at(i).join();
  }

  uint64_t total_count = 0;
  for (size_t i = 0; i < config.thread_count_; ++i) {
    total_count += operation_counts[i];
  }

  float iops = total_count * 1.0 / config.time_duration_ / 1000; // K
  float bandwidth = iops * config.data_size_ / 1000; // MB
  float latency = 1 / (iops / config.thread_count_) * 1000;

  printf("thread count = %llu, data size = %llu bytes, iops = %.2f K ops, bandwidth = %.2f MB, latency = %.2f us\n", 
    config.thread_count_, config.data_size_, iops, bandwidth, latency);

  delete[] operation_counts;
  operation_counts = nullptr;

  for (size_t i = 0; i < config.thread_count_; ++i) {
    fclose(file_handlers[i].file_);
  }
}

int main(int argc, char* argv[]) {

  Config config;

  ParseArgs(argc, argv, config);
  
  PerformWrite(config);

}
