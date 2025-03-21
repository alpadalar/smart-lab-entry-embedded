import board
import busio
import time
import smbus
from adafruit_pn532.i2c import PN532_I2C
from src.config import INSIDE_NFC_CHANNEL, OUTSIDE_NFC_CHANNEL, NFC_ADDR

class NFCReader:
    def __init__(self, multiplexer, is_inside=True):
        self.multiplexer = multiplexer
        self.is_inside = is_inside
        self.channel = INSIDE_NFC_CHANNEL if is_inside else OUTSIDE_NFC_CHANNEL
        
        # I2C bağlantısı (düşük hızda)
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)  # 100kHz
        self.smbus = smbus.SMBus(1)
        
        # NFC okuyucuyu başlat
        try:
            print(f"{'İç' if is_inside else 'Dış'} NFC okuyucu başlatılıyor...")
            
            # Önce multiplexer kanalını seç
            self.multiplexer.select_channel(self.channel)
            time.sleep(0.1)  # Kanal değişikliği için bekle
            
            # I2C cihazlarını kontrol et
            devices = self.i2c.scan()
            print(f"Kanal {self.channel} üzerindeki I2C cihazları: {[hex(device) for device in devices]}")
            
            # PN532'yi başlat
            print(f"PN532 başlatılıyor (Adres: 0x{NFC_ADDR:02X})...")
            
            # PN532'yi I2C adresiyle başlat
            self.pn532 = PN532_I2C(self.i2c, address=NFC_ADDR, debug=True)
            
            # PN532'yi yapılandır
            print("PN532 yapılandırılıyor...")
            self.pn532.SAM_configuration()
            
            # Firmware versiyonunu kontrol et
            print("Firmware versiyonu kontrol ediliyor...")
            version = self.pn532.get_firmware_version()
            print(f"{'İç' if is_inside else 'Dış'} NFC okuyucu başarıyla başlatıldı")
            print(f"Firmware versiyonu: {version}")
            
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
            time.sleep(0.1)  # Kanal değişikliği için bekle
            
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
            time.sleep(0.1)  # Kanal değişikliği için bekle
            
            # PN532'yi temizle
            if hasattr(self, 'pn532'):
                self.pn532.deinit()
            
            # I2C bağlantılarını temizle
            if hasattr(self, 'i2c'):
                self.i2c.deinit()
            if hasattr(self, 'smbus'):
                self.smbus.close()
                
        except Exception as e:
            print(f"NFC okuyucu temizleme hatası: {str(e)}")
            print(f"Hata detayı: {type(e).__name__}")
            
    def __del__(self):
        """Nesne silindiğinde kaynakları temizle"""
        self.cleanup() 