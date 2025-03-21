import board
import busio
import time
import smbus
from adafruit_pn532.i2c import PN532_I2C
from src.config import I2C_BUS, MULTIPLEXER_ADDR

class NFCReader:
    def __init__(self, channel):
        """NFC okuyucu başlatma"""
        self.channel = channel
        self.bus = smbus.SMBus(I2C_BUS)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # Kanalı seç
        self.select_channel()
        
        # PN532'yi başlat
        self.pn532 = PN532_I2C(self.i2c)
        self.pn532.SAM_configuration()
        
    def select_channel(self):
        """Multiplexer kanalını seç"""
        self.bus.write_byte(MULTIPLEXER_ADDR, 1 << self.channel)
        time.sleep(0.01)
        
    def read_card(self):
        """Kart okuma işlemi"""
        try:
            self.select_channel()
            uid = self.pn532.read_passive_target(timeout=0.1)
            if uid:
                return ''.join([hex(i)[2:].zfill(2) for i in uid])
            return None
        except Exception as e:
            print(f"Kart okuma hatası: {e}")
            return None
            
    def cleanup(self):
        """Kaynakları temizle"""
        try:
            if hasattr(self, 'pn532'):
                self.pn532.deinit()
            if hasattr(self, 'i2c'):
                self.i2c.deinit()
            if hasattr(self, 'bus'):
                self.bus.close()
        except:
            pass 