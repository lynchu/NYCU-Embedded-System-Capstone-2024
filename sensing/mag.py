#!/usr/bin/python3
# mag direction
import smbus
import time
from math import *
import os

bus = smbus.SMBus(1);            # 0 for R-Pi Rev. 1, 1 for Rev. 2

# the following address is defined by datasheet
# HMC5883L (Magnetometer) constants
HMC5883L_ADDRESS = 0x1E  # I2C address

HMC5883L_CRA = 0x00  # write CRA(00), Configuration Register A
HMC5883L_CRB = 0x01  # write CRB(01), Configuration Register B
HMC5883L_MR = 0x02  # write Mode(02)
HMC5883L_DO_X_H = 0x03  # Data Output
HMC5883L_DO_X_L = 0x04
HMC5883L_DO_Z_H = 0x05
HMC5883L_DO_Z_L = 0x06
HMC5883L_DO_Y_H = 0x07
HMC5883L_DO_Y_L = 0x08

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

class IMU(object):

    def write_byte(self, adr, value):
        bus.write_byte_data(self.ADDRESS, adr, value)

    def read_byte(self, adr):
        return bus.read_byte_data(self.ADDRESS, adr)

    def read_word(self, adr, rf=1):
        # rf=1 Little Endian Format, rf=0 Big Endian Format
        if rf == 1:
            # acc, gyro
            low = self.read_byte(adr)
            high = self.read_byte(adr + 1)
        else:
            # compass
            high = self.read_byte(adr)
            low = self.read_byte(adr + 1)
        val = (high << 8) + low
        return val

    def read_word_2c(self, adr, rf=1):
        val = self.read_word(adr, rf)
        if val & (1 << 16 - 1):
            return val - (1 << 16)
        else:
            return val

class gy801(object):
    def __init__(self):
        self.compass = HMC5883L()
        # self.accel = ADXL345()

class HMC5883L(IMU):

    ADDRESS = HMC5883L_ADDRESS

    def __init__(self):
        # Class Properties
        self.X = None
        self.Y = None
        self.Z = None
        self.angle = None
        self.Xoffset = 106.5
        self.Yoffset = -469.0
        self.Zoffset = -29.0

        # Declination Angle
        self.angle_offset = (-1 * (4 + (32 / 60))) / (180 / pi)
        # Formula: (deg + (min / 60.0)) / (180 / M_PI);
        # ex: Hsinchu = Magnetic Declination: -4 deg, 32 min
        # declinationAngle = ( -1 * (4 + (32/60))) / (180 / pi)
        # http://www.magnetic-declination.com/

        ## @@@
        self.scale = 0.92  # convert bit value(LSB) to gauss. DigitalResolution

        # Configuration Register A
        self.write_byte(HMC5883L_CRA, 0b01110000)
        # CRA6-CRA5 = 11 -> 8 samples per measurement
        # CRA4-CRA2 = 100 -> Data Output Rate = 15Hz
        # CRA1-CRA0 = 00 -> Normal measurement configuration (Default)

        # Configuration Register B
        self.write_byte(HMC5883L_CRB, 0b00100000)
        # CRB7-CRB5 = 001 (Gain Configuration Bits) -> Gain=1090(LSb/Gauss), default
        # ps. output range = -2048 to 2047

        # Mode Register
        self.write_byte(HMC5883L_MR, 0b00000000)
        # MR1-MR0 = 00 (Mode Select Bits) -> Continuous-Measurement Mode.

    def getX(self):
        self.X = (self.read_word_2c(HMC5883L_DO_X_H, rf=0) - self.Xoffset) * self.scale
        return self.X

    def getY(self):
        self.Y = (self.read_word_2c(HMC5883L_DO_Y_H, rf=0) - self.Yoffset) * self.scale
        return self.Y

    def getZ(self):
        self.Z = (self.read_word_2c(HMC5883L_DO_Z_H, rf=0) - self.Zoffset) * self.scale
        return self.Z

    def getHeading(self):
        bearing = degrees(atan2(self.getY(), self.getX()))

        if bearing < 0:
            bearing += 360
        if bearing > 360:
            bearing -= 360
        self.angle = bearing + self.angle_offset
        return self.angle


try:
    sensors = gy801()
    compass = sensors.compass

    output_folder = "../result/mag"
    os.makedirs(output_folder, exist_ok=True)
    
    output_file_path = f"{output_folder}/{time.time()}.txt"
    with open(output_file_path, "a") as log_file:  # Open the log file in append mode
        while True:
            print("----------------------------")
            magx = compass.getX()
            magy = compass.getY()
            magz = compass.getZ()
            # direction, s_cnt, l_cnt, r_cnt, dx, dy, s_x, s_y = get_direction(magx, magy, magz)

            print("X = %d ," % (magx)),
            print("Y = %d ," % (magy)),
            print("Z = %d ," % (magz))
            # print(direction)

            # Save the values to the log file
            log_file.write(f"{time.time()}, {magx}, {magy}, {magz}\n")

            time.sleep(0.005)

except KeyboardInterrupt:
    print("Cleanup")