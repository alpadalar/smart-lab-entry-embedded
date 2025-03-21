import RPi.GPIO as GPIO
import time
import yaml

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(config['buzzer_pins']['inside'], GPIO.OUT)
GPIO.setup(config['buzzer_pins']['outside'], GPIO.OUT)

def beep(role, pattern):
    pin = config['buzzer_pins'][role]
    for dur in pattern:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(dur)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1) 