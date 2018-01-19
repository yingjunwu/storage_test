#pragma once

static const float CPU_MHZ = 1400;

class PreciseTimeMeasurer{
public:
  PreciseTimeMeasurer(){}
  ~PreciseTimeMeasurer(){}

//#if defined(__x86_64__)
  static __inline__ unsigned long long rdtsc(void){
    unsigned hi, lo;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((unsigned long long)lo) | (((unsigned long long)hi) << 32);
  }
//#endif

  void StartTimer(){
    start_time_ = rdtsc();
  }

  void EndTimer(){
    end_time_ = rdtsc();
  }

  long long GetElapsedMilliSeconds(){
    return (long long)((end_time_ - start_time_) / (CPU_MHZ * 1000));
  }

  long long GetElapsedMicroSeconds(){
    return (long long)((end_time_ - start_time_) / CPU_MHZ);
  }

  long long GetElapsedNanoSeconds(){
    return (long long)((end_time_ - start_time_) * 1000 / CPU_MHZ);
  }

private:
  PreciseTimeMeasurer(const PreciseTimeMeasurer&);
  PreciseTimeMeasurer& operator=(const PreciseTimeMeasurer&);

private:
  unsigned long long start_time_;
  unsigned long long end_time_;
};