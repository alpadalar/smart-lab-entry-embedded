import board
import busio
import time
from adafruit_pn532.i2c import PN532_I2C
from src.config import INSIDE_NFC_CHANNEL, OUTSIDE_NFC_CHANNEL, NFC_ADDR

class NFCReader:
    def __init__(self, multiplexer, is_inside=True):
        """NFC okuyucu başlatma"""
        self.multiplexer = multiplexer
        self.is_inside = is_inside
        self.channel = INSIDE_NFC_CHANNEL if is_inside else OUTSIDE_NFC_CHANNEL
        
        print(f"{'İç' if is_inside else 'Dış'} NFC okuyucu başlatılıyor...")
        print(f"Kanal {self.channel} seçildi.")
        
        # I2C bağlantısı (düşük hızda)
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)  # 100kHz
            print("I2C bağlantısı başarılı.")
        except Exception as e:
            print(f"I2C bağlantı hatası: {str(e)}")
            raise
        
        # NFC okuyucuyu başlat
        try:
            print(f"PN532 başlatılıyor (Kanal: {self.channel})...")
            self.multiplexer.select_channel(self.channel)
            time.sleep(0.1)  # Kanal değişikliği için bekle
            
            # PN532'yi başlat
            self.pn532 = PN532_I2C(self.i2c, debug=True)
            
            # PN532'yi yapılandır
            self.pn532.SAM_configuration()
            
            # Firmware versiyonunu kontrol et
            version = self.pn532.get_firmware_version()
            print(f"{'İç' if is_inside else 'Dış'} NFC okuyucu başarıyla başlatıldı")
            print(f"Firmware versiyonu: {version}")
            
        except Exception as e:
            print(f"NFC okuyucu başlatma hatası: {str(e)}")
            raise
        
    def read_card(self):
        """Kart okuma işlemi yapar"""
        try:
            self.multiplexer.select_channel(self.channel)
            time.sleep(0.1)  # Kanal değişikliği için bekle
            
            uid = self.pn532.read_passive_target(timeout=0.1)
            if uid:
                return ''.join([hex(i)[2:].zfill(2) for i in uid])
            return None
        except Exception as e:
            print(f"NFC okuma hatası: {e}")
            return None 

    def cleanup(self):
        """NFC okuyucuyu temizler"""
        try:
            if hasattr(self, 'pn532'):
                self.multiplexer.select_channel(self.channel)
                time.sleep(0.1)  # Kanal değişikliği için bekle
                self.pn532.deinit()
        except Exception as e:
            print(f"NFC okuyucu temizleme hatası: {str(e)}")
            print("Hata detayı:", type(e).__name__)
            
    def __del__(self):
        """Nesne silindiğinde kaynakları temizle"""
        self.cleanup() 