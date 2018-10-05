
# coding: utf-8

# In[27]:


import nidaqmx
from nidaqmx.constants import (
    LineGrouping)
import pprint
import threading
import time
import pandas as pd

pp = pprint.PrettyPrinter(indent=4)

done = 0
pulse_width = 2
f = pd.read_csv(filepath_or_buffer = 'b.txt',
                dtype = {'clk' : bool, 'sync_clk' : bool, 'input_enable' : bool, 'input_signal' : bool, 'reset_n ' : bool})

# Create pulse_arr for {EN, DATA, PRG_CLK, CLK, RSTB}
pulse_en = list(f['input_enable'])
pulse_data = list(f['input_signal'])
pulse_prg_clk = list(f['clk'])
pulse_clk = list(f['sync_clk'])
pulse_rstb = list(f['reset_n '])

#print(pulse_en)
#print(pulse_data)
print(pulse_prg_clk)
print(pulse_clk)
#print(pulse_rstb)

# Threading Class for digital export
class myThread_o (threading.Thread):
    def __init__(self, threadID, name, port_line, pulse_arr, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.port_line = port_line
        self.pulse_arr = pulse_arr
        self.delay = delay
    def run(self):
        while(done==0):
            pulse_gen(self.name, self.port_line, self.delay, self.pulse_arr)
            
# Threading Class for digital import
class myThread_i (threading.Thread):
    def __init__(self, threadID, name, port_line):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.port_line = port_line
    def run(self):
        check_done(self.name, self.port_line)
    
def check_done(threadName, port_line):
    with nidaqmx.Task() as task_i:
        task_i.di_channels.add_di_chan(
            port_line,
            line_grouping=LineGrouping.CHAN_PER_LINE)
        done = task_i.read()

def pulse_gen(threadName, port_line, delay, pulse_arr):
    with nidaqmx.Task() as task_o:
        task_o.do_channels.add_do_chan(
            port_line,
            line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
        for i in pulse_arr:
            task_o.write(i)
            print(threadName, time.strftime('%H' + '%M' + '%S'))
            time.sleep(delay)

# Create new export threads {EN, DATA, PRG_CLK, CLK, RSTB}
thread_en = myThread_o(1, "Thread-en", 'Dev1/port11/line7', pulse_en, pulse_width)
thread_data = myThread_o(2, "Thread-data", 'Dev1/port8/line7', pulse_data, pulse_width)
thread_prg_clk = myThread_o(3, "Thread-prg_clk", 'Dev1/port2/line7', pulse_prg_clk, pulse_width)
thread_clk = myThread_o(4, "Thread-clk", 'Dev1/port5/line7', pulse_clk, pulse_width)
thread_rstb = myThread_o(5, "Thread-rstb", 'Dev1/port2/line6', pulse_rstb, pulse_width)

# Creaate new import thread {DONE}
thread_done = myThread_i(6, "Thread-done", 'Dev1/port8/line6')

# Start data Thread
thread_data.start()

# Dealy for snatching data(setup time)
time.sleep(pulse_width/float(2))

# Start other export Threads
thread_en.start()
thread_prg_clk.start()
thread_clk.start()
thread_rstb.start()

# Start import Thread
thread_done.start()

