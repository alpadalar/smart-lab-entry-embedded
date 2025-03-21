import board as pi_board
import threading
import time
import math
import yaml
from rpi_ws281x import PixelStrip, Color

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# LED strip özelliklerini tanımla
LED_COUNT = config['led_pixel_count']
LED_FREQ_HZ = 800000  # LED sinyal frekansı
LED_DMA = 10          # DMA kanalı
LED_BRIGHTNESS = 255  # 0-255 arası parlaklık ayarı
LED_INVERT = False    # Sinyal terslemesi

# LED şerit nesnelerini oluştur
pixels = {
    "inside": PixelStrip(LED_COUNT, config['led_pins']['inside'], LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS),
    "outside": PixelStrip(LED_COUNT, config['led_pins']['outside'], LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
}

# LED şeritlerini başlat
for p in pixels.values():
    p.begin()

def color_wipe(strip, color):
    """Şeritteki tüm pikselleri aynı renge boyar."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def rgb_to_color(rgb_tuple):
    """RGB tuple'dan rpi_ws281x Color nesnesine dönüştürür."""
    r, g, b = rgb_tuple
    return Color(r, g, b)

def breathing_effect(pixels_obj):
    while True:
        for i in range(0, 360, 5):
            brightness = (math.exp(math.sin(math.radians(i))) - 0.3679) / (math.e - 0.3679)
            r, g, b = [int(255 * brightness)] * 3
            color_wipe(pixels_obj, Color(r, g, b))
            time.sleep(0.05)

def show_color(role, rgb_color, duration=2):
    p = pixels[role]
    color = rgb_to_color(rgb_color)
    color_wipe(p, color)
    time.sleep(duration)
    color_wipe(p, Color(0, 0, 0))

def start_breathing(role):
    threading.Thread(target=breathing_effect, args=(pixels[role],), daemon=True).start() 