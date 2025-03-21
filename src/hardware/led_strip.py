import time
from rpi_ws281x import *
from src.config import (
    LED_COUNT, INSIDE_LED_PIN, OUTSIDE_LED_PIN,
    COLORS, LED_DURATIONS
)

class LEDStrip:
    def __init__(self, pin, is_inside=True):
        self.is_inside = is_inside
        self.pin = pin
        
        # LED şerit başlatma
        self.strip = Adafruit_NeoPixel(
            LED_COUNT, self.pin, 800000, 10, False, 255, 0
        )
        self.strip.begin()
        self.strip.show()
        
    def set_color(self, color_name):
        """LED şeridi belirtilen renge ayarlar"""
        if color_name not in COLORS:
            return
            
        color = COLORS[color_name]
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, Color(color[0], color[1], color[2]))
        self.strip.show()
        
    def flash(self, color_name, duration=None):
        """LED şeridi belirtilen renkte yanıp söndürür"""
        if color_name not in COLORS:
            return
            
        if duration is None:
            duration = LED_DURATIONS.get(color_name, 0.5)
            
        self.set_color(color_name)
        time.sleep(duration)
        self.set_color("OFF")
        
    def cleanup(self):
        """LED şeridi temizler"""
        self.set_color("OFF") 