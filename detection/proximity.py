import RPi.GPIO as GPIO 
import time


BUZZER = 11

dist_level1 = 50
dist_level2 = 30


# https://www.instructables.com/Raspberry-Pi-Tutorial-How-to-Use-a-Buzzer/
def buzz(duration, frequency):
    GPIO.output(BUZZER,GPIO.HIGH)
    print ("*Beep*")
    time.sleep(duration)
    GPIO.output(BUZZER,GPIO.LOW)
    time.sleep(frequency)

def main():
    
        if (distance < dist_level2):
            buzz(0.1, 0.25)
        elif (distance < dist_level1):
            buzz(0.1, 0.75)
        
def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUZZER,GPIO.OUT)


if __name__ == "__main__":
    try:
        setup()
        main()

    except KeyboardInterrupt:
        print("Exception: KeyboardInterrupt")
    finally:
        GPIO.cleanup()