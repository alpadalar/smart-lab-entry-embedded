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
        
        # I2C bağlantısı
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            print("I2C bağlantısı başarılı.")
        except Exception as e:
            print(f"I2C bağlantı hatası: {str(e)}")
            raise
        
        # NFC okuyucuyu başlat
        try:
            print(f"PN532 başlatılıyor (Kanal: {self.channel})...")
            
            # Önce multiplexer kanalını seç
            self.multiplexer.select_channel(self.channel)
            time.sleep(0.01)  # Kanal değişikliği için kısa bekleme
            
            # PN532'yi başlat
            self.pn532 = PN532_I2C(self.i2c)
            
            # PN532'yi yapılandır
            print("PN532 yapılandırılıyor...")
            self.pn532.SAM_configuration()
            
            print(f"{'İç' if is_inside else 'Dış'} NFC okuyucu başarıyla başlatıldı")
            
        except Exception as e:
            print(f"NFC okuyucu başlatma hatası: {str(e)}")
            print(f"Hata detayı: {type(e).__name__}")
            self.cleanup()  # Hata durumunda kaynakları temizle
            raise
        
    def read_card(self):
        """Kart okuma işlemi yapar"""
        try:
            # Kanalı seç
            self.multiplexer.select_channel(self.channel)
            time.sleep(0.01)  # Kanal değişikliği için kısa bekleme
            
            # Kartı oku
            uid = self.pn532.read_passive_target(timeout=0.1)
            if uid:
                return ''.join([hex(i)[2:].zfill(2) for i in uid])
            return None
        except Exception as e:
            print(f"NFC okuma hatası: {e}")
            print(f"Hata detayı: {type(e).__name__}")
            return None 

    def cleanup(self):
        """NFC okuyucuyu temizler"""
        try:
            # Kanalı seç
            self.multiplexer.select_channel(self.channel)
            time.sleep(0.01)  # Kanal değişikliği için kısa bekleme
            
            # PN532'yi temizle
            if hasattr(self, 'pn532'):
                self.pn532.deinit()
            
            # I2C bağlantısını temizle
            if hasattr(self, 'i2c'):
                self.i2c.deinit()
                
        except Exception as e:
            print(f"NFC okuyucu temizleme hatası: {str(e)}")
            print(f"Hata detayı: {type(e).__name__}")
            
    def __del__(self):
        """Nesne silindiğinde kaynakları temizle"""
        self.cleanup() 