#!/usr/bin/python3

import time
from math import *

x_list = []
y_list = []
s_x = 0  # the x value for straight
s_y = 0

cnt = 0 # for list
r_cnt = 0  # count how long it has heading right
l_cnt = 0
s_cnt = 0
turn_time_th = 50  # about to turn for more than this time -> turn
stra_time_th = 50
x_angl_th = 40  # turn for more than this angl -> about to turn
y_angl_th = 40
s_angel_th = 20  # turn less than it -> straight
direction = "straight"  # current direction, initially straight

def avg(list):
    return sum(list) / len(list)

def get_direction(magx, magy, magz):
    global s_cnt, l_cnt, r_cnt, s_x, s_y, s_x_set, s_y_set, direction, cnt, x_list, y_list
    x_list.append(magx)
    y_list.append(magy)
    cnt = cnt + 1
    if(cnt > stra_time_th):
        s_x = avg(x_list)
        s_y = avg(y_list)
        x_list.clear()
        y_list.clear()
        cnt = 0
        
    # decide the direction
    if s_cnt > stra_time_th:
        direction = "straight"
        s_cnt = 0
        l_cnt = 0
        r_cnt = 0
        # decide the value for straight after turning
        
        
    elif l_cnt > turn_time_th:
        direction = "left"
        s_cnt = 0
        l_cnt = 0
        r_cnt = 0
    elif r_cnt > turn_time_th:
        direction = "right"
        s_cnt = 0
        l_cnt = 0
        r_cnt = 0

    # count how long it has been about to turn
    dx = s_x - magx 
    dy = s_y - magy
    print("dx = ", dx)
    print("dy = ", dy)
    print("s_cnt = ", s_cnt)
    print("l_cnt = ", l_cnt)
    print("r_cnt = ", r_cnt)
    print("s_x = ", s_x)
    print("s_y = ", s_y)
    if s_x - magx < s_angel_th and s_y - magy < s_angel_th and magy - s_y < s_angel_th:
        s_cnt += 1
    elif magx - s_x > x_angl_th or magy - s_y > y_angl_th:
        l_cnt += 1
    elif s_x - magx > x_angl_th or s_y - magy > y_angl_th:
        r_cnt += 1

    return direction, s_cnt, l_cnt, r_cnt, dx, dy, s_x, s_y

def read_log_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            timestamp = float(parts[0])
            magx = float(parts[1])
            magy = float(parts[2])
            magz = float(parts[3])
            yield timestamp, magx, magy, magz
            
# tmp = 0

# try:
#     input_file_path = 'left_dir.txt'  # Update with the correct path to your input log file
#     output_file_path = 'out_left.txt'  # Output log file

#     with open(output_file_path, 'a') as log_file:  # Open the output log file in append mode
#         for timestamp, magx, magy, magz in read_log_file(input_file_path):
#             if(tmp == 0):
#                 s_x = magx
#                 s_y = magy
#                 tmp = 1
#             print("----------------------------")
#             direction, s_cnt, l_cnt, r_cnt, dx, dy, s_x, s_y = get_direction(magx, magy, magz)

#             print(f"X = {magx}, Y = {magy}, Z = {magz} (gauss)")
#             print(direction)

#             # Save the values to the log file
#             # log_file.write(f"x={int(magx)}, y={int(magy)}, s_x={int(s_x)}, s_y={int(s_y)}, s={s_cnt}, l={l_cnt}, r={r_cnt}, dx={int(dx)}, dy={int(dy)}, {direction}\n")


# except KeyboardInterrupt:
#     print("Cleanup")
