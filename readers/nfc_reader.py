import threading
import time
from readers.multiplexer import select_channel
import board
import busio
from utils.api_client import send_card
from utils.logger import log
from controllers.relay_controller import trigger_relay
from controllers.led_controller import show_color
from controllers.buzzer_controller import beep
from controllers.lcd_controller import show_scan_result, start_idle_screen, stop_idle_screen
import os
import yaml
import logging
from datetime import datetime

# Logger kurulumu
logger = logging.getLogger(__name__)

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

# NFC okuyucu durağan zamanı (son başarılı okumadan sonra)
SCAN_COOLDOWN_TIME = 3  # saniye

try:
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Config dosyası yüklenemedi: {str(e)}")
    config = {
        "nfc_channels": {"inside": 0, "outside": 1},
        "multiplexer_address": 0x70
    }

# I2C yapılandırma
if SIMULATION_MODE:
    # Simülasyon modu - NFC okuyucu taklit sınıfı kullanılır
    try:
        from utils.dummy_nfc import DummyNFC as PN532_I2C
        # I2C objesini oluşturmayalım
        i2c = None
        logger.info("NFC simülasyon modu kullanılıyor")
        print("[NFC] Simülasyon modu kullanılıyor")
    except ImportError as e:
        logger.error(f"Dummy NFC modülü yüklenemedi: {str(e)}")
        raise ImportError("Simülasyon için gerekli dummy_nfc modülü yüklenemedi")
else:
    # Gerçek donanım modu - Adafruit PN532
    try:
        from adafruit_pn532.i2c import PN532_I2C
        try: 
            i2c = busio.I2C(board.SCL, board.SDA)
            logger.info("I2C başarıyla yapılandırıldı")
        except Exception as e:
            logger.error(f"I2C yapılandırması başarısız: {str(e)}")
            raise RuntimeError(f"I2C yapılandırması başarısız: {str(e)}")
    except ImportError as e:
        logger.error(f"Adafruit PN532 modülü yüklenemedi: {str(e)}")
        raise ImportError("NFC okuyucu için gerekli adafruit-circuitpython-pn532 modülü yüklenemedi")

class CardScanEvent:
    """Kart okuma olayı sınıfı"""
    def __init__(self, uid, role, is_inside):
        self.uid = uid
        self.role = role
        self.is_inside = is_inside
        self.timestamp = datetime.now()
        self.processed = False
        self.success = False
        self.door_opened = False

def handle_reader(role, channel, is_inside, lcd_enabled=False):
    """NFC okuyucu yönetimi"""
    global i2c
    
    try:
        select_channel(channel)
        
        # NFC okuyucu başlatma
        try:
            reader = PN532_I2C(i2c, debug=False)
            # NFC okuyucu ayarları
            reader.SAM_configuration()  # Varsayılan SAM yapılandırması
        except Exception as e:
            logger.error(f"{role} NFC okuyucu başlatılamadı: {str(e)}")
            print(f"[HATA] {role} NFC okuyucu başlatılamadı: {str(e)}")
            # Tekrar deneme için kısa bir süre bekle
            time.sleep(5)
            return
        
        # LED'i hazırla
        from controllers.led_controller import start_breathing
        start_breathing(role)
        
        logger.info(f"{role} NFC okuyucu başarıyla başlatıldı")
        print(f"[NFC] {role} okuyucu başlatıldı")
        
        # Son kart okuma zamanı - kontrol için
        last_scan_time = 0
        
        while True:
            try:
                # Kanal seçimi - her döngüde yenile
                select_channel(channel)
                
                # Kart okuma
                uid = reader.read_passive_target(timeout=0.1)
                current_time = time.time()
                
                # Kart algılandı ve soğuma süresi geçtiyse
                if uid and (current_time - last_scan_time) > SCAN_COOLDOWN_TIME:
                    uid_hex = uid.hex()
                    last_scan_time = current_time
                    
                    # Kart okuma olayı oluştur
                    scan_event = CardScanEvent(uid_hex, role, is_inside)
                    logger.info(f"{role.upper()} - UID: {uid_hex}")
                    
                    # Kart bilgisini API'ye gönder
                    try:
                        status, response = send_card(uid_hex, is_inside)
                        scan_event.processed = True
                        opened = False
                        
                        if status == 200 and response:
                            if response.get("openDoor"):
                                trigger_relay()
                                show_color(role, (0, 255, 0))  # Yeşil - başarılı
                                beep(role, [0.1, 0.1])
                                opened = True
                                scan_event.success = True
                                scan_event.door_opened = True
                            else:
                                show_color(role, (0, 0, 255))  # Mavi - geçersiz kart
                                beep(role, [0.1])
                                scan_event.success = False
                        else:
                            show_color(role, (255, 0, 0))  # Kırmızı - hata
                            beep(role, [1.0])
                            scan_event.success = False
                        
                        # LCD ekranında göster
                        if lcd_enabled:
                            direction = "Disari ciktiniz" if not is_inside else "Iceri girdiniz"
                            try:
                                stop_idle_screen()
                                show_scan_result(direction, opened)
                                start_idle_screen()
                            except Exception as e:
                                logger.error(f"LCD gösterimi hatası: {str(e)}")
                        
                        # Kart okunduktan sonra bir süre bekle
                        time.sleep(1)
                    except Exception as e:
                        logger.error(f"Kart işleme hatası: {str(e)}")
                        show_color(role, (255, 165, 0))  # Turuncu - işlem hatası
                        beep(role, [0.2, 0.2, 0.2])
                
            except Exception as e:
                logger.error(f"{role} okuyucu döngüsünde hata: {str(e)}")
                # Hata durumunda LED kırmızı yanıp sönsün
                show_color(role, (255, 0, 0))
                time.sleep(1)
                # Okuyucuyu sıfırla
                try:
                    reader = PN532_I2C(i2c, debug=False)
                except Exception:
                    pass
                
                # Hata sonrası kısa bekleme
                time.sleep(2)
                
    except Exception as e:
        logger.critical(f"{role} NFC thread hatası: {str(e)}")
        print(f"[HATA] {role} NFC thread'i başarısız: {str(e)}")
        # Ana threadi bilgilendir 