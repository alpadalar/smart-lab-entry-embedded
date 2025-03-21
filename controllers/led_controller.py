import threading
import time
import yaml
import os
from signal import pause

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

# Pin factory kontrolü
PIN_FACTORY = os.environ.get('GPIOZERO_PIN_FACTORY', 'native')

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

if SIMULATION_MODE:
    # Simülasyon modu
    from utils.dummy_gpio_zero import PWMLED, LED
    print("[LED] Simülasyon modu kullanılıyor (gpiozero)")
else:
    try:
        # Gerçek donanım modu - önce lgpio deneyin
        import lgpio
        from gpiozero import PWMLED, LED
        from gpiozero.pins.lgpio import LGPIOFactory
        pin_factory = LGPIOFactory()
        print("[LED] Gerçek donanım modu kullanılıyor (lgpio)")
    except ImportError:
        # Gerçek donanım modu - lgpio yoksa standart gpiozero
        from gpiozero import PWMLED, LED
        pin_factory = None
        print("[LED] Gerçek donanım modu kullanılıyor (standart)")

# README'de belirtilen pinleri kullan
led_pins = {
    "inside": 18,  # GPIO18 (Pin 12)
    "outside": 12  # GPIO12 (Pin 32)
}

# LED nesnelerini oluştur
try:
    if SIMULATION_MODE:
        leds = {
            "inside": PWMLED(led_pins["inside"]),
            "outside": PWMLED(led_pins["outside"])
        }
    else:
        leds = {
            "inside": PWMLED(led_pins["inside"], pin_factory=pin_factory),
            "outside": PWMLED(led_pins["outside"], pin_factory=pin_factory)
        }
except Exception as e:
    print(f"[LED] PWMLED oluşturulurken hata: {e}")
    print("[LED] Normal LED'lerle devam ediliyor...")
    try:
        # PWM çalışmıyorsa normal LED kullan
        if SIMULATION_MODE:
            leds = {
                "inside": LED(led_pins["inside"]),
                "outside": LED(led_pins["outside"])
            }
        else:
            leds = {
                "inside": LED(led_pins["inside"], pin_factory=pin_factory),
                "outside": LED(led_pins["outside"], pin_factory=pin_factory)
            }
        print("[LED] Normal LED'ler başarıyla oluşturuldu")
    except Exception as e:
        print(f"[LED] Normal LED oluşturulurken de hata: {e}")
        # Dummy PWMLED nesnesi
        from utils.dummy_gpio_zero import PWMLED
        leds = {
            "inside": PWMLED(led_pins["inside"]),
            "outside": PWMLED(led_pins["outside"])
        }
        print("[LED] Hata nedeniyle simülasyon moduna geçildi")

def _blink_pattern(led, pattern):
    """Özel blink desenini uygular"""
    for state in pattern:
        if state:
            led.on()
        else:
            led.off()
        time.sleep(0.2)

def breathing_effect(led):
    """Nefes alıp veren LED efekti - pulse() ile yapıyoruz"""
    try:
        led.pulse()
    except Exception as e:
        print(f"[LED] Nefes efekti hatası: {e}")
        # Manuel pulse efekti
        while True:
            for i in range(0, 101, 5):
                try:
                    led.value = i / 100.0
                    time.sleep(0.05)
                except:
                    led.on()
                    time.sleep(0.05)
            for i in range(100, -1, -5):
                try:
                    led.value = i / 100.0
                    time.sleep(0.05)
                except:
                    led.off()
                    time.sleep(0.05)

def show_pattern(role, pattern, duration=2):
    """LED yanıp sönme desenini göster
    pattern: açık/kapalı durumlar listesi (Ör: [1, 0, 1, 0] - açık, kapalı, açık, kapalı)
    """
    try:
        led = leds[role]
        
        # GPIOZero blink fonksiyonunu kullanmak yerine manuel kontrol ediyoruz
        # çünkü karmaşık desenler için blink yeterli değil
        _blink_pattern(led, pattern)
        time.sleep(duration)
        led.off()
    except Exception as e:
        print(f"[LED] Desen gösterme hatası: {e}")

def show_color(role, color, duration=2):
    """
    color: (r, g, b) - Bu implementasyonda ortalama parlaklık kullanılır
    """
    try:
        # RGB'den parlaklık hesapla (ortalama değer)
        brightness = sum(color) / (3 * 255)
        
        led = leds[role]
        
        # PWM kontrolü varsa
        if hasattr(led, 'value'):
            led.value = brightness
        else:
            # Normal LED ise sadece açıp kapatabiliyoruz
            if brightness > 0.5:
                led.on()
            else:
                led.off()
                
        time.sleep(duration)
        led.off()  # Kapat
    except Exception as e:
        print(f"[LED] Renk gösterme hatası: {e}")

def start_breathing(role):
    """Nefes alıp veren LED efektini başlat"""
    try:
        # GPIOZero'nun pulse metodu
        leds[role].pulse(fade_in_time=1, fade_out_time=1, n=None, background=True)
    except Exception as e:
        print(f"[LED] Nefes efekti başlatma hatası: {e}")
        # Manuel nefes efekti
        threading.Thread(target=breathing_effect, args=(leds[role],), daemon=True).start()

# Cleanup fonksiyonu - LED'leri sıfırla ve kaynakları serbest bırak
def cleanup():
    """
    LED kaynaklarını temizler ve serbest bırakır.
    Ana program sonlandığında çağrılır.
    """
    try:
        global leds, breathing_threads, pattern_timers
        
        # Devam eden tüm etkinlikleri durdur
        for role in breathing_threads:
            if breathing_threads[role] and breathing_threads[role].is_alive():
                # Breath thread'lerini durdur
                breathing_active[role] = False
                breathing_threads[role].join(timeout=1.0)
                
        # Zamanlayıcıları iptal et
        for timer in pattern_timers:
            if timer.is_alive():
                timer.cancel()
        
        # Tüm LED'leri kapat
        if leds:
            for role in leds:
                if leds[role]:
                    try:
                        if hasattr(leds[role], 'off'):
                            leds[role].off()
                        if hasattr(leds[role], 'close'):
                            leds[role].close()
                    except Exception as e:
                        print(f"[HATA] {role} LED kapatılırken hata: {str(e)}")
        
        # Değişkenleri temizle
        breathing_threads.clear()
        pattern_timers.clear()
        breathing_active.clear()
        
        return True
    except Exception as e:
        print(f"[HATA] LED cleanup işlemi sırasında hata: {str(e)}")
        return False 