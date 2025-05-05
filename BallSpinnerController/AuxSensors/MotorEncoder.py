import pigpio
import time
from .iAuxSensor import iAuxSensor
import threading

class MotorEncoder(iAuxSensor):
    # GPIO pins
    PIN_A = 25
    PIN_B = 27
    PIN_I = 7

    def __init__(self, PIN_A = 25, PIN_B = 27, PIN_I = 7):
        self.pi = pigpio.pi()
        self.PIN_B = PIN_B
        self.PIN_A = PIN_A
        self.PIN_I = PIN_I

        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon")

        # Encoder state
        self.pulses = 0
        self.last_index_time = None
        
        # Set up GPIOs
        self.pi.set_mode(PIN_A, pigpio.INPUT)
        self.pi.set_mode(PIN_B, pigpio.INPUT)
        self.pi.set_mode(PIN_I, pigpio.INPUT)

        self.pi.set_pull_up_down(PIN_A, pigpio.PUD_UP)
        self.pi.set_pull_up_down(PIN_B, pigpio.PUD_UP)
        self.pi.set_pull_up_down(PIN_I, pigpio.PUD_UP)

        # Set callbacks
        cb_a = self.pi.callback(PIN_A, pigpio.RISING_EDGE, self.pulse_a)
       # cb_i = self.pi.callback(PIN_I, pigpio.RISING_EDGE, self.index_callback)

        self.CPR = 500
        self.rpm = 0
        self.t = threading.Timer(1.0,self.index_callback)
        self.t.start()

    # Callback functions
    def pulse_a(self, Blah, moreBlah, moreMoreBlah):
        b_level = self.pi.read(self.PIN_B)
        #print("Tick")
        self.pulses += 1
    

    def index_callback(self, Blah = None, moreBlah = None, moreMoreBlah = None):
        #RPM = (Pulses / Time Interval) * 60 / Pulses Per Revolution (PPR)
        now = time.time()
        self.rpm = (self.pulses ) * 60 / self.CPR
        #print(f"RPM: {self.rpm:.2f}, Position since last index: {self.pulses}")
        self.last_index_time = now
        self.pulses = 0  # Reset position per revolution if you want
        del self.t
        self.t = threading.Timer(1.0,self.index_callback)
        self.t.start()

    def stopSenosr(self):

       #cb_a.cancel()
        #cb_i.cancel()
        self.pi.stop()

    def readData(self):
        return self.rpm