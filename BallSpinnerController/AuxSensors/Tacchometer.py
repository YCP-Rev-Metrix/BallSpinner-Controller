import RPi.GPIO as GPIO
import time
from .iAuxSensor import iAuxSensor

class Tacchometer(iAuxSensor):
    def __init__(self, GPIOPin : int):
        self.INPUT_PIN = GPIOPin
        GPIO.cleanup()  # Reset GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    def readData(self): 
        #This code doesn't work, but is more of a courtesy for Sam Diskin, who tried very hard
        #To design a Light Tacchometer reader
        GPIO.add_event_detect(self.INPUT_PIN, GPIO.FALLING, bouncetime=200)
        while True:
            if GPIO.event_detected(self.INPUT_PIN):
                print("Edge detected")
            time.sleep(0.1)

    def __del__():
        GPIO.cleanup()