import time
import yaml
import os

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

if SIMULATION_MODE:
    # Simülasyon modu
    from utils.dummy_gpio import setmode, setwarnings, setup, output, BCM, OUT, HIGH, LOW
    print("[BUZZER] Simülasyon modu kullanılıyor")
else:
    # Gerçek donanım modu
    import RPi.GPIO as GPIO
    setmode = GPIO.setmode
    setwarnings = GPIO.setwarnings
    setup = GPIO.setup
    output = GPIO.output
    BCM = GPIO.BCM
    OUT = GPIO.OUT
    HIGH = GPIO.HIGH
    LOW = GPIO.LOW

setmode(BCM)
setwarnings(False)
setup(config['buzzer_pins']['inside'], OUT)
setup(config['buzzer_pins']['outside'], OUT)

def beep(role, pattern):
    pin = config['buzzer_pins'][role]
    for dur in pattern:
        output(pin, HIGH)
        time.sleep(dur)
        output(pin, LOW)
        time.sleep(0.1) 