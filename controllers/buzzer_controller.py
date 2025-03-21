import time
import yaml
import os

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

if SIMULATION_MODE:
    # Simülasyon modu
    from utils.dummy_gpio_zero import Buzzer
    print("[BUZZER] Simülasyon modu kullanılıyor (gpiozero)")
else:
    # Gerçek donanım modu
    from gpiozero import Buzzer

# Buzzer nesnelerini oluştur
buzzers = {
    "inside": Buzzer(config['buzzer_pins']['inside']),
    "outside": Buzzer(config['buzzer_pins']['outside'])
}

def beep(role, pattern):
    """
    Buzzer ses çıkarma
    pattern: bip uzunlukları listesi (örn: [0.1, 0.1] - kısa-kısa bip)
    """
    buzzer = buzzers[role]
    for dur in pattern:
        buzzer.on()
        time.sleep(dur)
        buzzer.off()
        time.sleep(0.1) 