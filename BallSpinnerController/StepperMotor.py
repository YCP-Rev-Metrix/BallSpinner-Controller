from .iMotor import iMotor
import RPi.GPIO as GPIO

class StepperMotor(iMotor):
# Pin configuration (using BCM numbering)
#DIR_PIN = 20     # Direction pin (CW/CCW)
#STEP_PIN = 35    # Using a valid pin (adjust if necessary)
#ENABLE_PIN = 16  # Enable pin


#Set PWM Pin Motor is Connected to 
#GPIOPin = STEP_PIN #12
#PWM = 400
#Configure GPIO Pin




    def __init__(self, GPIOPin : int):
        #Set PWM Pin Motor is Connected to 
        self.GPIOPin = GPIOPin #12
        self.PWM = 400

        #Configure GPIO Pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(GPIOPin, GPIO.OUT)
        #1kHz
        self.PWM : GPIO.PWM = GPIO.PWM(GPIOPin, 400)
        #Declare on/off State (0 = Off; 1 = On)
        self.state = False

    def turnOnMotor(self, rpm = 1):
        if not self.state:
            if int(rpm) != 0:
                self.PWM.ChangeFrequency(rpm * 400)
                self.PWM.start(50)
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
            self.PWM.ChangeFrequency(rpm * 400)
            

   
        

    def rampUp():
        pass

    def turnOffMotor():
        pass

