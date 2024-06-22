import RPi.GPIO as GPIO 
import time

input_file_path = "../result/ultrasonic/3.txt"
output_file_path = "ultrasonic_output_log3.txt"

BUZZER = 11

dist_level1 = 80
dist_level2 = 50


# https://www.instructables.com/Raspberry-Pi-Tutorial-How-to-Use-a-Buzzer/
def buzz(duration, frequency):
    GPIO.output(BUZZER,GPIO.HIGH)
    #print ("*Beep*")
    time.sleep(duration)
    GPIO.output(BUZZER,GPIO.LOW)
    time.sleep(frequency)

def main(distance):
    offset = 1
    if (distance < dist_level2):
        buzz(0.1, 0.25)
        print("too close")
        offset = 35
    elif (distance < dist_level1):
        buzz(0.1, 0.75)
        print("close")
        offset= 85 
    return offset
def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUZZER,GPIO.OUT)


if __name__ == "__main__":
    try:
        setup()
        data_list = []
        with open(input_file_path, "r") as file, open(output_file_path, "w") as output_file:
            for line in file:
                data = line.strip().split(", ")
                timestamp = float(data[0])
                distance = float(data[1])
                s = "none"
                if (distance < dist_level2):
                    s = "too close"
                elif (distance < dist_level1):
                    s = "close"
                data_list.append([timestamp, distance, s])
                output_file.write(f"distance = {distance}, message = {s}\n")
            
            i = 0
            while i < len(data_list):
                timestamp, distance, s = data_list[i]
                print("----------------------------")
                print(f"distance: {distance}")
                offset = main(distance)
                i = i + offset
                time.sleep(0.001)
                

    except KeyboardInterrupt:
        print("Exception: KeyboardInterrupt")
    finally:
        GPIO.cleanup()
