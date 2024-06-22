# coding: utf-8
## @package faboMPU9250
#  This is a library for the FaBo 9AXIS I2C Brick.
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

import libmpu9250
import time
import sys
import os

import numpy as np

mpu9250 = libmpu9250.MPU9250()

try:
    output_folder = "../result/acc_gyro"
    os.makedirs(output_folder, exist_ok=True)
    
    output_file_path = f"{output_folder}/{time.time()}.txt"
    with open(output_file_path, "a") as log_file:  # Open the log file in append mode
        while True:
            print("----------------------------")
           
            accel = mpu9250.readAccel()
            ax = accel['x']
            ay = accel['y']
            az = accel['z']
            
            gyro = mpu9250.readGyro()
            gx = gyro['x']
            gy = gyro['y']
            gz = gyro['z']
            
            # Print the values
            print(f"ax = {ax}, ay = {ay}, az = {az}")
            print(f"gx = {gx}, gy = {gy}, gz = {gz}")
            
            # Save the values to the log file
            log_file.write(f"{time.time()}, {ax}, {ay}, {az}, {gx}, {gy}, {gz}\n")
            
            time.sleep(0.001)
            
            
            
except KeyboardInterrupt:
    sys.exit()
