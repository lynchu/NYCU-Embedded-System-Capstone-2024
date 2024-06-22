# coding: utf-8
## @package faboMPU9250
#  This is a library for the FaBo 9AXIS I2C Brick.
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

import time
import sys
import numpy as np

# Define the avg function
def avg(list):
    return sum(list) / len(list)

# Initialize variables
x_list = []
y_list = []
cnt = 0
s_x = 0 
s_y = 0
brake_time_th = 40
brake_diff_th = -0.1
start_detect_brake = False
brake = False

# Define the detect_brake function
def detect_brake(ax, ay, az):
    global x_list, y_list, cnt, s_x, s_y, start_detect_brake, brake, brake_time_th, brake_diff_th
    x_list.append(ax)
    y_list.append(ay)
    cnt = cnt + 1
    if(cnt > brake_time_th):
        s_x = avg(x_list)
        s_y = avg(y_list)
        x_list.clear()
        y_list.clear()
        cnt = 0
        start_detect_brake = True
    
    diff = (ax - s_x) + (ay - s_y)
    if (diff < brake_diff_th): 
        brake = True
    else: 
        brake = False
        
    return brake, s_x, s_y, cnt, start_detect_brake, diff

# Paths to the log files
# log_file_path = "result/turn_left/1.txt"
# output_file_path = "brake_output_log.txt"

# try:
#     with open(log_file_path, "r") as file, open(output_file_path, "w") as output_file:
#         for line in file:
#             data = line.strip().split(", ")
#             timestamp = float(data[0])
#             ax = float(data[1])
#             ay = float(data[2])
#             az = float(data[3])
#             gx = float(data[4])
#             gy = float(data[5])
#             gz = float(data[6])
            
#             print("----------------------------")
#             print(f"ax: {ax}, ay: {ay}, az: {az}")
            
#             brake, s_x, s_y, cnt, start_detect_brake, diff = detect_brake(ax, ay, az)
#             if brake:
#                 print(f"!!! brake !!!")
            
#             # Write the variables to the output log file
#             output_file.write(f"ax: {ax}, ay: {ay}, az: {az}, brake={brake}, s_x={s_x}, s_y={s_y}, cnt={cnt}, diff={diff}, start={start_detect_brake}\n")
            
#             #time.sleep(0.005)
        
# except KeyboardInterrupt:
#     sys.exit()
# except FileNotFoundError:
#     print(f"Log file not found: {log_file_path}")
#     sys.exit()
