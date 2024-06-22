import smbus
import time
import RPi.GPIO as GPIO
import curses

import time
from math import *

input_file_path = "../result/mag/3.txt"
output_file_path = "turn_output_log3.txt"


# -----------------------------------------------------------
# LED control
# -----------------------------------------------------------

# Define I2C pins
IIC_SCL = 5 # serial clock
IIC_SDA = 3 # serial data

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IIC_SCL, GPIO.OUT)
GPIO.setup(IIC_SDA, GPIO.OUT)

# Table data
table = [
    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], # all on
    [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], # all off
    [0x00, 0x00, 0x00, 0x00, 0x00, 0x81, 0xC3, 0x66, 0x3C, 0x18, 0x81, 0xC3, 0x66, 0x3C, 0x18, 0x00], # right
    [0x00, 0x18, 0x3C, 0x66, 0xC3, 0x81, 0x18, 0x3C, 0x66, 0xC3, 0x81, 0x00, 0x00, 0x00, 0x00, 0x00], # left
    [0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xc3, 0xC3, 0xC3, 0xC3, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00] # break(square)
]

# Initialize I2C (SMBus)
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

def iic_start():
    GPIO.output(IIC_SCL, GPIO.LOW)
    time.sleep(0.00003)
    GPIO.output(IIC_SDA, GPIO.HIGH)
    time.sleep(0.00003)
    GPIO.output(IIC_SCL, GPIO.HIGH)
    time.sleep(0.00003)
    GPIO.output(IIC_SDA, GPIO.LOW)
    time.sleep(0.00003)

def iic_send(send_data):
    for i in range(8):
        GPIO.output(IIC_SCL, GPIO.LOW)
        time.sleep(0.00003)
        if send_data & 0x01:
            GPIO.output(IIC_SDA, GPIO.HIGH)
        else:
            GPIO.output(IIC_SDA, GPIO.LOW)
        time.sleep(0.00003)
        GPIO.output(IIC_SCL, GPIO.HIGH)
        time.sleep(0.00003)
        send_data = send_data >> 1

def iic_end():
    # GPIO.output(IIC_SCL, GPIO.LOW)
    GPIO.output(IIC_SCL, GPIO.LOW)
    time.sleep(0.00003)
    GPIO.output(IIC_SDA, GPIO.LOW)
    time.sleep(0.00003)
    GPIO.output(IIC_SCL, GPIO.HIGH)
    time.sleep(0.00003)
    GPIO.output(IIC_SDA, GPIO.HIGH)
    time.sleep(0.00003)

def update_display(data_line):
    start_time = time.time()
    
    #print("PRINT table[", data_line, "]")
    iic_start()
    iic_send(0x40)  # Set the address to add automatically 1
    iic_end()

    iic_start()
    iic_send(0xc0)  # Set the initial address to 0

    for i in range(16):
        #print(f"#{i+1}: {hex(table[data_line][i])}")
        iic_send(table[data_line][i])
        # iic_send(0x0F)
 
    
    iic_end()

    iic_start()
    iic_send(0x8A)  # Display brightness setting
    iic_end()
    
    end_time = time.time()  
    duration = end_time - start_time  
    print(f"Duration of update_display: {duration:.6f} seconds") 

def graph_right():
    update_display(2)
    time.sleep(1)
    update_display(1)
    time.sleep(0.5)

def graph_left():
    update_display(3)
    time.sleep(1)
    update_display(1)
    time.sleep(0.5)

def graph_brake():
    update_display(4)

# -----------------------------------------------------------
# turn decision
# -----------------------------------------------------------

def read_log_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            timestamp = float(parts[0])
            magx = float(parts[1])
            magy = float(parts[2])
            magz = float(parts[3])
            yield timestamp, magx, magy, magz


x_list = []
y_list = []
s_x = 0  # the x value for straight
s_y = 0

cnt = 0 # for list
r_cnt = 0  # count how long it has heading right
l_cnt = 0
s_cnt = 0
turn_time_th = 60  # about to turn for more than this time -> turn
stra_time_th = 50
x_angl_th = 30  # turn for more than this angl -> about to turn
y_angl_th = 30
s_angel_th = 30  # turn less than it -> straight
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
    dx = magx - s_x 
    dy = magy - s_y
    # print("dx = ", dx)
    # print("dy = ", dy)
    # print("s_cnt = ", s_cnt)
    # print("l_cnt = ", l_cnt)
    # print("r_cnt = ", r_cnt)
    # print("s_x = ", s_x)
    # print("s_y = ", s_y)
    if dx < s_angel_th and dy < s_angel_th and -dx < s_angel_th and -dy < s_angel_th:
        s_cnt += 1
    elif dx > x_angl_th or dy > y_angl_th:
        l_cnt += 1
    elif -dx > x_angl_th or -dy > y_angl_th:
        r_cnt += 1

    return direction, s_cnt, l_cnt, r_cnt, dx, dy, s_x, s_y

tmp = 0
data_list = []
try:
    with open(output_file_path, 'a') as output_file:  # Open the output log file in append mode
        for timestamp, magx, magy, magz in read_log_file(input_file_path):  
            if(tmp == 0):
                s_x = magx
                s_y = magy
                tmp = 1
            
            direction, s_cnt, l_cnt, r_cnt, dx, dy, s_x, s_y = get_direction(magx, magy, magz)

            # Append the values to the list
            data_list.append([timestamp, magx, magy, magz, dx, dy, s_cnt, l_cnt, r_cnt, direction])
            # Save the values to the log file
            #output_file.write(f"mx = {magx}, my = {magy}, mz = {magz}, direction = {direction}\n")
            output_file.write(f"dx = {dx}, dy = {dy},  s_cnt = {s_cnt}, l_cnt = {l_cnt}, r_cnt = {r_cnt}, direction = {direction}\n")
            

        i = 0

        # Use a while loop to process data_list with controlled index increment
        while i < len(data_list):

            timestamp, magx, magy, magz, dx, dy, s_cnt, l_cnt, r_cnt, direction = data_list[i]

            
            print("----------------------------")
            
            if (direction == "left"):
                graph_left()
                i = i + 300 # 1.5/0.005
            elif (direction == "right"):
                graph_right()
                i = i + 300
            else:
                i += 1
            
            print(f"mx: {magx}, my: {magy}, mz: {magz}")
            print(direction)

            time.sleep(0.005)
            
except KeyboardInterrupt:
    print("Cleanup")