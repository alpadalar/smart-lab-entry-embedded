import time
import threading
from hardware.multiplexer import I2CMultiplexer
from hardware.nfc_reader import NFCReader
from hardware.lcd_display import LCDDisplay
from hardware.led_strip import LEDStrip
from hardware.buzzer import Buzzer
from hardware.relay import Relay
from utils.api_client import APIClient
from utils.logger import Logger
from config import (
    INSIDE_LED_PIN, OUTSIDE_LED_PIN,
    INSIDE_BUZZER_PIN, OUTSIDE_BUZZER_PIN
)

class AccessControlSystem:
    def __init__(self):
        # Donanım bileşenlerini başlat
        self.multiplexer = I2CMultiplexer()
        self.inside_nfc = NFCReader(self.multiplexer, is_inside=True)
        self.outside_nfc = NFCReader(self.multiplexer, is_inside=False)
        self.lcd = LCDDisplay(self.multiplexer)
        self.inside_led = LEDStrip(INSIDE_LED_PIN, is_inside=True)
        self.outside_led = LEDStrip(OUTSIDE_LED_PIN, is_inside=False)
        self.inside_buzzer = Buzzer(INSIDE_BUZZER_PIN, is_inside=True)
        self.outside_buzzer = Buzzer(OUTSIDE_BUZZER_PIN, is_inside=False)
        self.relay = Relay()
        
        # Yardımcı bileşenleri başlat
        self.api = APIClient()
        self.logger = Logger()
        
        # LED efektlerini başlat
        self.inside_led.start_breathing()
        self.outside_led.start_breathing()
        
        # LCD'yi başlat
        self.lcd.show_welcome()
        
    def handle_card_read(self, card_uid, is_inside):
        """Kart okuma işlemini yönetir"""
        try:
            # API'den erişim kontrolü
            door_opened = self.api.check_access(card_uid, is_inside)
            
            # Röle kontrolü
            if door_opened:
                self.relay.trigger()
                
            # LED ve buzzer kontrolü
            led = self.inside_led if is_inside else self.outside_led
            buzzer = self.inside_buzzer if is_inside else self.outside_buzzer
            
            if door_opened:
                led.show_success()
                buzzer.success_beep()
            else:
                led.show_fail()
                buzzer.fail_beep()
                
            # LCD güncelleme
            self.lcd.show_access_info(is_inside, door_opened)
            
            # Loglama
            self.logger.log_access(card_uid, is_inside, door_opened)
            
        except Exception as e:
            error_msg = f"Hata oluştu: {str(e)}"
            print(error_msg)
            self.logger.log_error(error_msg)
            
            # Hata durumunda LED ve buzzer
            led = self.inside_led if is_inside else self.outside_led
            buzzer = self.inside_buzzer if is_inside else self.outside_buzzer
            led.show_error()
            buzzer.error_beep()
            
            self.lcd.show_error("Bir hata oluştu!")
            
    def run(self):
        """Ana döngü"""
        print("Sistem başlatıldı. Kart bekleniyor...")
        
        while True:
            try:
                # İç NFC kontrolü
                inside_uid = self.inside_nfc.read_card()
                if inside_uid:
                    self.handle_card_read(inside_uid, True)
                    
                # Dış NFC kontrolü
                outside_uid = self.outside_nfc.read_card()
                if outside_uid:
                    self.handle_card_read(outside_uid, False)
                    
                time.sleep(0.1)  # CPU kullanımını azalt
                
            except KeyboardInterrupt:
                print("\nProgram sonlandırılıyor...")
                break
            except Exception as e:
                error_msg = f"Beklenmeyen hata: {str(e)}"
                print(error_msg)
                self.logger.log_error(error_msg)
                time.sleep(1)  # Hata durumunda kısa bekleme
                
    def cleanup(self):
        """Kaynakları temizler"""
        self.inside_buzzer.cleanup()
        self.outside_buzzer.cleanup()

if __name__ == "__main__":
    system = AccessControlSystem()
    try:
        system.run()
    finally:
        system.cleanup() 