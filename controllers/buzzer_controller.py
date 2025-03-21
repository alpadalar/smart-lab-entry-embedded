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
    from utils.dummy_gpio_zero import Buzzer, DigitalOutputDevice
    print("[BUZZER] Simülasyon modu kullanılıyor (gpiozero)")
else:
    try:
        # Gerçek donanım modu - önce lgpio deneyin
        import lgpio
        from gpiozero import Buzzer, DigitalOutputDevice
        from gpiozero.pins.lgpio import LGPIOFactory
        pin_factory = LGPIOFactory()
        print("[BUZZER] Gerçek donanım modu kullanılıyor (lgpio)")
    except ImportError:
        # Gerçek donanım modu - lgpio yoksa standart gpiozero
        from gpiozero import Buzzer, DigitalOutputDevice
        pin_factory = None
        print("[BUZZER] Gerçek donanım modu kullanılıyor (standart)")

# README'de belirtilen pinleri kullan
buzzer_pins = {
    "inside": 23,  # GPIO23 (Pin 16)
    "outside": 24  # GPIO24 (Pin 18)
}

# Buzzer nesnelerini oluştur
try:
    if SIMULATION_MODE:
        buzzers = {
            "inside": Buzzer(buzzer_pins["inside"]),
            "outside": Buzzer(buzzer_pins["outside"])
        }
    else:
        buzzers = {
            "inside": Buzzer(buzzer_pins["inside"], pin_factory=pin_factory),
            "outside": Buzzer(buzzer_pins["outside"], pin_factory=pin_factory)
        }
    print("[BUZZER] Buzzer sınıfı başarıyla oluşturuldu")
except Exception as e:
    print(f"[BUZZER] Buzzer oluşturulurken hata: {e}")
    print("[BUZZER] DigitalOutputDevice ile devam ediliyor...")
    
    try:
        # Buzzer sınıfı çalışmıyorsa genel dijital çıkış cihazı kullan
        if SIMULATION_MODE:
            buzzers = {
                "inside": DigitalOutputDevice(buzzer_pins["inside"], active_high=True),
                "outside": DigitalOutputDevice(buzzer_pins["outside"], active_high=True)
            }
        else:
            buzzers = {
                "inside": DigitalOutputDevice(buzzer_pins["inside"], active_high=True, pin_factory=pin_factory),
                "outside": DigitalOutputDevice(buzzer_pins["outside"], active_high=True, pin_factory=pin_factory)
            }
        print("[BUZZER] DigitalOutputDevice başarıyla oluşturuldu")
    except Exception as e:
        print(f"[BUZZER] DigitalOutputDevice oluşturulurken de hata: {e}")
        # Dummy Buzzer nesnesi
        from utils.dummy_gpio_zero import Buzzer
        buzzers = {
            "inside": Buzzer(buzzer_pins["inside"]),
            "outside": Buzzer(buzzer_pins["outside"])
        }
        print("[BUZZER] Hata nedeniyle simülasyon moduna geçildi")

def beep(role, pattern):
    """
    Buzzer ses çıkarma
    pattern: bip uzunlukları listesi (örn: [0.1, 0.1] - kısa-kısa bip)
    """
    try:
        buzzer = buzzers[role]
        
        # Buzzer sınıfının beep metodu varsa kullan
        if hasattr(buzzer, 'beep'):
            # Eğer sadece tek bir bip isteniyorsa GPIOZero'nun beep metodunu kullan
            if len(pattern) == 1:
                buzzer.beep(on_time=pattern[0], off_time=0.1, n=1, background=True)
                time.sleep(pattern[0] + 0.1)  # Bipin bitmesini bekle
            else:
                # Birden fazla bip için manuel kontrol
                for dur in pattern:
                    buzzer.on()
                    time.sleep(dur)
                    buzzer.off()
                    time.sleep(0.1)
        else:
            # DigitalOutputDevice için manuel kontrolle bip
            for dur in pattern:
                buzzer.on()
                time.sleep(dur)
                buzzer.off()
                time.sleep(0.1)
    except Exception as e:
        print(f"[BUZZER] Bip sesi çıkarma hatası: {e}") 

# Cleanup fonksiyonu - Buzzer'ları sıfırla ve kaynakları serbest bırak
def cleanup():
    """
    Buzzer kaynaklarını temizler ve serbest bırakır.
    Ana program sonlandığında çağrılır.
    """
    try:
        global buzzers
        
        # Tüm buzzer'ları kapat
        if buzzers:
            for role in buzzers:
                if buzzers[role]:
                    try:
                        if hasattr(buzzers[role], 'off'):
                            buzzers[role].off()
                        if hasattr(buzzers[role], 'close'):
                            buzzers[role].close()
                    except Exception as e:
                        print(f"[HATA] {role} buzzer kapatılırken hata: {str(e)}")
        
        # Aktif beep timerları durdur
        for timer in beep_timers:
            if timer.is_alive():
                timer.cancel()
        
        beep_timers.clear()
        
        return True
    except Exception as e:
        print(f"[HATA] Buzzer cleanup işlemi sırasında hata: {str(e)}")
        return False 