import RPi.GPIO as GPIO
import time
import usbrelay_py
from src.config import (
    INSIDE_LED_PIN, OUTSIDE_LED_PIN,
    INSIDE_BUZZER_PIN, OUTSIDE_BUZZER_PIN,
    INSIDE_NFC_CHANNEL, OUTSIDE_NFC_CHANNEL,
    RELAY_TRIGGER_TIME
)
from src.nfc_reader import NFCReader

def setup_gpio():
    """GPIO pinlerini ayarla"""
    GPIO.setmode(GPIO.BCM)
    
    # LED pinleri
    GPIO.setup(INSIDE_LED_PIN, GPIO.OUT)
    GPIO.setup(OUTSIDE_LED_PIN, GPIO.OUT)
    
    # Buzzer pinleri
    GPIO.setup(INSIDE_BUZZER_PIN, GPIO.OUT)
    GPIO.setup(OUTSIDE_BUZZER_PIN, GPIO.OUT)
    
    # Başlangıçta tüm çıkışları kapat
    GPIO.output(INSIDE_LED_PIN, GPIO.LOW)
    GPIO.output(OUTSIDE_LED_PIN, GPIO.LOW)
    GPIO.output(INSIDE_BUZZER_PIN, GPIO.LOW)
    GPIO.output(OUTSIDE_BUZZER_PIN, GPIO.LOW)

def trigger_relays():
    """Röleleri tetikle"""
    try:
        # Bağlı röle kartlarını bul
        boards = usbrelay_py.board_details()
        
        # Her kart için röleleri kontrol et
        for board_id, num_relays in boards:
            # Röleleri aç
            for relay in range(1, num_relays + 1):
                usbrelay_py.board_control(board_id, relay, 1)
            
            # Bekle
            time.sleep(RELAY_TRIGGER_TIME)
            
            # Röleleri kapat
            for relay in range(1, num_relays + 1):
                usbrelay_py.board_control(board_id, relay, 0)
                
    except Exception as e:
        print(f"Röle hatası: {e}")

def success_effect(is_inside):
    """Başarılı kart okuma efektleri"""
    led_pin = INSIDE_LED_PIN if is_inside else OUTSIDE_LED_PIN
    buzzer_pin = INSIDE_BUZZER_PIN if is_inside else OUTSIDE_BUZZER_PIN
    
    # LED ve buzzer efektleri
    GPIO.output(led_pin, GPIO.HIGH)
    GPIO.output(buzzer_pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(buzzer_pin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(led_pin, GPIO.LOW)

def main():
    """Ana program"""
    try:
        # GPIO ayarları
        setup_gpio()
        
        # NFC okuyucuları başlat
        inside_nfc = NFCReader(INSIDE_NFC_CHANNEL)
        outside_nfc = NFCReader(OUTSIDE_NFC_CHANNEL)
        
        print("Sistem başlatıldı. Kart bekleniyor...")
        
        while True:
            try:
                # İç NFC okuyucuyu kontrol et
                inside_uid = inside_nfc.read_card()
                if inside_uid:
                    print(f"İç NFC: Kart okundu! UID: {inside_uid}")
                    success_effect(True)
                    trigger_relays()
                    continue
                
                # Dış NFC okuyucuyu kontrol et
                outside_uid = outside_nfc.read_card()
                if outside_uid:
                    print(f"Dış NFC: Kart okundu! UID: {outside_uid}")
                    success_effect(False)
                    trigger_relays()
                    continue
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Döngü hatası: {e}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Program hatası: {e}")
    finally:
        # Kaynakları temizle
        inside_nfc.cleanup()
        outside_nfc.cleanup()
        GPIO.cleanup()

if __name__ == "__main__":
    main() 