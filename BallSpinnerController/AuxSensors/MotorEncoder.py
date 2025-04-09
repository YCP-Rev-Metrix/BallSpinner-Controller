import pigpio
import time
from .iAuxSensor import iAuxSensor

class MotorEncoder(iAuxSensor):
    # GPIO pins
    PIN_A = 15
    PIN_B = 27
    PIN_I = 14

    def __init__(self, PIN_A = 15, PIN_B = 27, PIN_I = 14):
        self.pi = pigpio.pi()
        self.PIN_B = PIN_B
        self.PIN_A = PIN_A
        self.PIN_I = PIN_I

        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon")

        # Encoder state
        self.position = 0
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
        cb_i = self.pi.callback(PIN_I, pigpio.RISING_EDGE, self.index_callback)
        self.rpm = 0

    # Callback functions
    def pulse_a(self, gpio, level, tick):
        self.position
        b_level = self.pi.read(self.PIN_B)
        if b_level == 1:
            self.position += 1
        else:
            self.position -= 1

    def index_callback(self, gpio, level, tick):
        now = time.time()
        if self.last_index_time is not None:
            dt = now - self.last_index_time
            self.rpm = 60 / dt
            print(f"RPM: {self.rpm:.2f}, Position since last index: {self.position}")
        self.last_index_time = now
        self.position = 0  # Reset position per revolution if you want

    
    def stopSenosr(self):

       #cb_a.cancel()
        #cb_i.cancel()
        self.pi.stop()

    def readData(self):
        return self.rpm