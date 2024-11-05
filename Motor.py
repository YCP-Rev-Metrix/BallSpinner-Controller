
import RPi.GPIO as GPIO

class Motor():

    def Motor(self, GPIOPin):
        #Set PWM Pin Motor is Connected to 
        self.GPIOPin = GPIOPin #12

        #Configure GPIO Pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIOPin, GPIO.OUT)


        self.PWM = GPIO.PWM(GPIOPin, 1000)
        #Declare on/off State (0 = Off; 1 = On)
        self.state = False

    # Turns on Motor at Power (100% Duty Cycle)
    def turnOnMotor(self):
        if not self.state:
            self.PWM.start(100)
            self.state = True
        else:
            print("Unable to Start Motor: Motor is Already Running")

    # Turns on Motor at Specified Power (Duty Cycle)
    def turnOnMotor(self, dutyCycle : int):
        if not self.state:
            self.PWM.start(dutyCycle)
            self.state = True
        else:
            print("Unable to Start Motor: Motor is Already Running")

    def turnOffMotor(self):
        if self.state:
            self.PWM.stop()
            self.state = False
        else:
            print("Unable to Stop Motor: Motor is Not Running")

    def changeSpeed(self, dutyCycle : int):
        if self.state:
            self.PWM.ChangeDutyCycle(dutyCycle/100)
        else:
            print("Unable to Change Speed: Motor is Not Running")
