import neopixel
import board as pi_board
import threading
import time
import math
import yaml

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

pin_map = {
    config['led_pins']['inside']: pi_board.D18,
    config['led_pins']['outside']: pi_board.D19
}

pixels = {
    "inside": neopixel.NeoPixel(pin_map[config['led_pins']['inside']], config['led_pixel_count'], auto_write=False),
    "outside": neopixel.NeoPixel(pin_map[config['led_pins']['outside']], config['led_pixel_count'], auto_write=False)
}

def breathing_effect(pixels_obj):
    while True:
        for i in range(0, 360, 5):
            brightness = (math.exp(math.sin(math.radians(i))) - 0.3679) / (math.e - 0.3679)
            color = tuple(int(255 * brightness) for _ in range(3))
            pixels_obj.fill(color)
            pixels_obj.show()
            time.sleep(0.05)

def show_color(role, color, duration=2):
    p = pixels[role]
    p.fill(color)
    p.show()
    time.sleep(duration)
    p.fill((0, 0, 0))
    p.show()

def start_breathing(role):
    threading.Thread(target=breathing_effect, args=(pixels[role],), daemon=True).start() 