import smbus
import time
from src.config import MULTIPLEXER_ADDR, I2C_BUS

class I2CMultiplexer:
    def __init__(self):
        """I2C Multiplexer başlatma"""
        try:
            print("I2C Multiplexer başlatılıyor...")
            self.bus = smbus.SMBus(I2C_BUS)
            
            # Multiplexer'ın varlığını kontrol et
            try:
                self.bus.read_byte(MULTIPLEXER_ADDR)
                print(f"I2C Multiplexer (0x{MULTIPLEXER_ADDR:02X}) başarıyla başlatıldı.")
            except Exception as e:
                print(f"Multiplexer bulunamadı: {str(e)}")
                print("Lütfen şunları kontrol edin:")
                print("1. I2C etkin mi? (sudo raspi-config)")
                print("2. Modül doğru bağlı mı?")
                print("3. I2C adresi doğru mu?")
                raise
                
            # Başlangıçta tüm kanalları kapat
            self.bus.write_byte(MULTIPLEXER_ADDR, 0x00)
            time.sleep(0.1)  # Başlangıç ayarları için bekle
            
        except Exception as e:
            print(f"I2C Multiplexer başlatılamadı: {str(e)}")
            if hasattr(self, 'bus'):
                self.bus.close()
            raise
        
    def select_channel(self, channel):
        """Belirtilen kanalı seçer"""
        if 0 <= channel <= 7:
            try:
                # Önce tüm kanalları kapat
                self.bus.write_byte(MULTIPLEXER_ADDR, 0x00)
                time.sleep(0.01)
                
                # İstenen kanalı seç
                self.bus.write_byte(MULTIPLEXER_ADDR, 1 << channel)
                time.sleep(0.01)  # Kanal değişikliği için bekle
                
                # Kanal seçimini doğrula
                current_channel = self.bus.read_byte(MULTIPLEXER_ADDR)
                if current_channel == (1 << channel):
                    print(f"Kanal {channel} başarıyla seçildi.")
                    return True
                else:
                    print(f"Kanal {channel} seçilemedi. Mevcut durum: {current_channel}")
                    return False
                    
            except Exception as e:
                print(f"Kanal {channel} seçilemedi: {str(e)}")
                raise
        else:
            raise ValueError("Kanal numarası 0-7 arasında olmalıdır")
            
    def __del__(self):
        """Nesne silindiğinde I2C bağlantısını kapatır"""
        self.cleanup()

    def cleanup(self):
        """Multiplexer'ı temizler"""
        try:
            # Tüm kanalları kapat
            self.bus.write_byte(MULTIPLEXER_ADDR, 0x00)
            time.sleep(0.01)
            self.bus.close()
            print("Multiplexer temizlendi.")
        except Exception as e:
            print(f"Multiplexer temizleme hatası: {str(e)}") 