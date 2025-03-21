import time
from src.config import (
    LED_COUNT, INSIDE_LED_PIN, OUTSIDE_LED_PIN,
    COLORS, LED_DURATIONS
)
import board
import neopixel
import threading

class LEDStrip:
    def __init__(self, pin, is_inside=True):
        self.pixels = neopixel.NeoPixel(pin, LED_COUNT)
        self.is_inside = is_inside
        self.breathing_thread = None
        self.stop_breathing = False
        
    def start_breathing(self):
        """Beyaz nefes alma efektini başlatır"""
        if self.breathing_thread and self.breathing_thread.is_alive():
            return
            
        self.stop_breathing = False
        self.breathing_thread = threading.Thread(target=self._breathing_effect)
        self.breathing_thread.daemon = True
        self.breathing_thread.start()
        
    def stop_breathing_effect(self):
        """Nefes alma efektini durdurur"""
        self.stop_breathing = True
        if self.breathing_thread:
            self.breathing_thread.join()
            
    def _breathing_effect(self):
        """Beyaz nefes alma efekti"""
        while not self.stop_breathing:
            for i in range(0, 255, 5):
                if self.stop_breathing:
                    break
                self.pixels.fill((i, i, i))
                time.sleep(0.05)
            for i in range(255, 0, -5):
                if self.stop_breathing:
                    break
                self.pixels.fill((i, i, i))
                time.sleep(0.05)
                
    def show_success(self):
        """Başarılı geçiş efekti"""
        self.stop_breathing_effect()
        self.pixels.fill(COLORS["GREEN"])
        time.sleep(LED_DURATIONS["SUCCESS"])
        self.start_breathing()
        
    def show_fail(self):
        """Başarısız geçiş efekti"""
        self.stop_breathing_effect()
        self.pixels.fill(COLORS["BLUE"])
        time.sleep(LED_DURATIONS["FAIL"])
        self.start_breathing()
        
    def show_error(self):
        """Hata efekti"""
        self.stop_breathing_effect()
        self.pixels.fill(COLORS["RED"])
        time.sleep(LED_DURATIONS["ERROR"])
        self.start_breathing() 