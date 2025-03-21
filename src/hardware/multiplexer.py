import smbus
import time
from src.config import MULTIPLEXER_ADDR, I2C_BUS

class I2CMultiplexer:
    def __init__(self):
        try:
            self.bus = smbus.SMBus(I2C_BUS)
            # Multiplexer'ın varlığını kontrol et
            self.bus.read_byte(MULTIPLEXER_ADDR)
            print(f"I2C Multiplexer (0x{MULTIPLEXER_ADDR:02X}) başarıyla başlatıldı.")
        except Exception as e:
            print(f"I2C Multiplexer başlatılamadı: {str(e)}")
            print("Lütfen şunları kontrol edin:")
            print("1. I2C etkin mi? (sudo raspi-config)")
            print("2. Modül doğru bağlı mı?")
            print("3. I2C adresi doğru mu?")
            raise
        
    def select_channel(self, channel):
        """Belirtilen kanalı seçer"""
        if 0 <= channel <= 7:
            try:
                self.bus.write_byte(MULTIPLEXER_ADDR, 1 << channel)
                time.sleep(0.01)  # Kanal değişikliği için kısa bekleme
                print(f"Kanal {channel} seçildi.")
            except Exception as e:
                print(f"Kanal {channel} seçilemedi: {str(e)}")
                raise
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