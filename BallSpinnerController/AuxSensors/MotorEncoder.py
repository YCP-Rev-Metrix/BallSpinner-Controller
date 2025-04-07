import pigpio
import time

# GPIO pins
PIN_A = 15
PIN_B = 27
PIN_I = 14

# Init
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Failed to connect to pigpio daemon")

# Encoder state
position = 0
last_index_time = None

# Callback functions
def pulse_a(gpio, level, tick):
    global position
    b_level = pi.read(PIN_B)
    if b_level == 1:
        position += 1
    else:
        position -= 1

def index_callback(gpio, level, tick):
    global last_index_time, position
    now = time.time()
    if last_index_time is not None:
        dt = now - last_index_time
        rpm = 60 / dt
        print(f"RPM: {rpm:.2f}, Position since last index: {position}")
    last_index_time = now
    position = 0  # Reset position per revolution if you want

# Set up GPIOs
pi.set_mode(PIN_A, pigpio.INPUT)
pi.set_mode(PIN_B, pigpio.INPUT)
pi.set_mode(PIN_I, pigpio.INPUT)

pi.set_pull_up_down(PIN_A, pigpio.PUD_UP)
pi.set_pull_up_down(PIN_B, pigpio.PUD_UP)
pi.set_pull_up_down(PIN_I, pigpio.PUD_UP)

# Set callbacks
cb_a = pi.callback(PIN_A, pigpio.RISING_EDGE, pulse_a)
cb_i = pi.callback(PIN_I, pigpio.RISING_EDGE, index_callback)

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    cb_a.cancel()
    cb_i.cancel()
    pi.stop()
