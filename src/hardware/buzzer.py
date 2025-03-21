import RPi.GPIO as GPIO
import time
import threading
from src.config import (
    INSIDE_BUZZER_PIN, OUTSIDE_BUZZER_PIN,
    BUZZER_DURATIONS
)

class Buzzer:
    def __init__(self, pin, is_inside=True):
        self.pin = pin
        self.is_inside = is_inside
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        
    def beep(self, duration):
        """Belirtilen süre boyunca bip sesi çıkarır"""
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.pin, GPIO.LOW)
        
    def success_beep(self):
        """Başarılı geçiş bip sesi"""
        self.beep(BUZZER_DURATIONS["SUCCESS"])
        time.sleep(0.1)
        self.beep(BUZZER_DURATIONS["SUCCESS"])
        
    def fail_beep(self):
        """Başarısız geçiş bip sesi"""
        self.beep(BUZZER_DURATIONS["FAIL"])
        
    def error_beep(self):
        """Hata bip sesi"""
        self.beep(BUZZER_DURATIONS["ERROR"])
        
    def cleanup(self):
        """GPIO pinlerini temizler"""
        GPIO.cleanup(self.pin) 