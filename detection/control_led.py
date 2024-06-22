import smbus
import time
import RPi.GPIO as GPIO
import curses

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
    
    print("PRINT table[", data_line, "]")
    iic_start()
    iic_send(0x40)  # Set the address to add automatically 1
    iic_end()

    iic_start()
    iic_send(0xc0)  # Set the initial address to 0

    for i in range(16):
        print(f"#{i+1}: {hex(table[data_line][i])}")
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

def graph_none():
    update_display(1)

def main():    
    while True:
        graph_right()

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         # iic_end()
        
#         GPIO.cleanup()
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         GPIO.cleanup()
#         exit(1)