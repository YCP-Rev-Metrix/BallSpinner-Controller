import RPi.GPIO as GPIO
import time

INPUT_PIN = 18

GPIO.cleanup()  # Reset GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    GPIO.add_event_detect(INPUT_PIN, GPIO.FALLING, bouncetime=200)
    while True:
        if GPIO.event_detected(INPUT_PIN):
            print("Edge detected")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting program.")
finally:
    GPIO.cleanup()