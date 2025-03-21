import smbus
import time
from src.config import MULTIPLEXER_ADDR, I2C_BUS

class I2CMultiplexer:
    def __init__(self):
        self.bus = smbus.SMBus(I2C_BUS)
        
    def select_channel(self, channel):
        """Belirtilen kanalı seçer"""
        if 0 <= channel <= 7:
            self.bus.write_byte(MULTIPLEXER_ADDR, 1 << channel)
            time.sleep(0.01)  # Kanal değişikliği için kısa bekleme
        else:
            raise ValueError("Kanal numarası 0-7 arasında olmalıdır")
            
    def __del__(self):
        """Nesne silindiğinde I2C bağlantısını kapatır"""
        try:
            self.bus.close()
        except:
            pass 

    def cleanup(self):
        """Multiplexer'ı temizler"""
        try:
            # Tüm kanalları kapat
            self.bus.write_byte(MULTIPLEXER_ADDR, 0x00)
        except Exception as e:
            print(f"Multiplexer temizleme hatası: {str(e)}") 