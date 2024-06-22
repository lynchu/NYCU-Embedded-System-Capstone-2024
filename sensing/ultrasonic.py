import RPi.GPIO as GPIO 
import time
import os

ULTRA_TRIGGER = 16
ULTRA_ECHO = 18

velocity = 343

def measure():
    GPIO.output(ULTRA_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(ULTRA_TRIGGER, GPIO.LOW)
    pulse_start = time.time()
    while GPIO.input(ULTRA_ECHO) == GPIO.LOW:
        pulse_start = time.time()
    while GPIO.input(ULTRA_ECHO) == GPIO.HIGH:
        pulse_end = time.time()

    t = pulse_end - pulse_start
    d = t*velocity
    d = (d/2)*100 # cm
    print(f"distance: {d}")

    return d

def main():
    output_folder = "../result/ultrasonic"
    os.makedirs(output_folder, exist_ok=True)
    
    output_file_path = f"{output_folder}/{time.time()}.txt"
    with open(output_file_path, "a") as output_file:
        while True:
            distance = measure()
            output_file.write(f"{time.time()}, {distance}\n")
    
def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ULTRA_TRIGGER, GPIO.OUT)
    GPIO.setup(ULTRA_ECHO, GPIO.IN)


if __name__ == "__main__":
    try:
        setup()
        main()

    except KeyboardInterrupt:
        print("Exception: KeyboardInterrupt")
    finally:
        GPIO.cleanup()