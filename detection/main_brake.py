import time
import sys
import numpy as np
import smbus
import RPi.GPIO as GPIO
import curses


input_file_path = "../result/acc_gyro/6.txt"
output_file_path = "brake_output_log6.txt"

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
    #print(f"Duration of update_display: {duration:.6f} seconds") 

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

def graph_none():
    update_display(1)

# -----------------------------------------------------------
# brake detection
# -----------------------------------------------------------


# Define the avg function
def avg(list):
    return sum(list) / len(list)

# Initialize variables
x_list = []
y_list = []
cnt = 0
s_x = 0 
s_y = 0
brake_time_th = 20
brake_diff_th = -0.2
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
    
    diff = (ax - s_x) 
    if (diff < brake_diff_th): 
        brake = True
    else: 
        brake = False
        
    return brake, s_x, s_y, cnt, start_detect_brake, diff


try:
    flag = 0
    with open(input_file_path, "r") as file, open(output_file_path, "w") as output_file:
        for line in file:
            data = line.strip().split(", ")
            timestamp = float(data[0])
            ax = float(data[1])
            ay = float(data[2])
            az = float(data[3])
            gx = float(data[4])
            gy = float(data[5])
            gz = float(data[6])
            
            print("----------------------------")
            print(f"ax: {ax}, ay: {ay}, az: {az}")
            
            # for detection
            brake, s_x, s_y, cnt, start_detect_brake, diff = detect_brake(ax, ay, az)
            if brake:
                print(f"brake")
                graph_brake()
                if flag == 0:
                    flag = 1
            else:
                print(f"stable")
                if flag == 1:
                    graph_none()
                    flag = 0


            output_file.write(f"ax = {ax}, ay = {ay}, az = {az}, diff = {diff} brake = {brake}\n")
            
            time.sleep(0.001)

except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()
except FileNotFoundError:
    print(f"Log file not found: {input_file_path}")
    sys.exit()
except Exception as e:
    print(f"An error occurred: {e}")
    GPIO.cleanup()
    exit(1)
