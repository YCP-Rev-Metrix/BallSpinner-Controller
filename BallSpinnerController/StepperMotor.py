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




    def __init__(self, GPIOPin):
        #Set PWM Pin Motor is Connected to 
        self.GPIOPin = GPIOPin #12
        self.PWM = 400
        #Configure GPIO Pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        
        GPIO.setup(GPIOPin, GPIO.OUT)
        #1kHz
        self.PWM = GPIO.PWM(GPIOPin, 400)
        #Declare on/off State (0 = Off; 1 = On)
        self.state = False

    def changeSpeed(self, rpm : int):
        self.PWM.ChangeFrequence(rpm * 400)

    def turnOnMotor(self, freq=100):
        self.PWM.ChangeFrequency(freq)
        self.PWM.start(50)

    def rampUp():
        pass

    def turnOffMotor():
        pass

