from time import sleep
import RPi.GPIO as GPIO

class Motor():

    def __init__(self, GPIOPin : int):
        #Set PWM Pin Motor is Connected to 
        self.GPIOPin = GPIOPin #12

        #Configure GPIO Pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(GPIOPin, GPIO.OUT)
        #1kHz
        self.PWM = GPIO.PWM(GPIOPin, 500)
        #Declare on/off State (0 = Off; 1 = On)
        self.state = False
        self.rpm = 0
    # Turns on Motor at Specified Power (Duty Cycle)
    def turnOnMotor(self, rpm = 1):
        dutyCycle = (rpm/60) * 100
        if not self.state:
            self.PWM.start(dutyCycle)
            self.state = True
            self.rpm = rpm
        else:
            print("Unable to Start Motor: Motor is Already Running")

    def turnOffMotor(self):
        if self.state:
            self.PWM.stop()
            GPIO.cleanup(self.GPIOPin)
            self.state = False
        else:
            print("Unable to Stop Motor: Motor is Not Running")

    def changeSpeed(self, rpm : float):
        #Hard-Coded Max Shunt Motor rpm
        dutyCycle = (rpm/60) * 100
        if dutyCycle > 100: dutyCycle = 100
        print("Changing Speed %i%%" % dutyCycle)
        if self.state:
            self.PWM.ChangeDutyCycle(dutyCycle)
            self.rpm = rpm
        
        else:
            print("Unable to Change Speed: Motor is Not Running")

    def rampUp(self):
        i = 0
        while i/25 < 1:
            i=i+1
            self.changeSpeed(int((i/25)*100))
            sleep(.5)