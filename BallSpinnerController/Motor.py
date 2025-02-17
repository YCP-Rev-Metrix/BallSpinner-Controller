from time import sleep
import RPi.GPIO as GPIO

class Motor():

    def __init__(self, GPIOPin : int):
        #Set PWM Pin Motor is Connected to 
        self.GPIOPin = GPIOPin #12

        #Configure GPIO Pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        #1kHz
        self.PWM = GPIO.PWM(GPIOPin, 500)
        #Declare on/off State (0 = Off; 1 = On)
        self.state = False

    # Turns on Motor at Specified Power (Duty Cycle)
    def turnOnMotor(self, dutyCycle = 100):
        if not self.state:
            self.PWM.start(dutyCycle)
            self.state = True
        else:
            print("Unable to Start Motor: Motor is Already Running")

    def turnOffMotor(self):
        if self.state:
            self.PWM.stop()
            GPIO.cleanup(self.GPIOPin)
            self.state = False
        else:
            print("Unable to Stop Motor: Motor is Not Running")

    def changeSpeed(self, dutyCycle : int):
        print("Changing Speed %i%%" % dutyCycle)
        if self.state:
            self.PWM.ChangeDutyCycle(dutyCycle)
        
        else:
            print("Unable to Change Speed: Motor is Not Running")

    def rampUp(self):
        i = 0
        while i/25 < 1:
            i=i+1
            self.changeSpeed(int((i/25)*100))
            sleep(.5)