from .iMotor import iMotor
import RPi.GPIO as GPIO

class StepperMotor(iMotor):

    DIP_Frequecy = 3200



    def __init__(self, GPIOPin : int):
        #Set PWM Pin Motor is Connected to 
        self.GPIOPin = GPIOPin #12
        self.freqMultiplier = 3200 #Change to DIP frequency

        #Configure GPIO Pin
        GPIO.setwarnings(False)
        #GPIO.setmode(GPIO.BCM)
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(GPIOPin, GPIO.OUT)
        #1kHz
        self.PWM : GPIO.PWM = GPIO.PWM(GPIOPin, self.freqMultiplier)
        #Declare on/off State (0 = Off; 1 = On)
        self.state = False
        self.rpm = 0

    def turnOnMotor(self, rpm = 1):
        if not self.state:
            if int(rpm) != 0:
                self.PWM.ChangeFrequency(rpm * self.freqMultiplier)
                self.PWM.start(50)
                self.rpm = rpm

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
            
    def changeSpeed(self, rpm : float):
        self.rpm = rpm
        if rpm > 0:
            if self.rpm == 0.0 :
                self.turnOnMotor(self.rpm)
            self.PWM.ChangeFrequency(rpm * self.freqMultiplier / 60)
            self.rpm = rpm


   
        

    def rampUp():
        pass

   

