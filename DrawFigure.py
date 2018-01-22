import matplotlib.pyplot as plt
import numpy as np
import re
import pickle
import os
import pylab
import matplotlib
import csv
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import LinearLocator


OPT_FONT_NAME = 'Helvetica'
TICK_FONT_SIZE = 20
LABEL_FONT_SIZE = 22
LEGEND_FONT_SIZE = 24
LABEL_FP = FontProperties(style='normal', size=LABEL_FONT_SIZE)
LEGEND_FP = FontProperties(style='normal', size=LEGEND_FONT_SIZE)
TICK_FP = FontProperties(style='normal', size=TICK_FONT_SIZE)

MARKERS = (['o', 's', 'v', "^", "h", "v", ">", "x", "d", "<", "|", "", "|", "_"])
COLOR_MAP = ( '#F58A87', '#80CA86', '#9EC9E9', '#FED113', '#D89761', '#F15854', '#5DA5DA', '#60BD68',  '#B276B2', '#DECF3F', '#F17CB0', '#B2912F', '#FAA43A', '#AFAFAF')
PATTERNS = ([ "//", "\\\\", "////", "o", "o", "\\\\" , "\\\\" , "//////", "//////", "." , "\\\\\\" , "\\\\\\" ])
LABEL_WEIGHT = 'bold'
LINE_COLORS = COLOR_MAP
LINE_WIDTH = 4.0
MARKER_SIZE = 8.0
MARKER_FREQUENCY = 1000

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['xtick.labelsize'] = TICK_FONT_SIZE
matplotlib.rcParams['ytick.labelsize'] = TICK_FONT_SIZE
matplotlib.rcParams['font.family'] = OPT_FONT_NAME


FIGURE_FOLDER = "ssd/"


def ConvertEpsToPdf(dir_filename):
  os.system("epstopdf --outfile " + dir_filename + ".pdf " + dir_filename + ".eps")
  os.system("rm -rf " + dir_filename + ".eps")


def read_file(filename, thread_counts, data_sizes):
  f = open(filename)
  last_line = ""

  iopss = np.zeros((len(thread_counts), len(data_sizes)))
  bandwidths = np.zeros((len(thread_counts), len(data_sizes)))
  latencies = np.zeros((len(thread_counts), len(data_sizes)))


  while 1:
    line = f.readline().rstrip("\n")
    if not line:
      break
    match_res = re.match(r'thread count = (.*), data size = (.*) bytes, iops = (.*) K ops, bandwidth = (.*) MB, latency = (.*) us', line)
    thread_count = match_res.group(1)
    data_size = match_res.group(2)
    iops = match_res.group(3)
    bandwidth = match_res.group(4)
    latency = match_res.group(5)

    thread_count_idx = thread_counts.index(int(thread_count))
    data_size_idx = data_sizes.index(int(data_size))
    iopss[thread_count_idx][data_size_idx] = iops
    bandwidths[thread_count_idx][data_size_idx] = bandwidth
    latencies[thread_count_idx][data_size_idx] = latency

  return iopss, bandwidths, latencies

def draw_figure(iopss, thread_counts, data_sizes, selected_thread_counts, selected_data_sizes, file_prefix, ylabel):

  fig = plt.figure(figsize=(8,3.2))
  figure = fig.add_subplot(111)

  x_values = selected_thread_counts
  y_values = [[] for x in xrange(len(selected_data_sizes))]

  FIGURE_LABEL = []
  for data_size in selected_data_sizes:
    FIGURE_LABEL.append(str(data_size))

  for thread_count in selected_thread_counts:
    thread_count_idx = thread_counts.index(thread_count)

    for data_size in selected_data_sizes:
      data_size_idx = data_sizes.index(data_size)
      selected_data_size_idx = selected_data_sizes.index(data_size)

      y_values[selected_data_size_idx].append(iopss[thread_count_idx][data_size_idx])
  
  idx = 0
  lines = [None] * (len(FIGURE_LABEL))
  for i in range(len(y_values)):
    lines[idx], = figure.plot(x_values, y_values[i], color=LINE_COLORS[i], \
                linewidth=LINE_WIDTH, marker=MARKERS[i], \
                markersize=MARKER_SIZE, label=FIGURE_LABEL[i])
    idx = idx + 1

  # plt.legend(lines, FIGURE_LABEL, prop=LEGEND_FP, 
  #                  loc=1, ncol=len(FIGURE_LABEL), mode="expand", shadow=False,
  #                  frameon=False, borderaxespad=0.0, handlelength=2)

  plt.xticks(x_values)
  plt.xlim(1, )
  plt.ylim(0, )

  plt.grid(axis='y',color='gray')    
  figure.yaxis.set_major_locator(LinearLocator(6))
  
  figure.get_xaxis().set_tick_params(direction='in', pad=10)
  figure.get_yaxis().set_tick_params(direction='in', pad=10)
  
  plt.xlabel('Number of threads', fontproperties=LABEL_FP)
  plt.ylabel(ylabel, fontproperties=LABEL_FP)

  
  size = fig.get_size_inches()
  dpi = fig.get_dpi()
  
  if not os.path.exists(FIGURE_FOLDER):
    os.makedirs(FIGURE_FOLDER)
  plt.savefig(FIGURE_FOLDER + "/" + file_prefix + ".eps", bbox_inches='tight', format='eps')
  ConvertEpsToPdf(FIGURE_FOLDER + "/" + file_prefix)

def create_legend(selected_data_sizes):
  fig = pylab.figure()
  ax1 = fig.add_subplot(111)

  FIGURE_LABEL = []
  for data_size in selected_data_sizes:
    FIGURE_LABEL.append(str(data_size))

  LINE_WIDTH = 8.0
  MARKER_SIZE = 12.0
  LEGEND_FP = FontProperties(style='normal', size=26)

  figlegend = pylab.figure(figsize=(12, 0.5))
  idx = 0
  lines = [None] * (len(FIGURE_LABEL))
  data = [1]
  x_values = [1]

  # lines[idx], = ax1.plot(x_values, data, linewidth = 0)
  idx = 0
  for group in xrange(len(FIGURE_LABEL)):
      lines[idx], = ax1.plot(x_values, data,
                             color=LINE_COLORS[idx], linewidth=LINE_WIDTH,
                             marker=MARKERS[idx], markersize=MARKER_SIZE, label=str(group))

      idx = idx + 1

  # LEGEND
  figlegend.legend(lines, FIGURE_LABEL, prop=LEGEND_FP, 
                   loc=1, ncol=len(FIGURE_LABEL), mode="expand", shadow=False,
                   frameon=False, borderaxespad=0.0, handlelength=2)

  if not os.path.exists(FIGURE_FOLDER):
    os.makedirs(FIGURE_FOLDER)
  figlegend.savefig(FIGURE_FOLDER + '/ssd_legend.pdf')


if __name__ == "__main__":
  filename = "result_ssd.txt"

  thread_counts = [1]
  for i in range(4, 81, 4):
    thread_counts.append(i)
  
  data_sizes = []
  for i in range(2, 16):
    data_sizes.append(1 << i)

  selected_thread_counts = [1]
  for i in range(8, 81, 8):
    selected_thread_counts.append(i)

  selected_data_sizes = []
  for i in range (3, 17, 2):
    selected_data_sizes.append(1 << i)

  iopss, bandwidths, latencies = read_file(filename, thread_counts, data_sizes)
  draw_figure(iopss, thread_counts, data_sizes, selected_thread_counts, selected_data_sizes, "ssd-iops", "iops")
  draw_figure(bandwidths, thread_counts, data_sizes, selected_thread_counts, selected_data_sizes, "ssd-bandwidth", "bandwidth")
  draw_figure(latencies, thread_counts, data_sizes, selected_thread_counts, selected_data_sizes, "ssd-latency", "latency")

  create_legend(selected_data_sizes)
  

