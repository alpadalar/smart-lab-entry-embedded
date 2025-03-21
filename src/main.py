import time
import RPi.GPIO as GPIO
import usbrelay_py
import traceback
from src.hardware.multiplexer import I2CMultiplexer
from src.hardware.nfc_reader import NFCReader
from src.hardware.lcd_display import LCDDisplay
from src.hardware.led_strip import LEDStrip
from src.hardware.buzzer import Buzzer
from src.utils.relay_control import trigger_relays
from src.config import (
    INSIDE_LED_PIN, OUTSIDE_LED_PIN,
    INSIDE_BUZZER_PIN, OUTSIDE_BUZZER_PIN,
    INSIDE_NFC_CHANNEL, OUTSIDE_NFC_CHANNEL
)

class HardwareError(Exception):
    """Donanım başlatma hataları için özel istisna sınıfı"""
    pass

class AccessControlSystem:
    def __init__(self):
        """Sistem başlatma"""
        print("Sistem başlatılıyor...")
        
        try:
            # GPIO ayarları
            print("GPIO ayarları yapılıyor...")
            GPIO.setmode(GPIO.BCM)
            print("GPIO ayarları tamamlandı.")
            
            # I2C Multiplexer başlat
            print("I2C Multiplexer başlatılıyor...")
            self.multiplexer = I2CMultiplexer()
            print("I2C Multiplexer (0x70) başarıyla başlatıldı.")
            
            # NFC okuyucuları başlat
            print("NFC okuyucular başlatılıyor...")
            self.inside_nfc = NFCReader(self.multiplexer, is_inside=True)
            self.outside_nfc = NFCReader(self.multiplexer, is_inside=False)
            print("NFC okuyucular başarıyla başlatıldı.")
            
            # LED şeritleri başlat
            print("LED şeritleri başlatılıyor...")
            self.inside_led = LEDStrip(INSIDE_LED_PIN, is_inside=True)
            self.outside_led = LEDStrip(OUTSIDE_LED_PIN, is_inside=False)
            print("LED şeritleri başarıyla başlatıldı.")
            
            # Buzzer'ları başlat
            print("Buzzer'lar başlatılıyor...")
            self.inside_buzzer = Buzzer(INSIDE_BUZZER_PIN, is_inside=True)
            self.outside_buzzer = Buzzer(OUTSIDE_BUZZER_PIN, is_inside=False)
            print("Buzzer'lar başarıyla başlatıldı.")
            
            # LCD ekranı başlat
            print("LCD ekran başlatılıyor...")
            self.lcd = LCDDisplay(self.multiplexer)
            print("LCD ekran başarıyla başlatıldı.")
            
            print("Tüm donanımlar başarıyla başlatıldı.")
            
        except Exception as e:
            print(f"Donanım başlatma hatası: {str(e)}")
            print("Hata detayı:")
            print(traceback.format_exc())
            self.cleanup()
            raise HardwareError(f"Donanım başlatılamadı: {str(e)}")
    
    def run(self):
        """Ana program döngüsü"""
        print("Sistem çalışıyor...")
        print("Kart bekleniyor...")
        
        try:
            while True:
                try:
                    # İç NFC okuyucuyu kontrol et
                    print("İç NFC okuyucu kontrol ediliyor...")
                    self.multiplexer.select_channel(INSIDE_NFC_CHANNEL)
                    inside_uid = self.inside_nfc.read_card()
                    if inside_uid:
                        print(f"İç NFC: Kart okundu! UID: {inside_uid}")
                        self.handle_card_read(True, inside_uid)
                        continue
                    
                    # Dış NFC okuyucuyu kontrol et
                    print("Dış NFC okuyucu kontrol ediliyor...")
                    self.multiplexer.select_channel(OUTSIDE_NFC_CHANNEL)
                    outside_uid = self.outside_nfc.read_card()
                    if outside_uid:
                        print(f"Dış NFC: Kart okundu! UID: {outside_uid}")
                        self.handle_card_read(False, outside_uid)
                        continue
                    
                    time.sleep(0.1)  # CPU kullanımını azaltmak için kısa bekleme
                    
                except Exception as e:
                    print(f"Döngü içi hata: {str(e)}")
                    print("Hata detayı:")
                    print(traceback.format_exc())
                    time.sleep(1)  # Hata durumunda 1 saniye bekle
                
        except KeyboardInterrupt:
            print("\nProgram kullanıcı tarafından durduruldu.")
        except Exception as e:
            print(f"Beklenmeyen hata: {str(e)}")
            print("Hata detayı:")
            print(traceback.format_exc())
        finally:
            self.cleanup()
    
    def handle_card_read(self, is_inside, uid):
        """Kart okuma işlemlerini yönet"""
        try:
            print(f"Kart işleniyor: {'İç' if is_inside else 'Dış'} NFC, UID: {uid}")
            
            # LED ve buzzer efektleri
            if is_inside:
                self.inside_led.success_effect()
                self.inside_buzzer.success_beep()
            else:
                self.outside_led.success_effect()
                self.outside_buzzer.success_beep()
            
            # Röleleri tetikle
            print("Röleler tetikleniyor...")
            trigger_relays()
            
            # LCD'ye bilgi göster
            print("LCD güncelleniyor...")
            self.lcd.show_card_info(uid, is_inside)
            
            # Kısa bir bekleme
            time.sleep(1)
            
        except Exception as e:
            print(f"Kart işleme hatası: {str(e)}")
            print("Hata detayı:")
            print(traceback.format_exc())
            if is_inside:
                self.inside_led.error_effect()
                self.inside_buzzer.error_beep()
            else:
                self.outside_led.error_effect()
                self.outside_buzzer.error_beep()
    
    def cleanup(self):
        """Kaynakları temizle"""
        print("Sistem kapatılıyor...")
        try:
            # NFC okuyucuları temizle
            if hasattr(self, 'inside_nfc'):
                self.inside_nfc.cleanup()
            if hasattr(self, 'outside_nfc'):
                self.outside_nfc.cleanup()
            
            # LED şeritleri temizle
            if hasattr(self, 'inside_led'):
                self.inside_led.cleanup()
            if hasattr(self, 'outside_led'):
                self.outside_led.cleanup()
            
            # Buzzer'ları temizle
            if hasattr(self, 'inside_buzzer'):
                self.inside_buzzer.cleanup()
            if hasattr(self, 'outside_buzzer'):
                self.outside_buzzer.cleanup()
            
            # LCD ekranı temizle
            if hasattr(self, 'lcd'):
                self.lcd.cleanup()
            
            # Multiplexer'ı temizle
            if hasattr(self, 'multiplexer'):
                self.multiplexer.cleanup()
            
            # GPIO'yu temizle
            GPIO.cleanup()
            
            print("Tüm kaynaklar temizlendi.")
            
        except Exception as e:
            print(f"Temizleme hatası: {str(e)}")
            print("Hata detayı:")
            print(traceback.format_exc())

if __name__ == "__main__":
    try:
        print("Program başlatılıyor...")
        system = AccessControlSystem()
        system.run()
    except Exception as e:
        print(f"Program hatası: {str(e)}")
        print("Hata detayı:")
        print(traceback.format_exc())
        if 'system' in locals():
            system.cleanup() 