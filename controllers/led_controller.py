import RPi.GPIO as GPIO
import threading
import time
import math
import yaml

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# GPIO ayarlarını yap
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED pinlerini ayarla
GPIO.setup(config['led_pins']['inside'], GPIO.OUT)
GPIO.setup(config['led_pins']['outside'], GPIO.OUT)

# PWM nesnelerini oluştur
pwm_leds = {
    "inside": GPIO.PWM(config['led_pins']['inside'], 100),  # 100 Hz
    "outside": GPIO.PWM(config['led_pins']['outside'], 100)  # 100 Hz
}

# PWM başlat
for led in pwm_leds.values():
    led.start(0)  # %0 duty cycle (kapalı)

def breathing_effect(led_pwm):
    """Nefes alıp veren LED efekti"""
    while True:
        for i in range(0, 101, 5):  # 0'dan 100'e
            led_pwm.ChangeDutyCycle(i)
            time.sleep(0.05)
        for i in range(100, -1, -5):  # 100'den 0'a
            led_pwm.ChangeDutyCycle(i)
            time.sleep(0.05)

def show_pattern(role, pattern, duration=2):
    """LED yanıp sönme desenini göster
    pattern: açık/kapalı durumlar listesi (Ör: [1, 0, 1, 0] - açık, kapalı, açık, kapalı)
    """
    led_pin = config['led_pins'][role]
    for state in pattern:
        GPIO.output(led_pin, state)
        time.sleep(0.2)
    time.sleep(duration)
    GPIO.output(led_pin, 0)  # Kapat

def show_color(role, color, duration=2):
    """
    color: (r, g, b) - Bu basit implementasyonda sadece parlaklık kullanılır
    """
    # RGB'den parlaklık hesapla (ortalama değer)
    brightness = sum(color) / (3 * 255) * 100
    
    pwm_led = pwm_leds[role]
    pwm_led.ChangeDutyCycle(brightness)
    time.sleep(duration)
    pwm_led.ChangeDutyCycle(0)  # Kapat

def start_breathing(role):
    """Nefes alıp veren LED efektini başlat"""
    threading.Thread(target=breathing_effect, args=(pwm_leds[role],), daemon=True).start() 