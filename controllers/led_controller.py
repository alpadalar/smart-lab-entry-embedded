import threading
import time
import math
import yaml
import os

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

if SIMULATION_MODE:
    # Simülasyon modu
    from utils.dummy_gpio_zero import PWMLED
    print("[LED] Simülasyon modu kullanılıyor (gpiozero)")
else:
    # Gerçek donanım modu
    from gpiozero import PWMLED

# LED nesnelerini oluştur
leds = {
    "inside": PWMLED(config['led_pins']['inside']),
    "outside": PWMLED(config['led_pins']['outside'])
}

def breathing_effect(led):
    """Nefes alıp veren LED efekti - artık pulse() ile yapıyoruz"""
    led.pulse()

def show_pattern(role, pattern, duration=2):
    """LED yanıp sönme desenini göster
    pattern: açık/kapalı durumlar listesi (Ör: [1, 0, 1, 0] - açık, kapalı, açık, kapalı)
    """
    led = leds[role]
    for state in pattern:
        if state:
            led.on()
        else:
            led.off()
        time.sleep(0.2)
    time.sleep(duration)
    led.off()

def show_color(role, color, duration=2):
    """
    color: (r, g, b) - Bu implementasyonda ortalama parlaklık kullanılır
    """
    # RGB'den parlaklık hesapla (ortalama değer)
    brightness = sum(color) / (3 * 255)
    
    led = leds[role]
    led.value = brightness
    time.sleep(duration)
    led.off()  # Kapat

def start_breathing(role):
    """Nefes alıp veren LED efektini başlat"""
    leds[role].pulse() 