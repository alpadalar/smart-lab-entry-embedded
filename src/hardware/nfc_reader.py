import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from config import INSIDE_NFC_CHANNEL, OUTSIDE_NFC_CHANNEL

class NFCReader:
    def __init__(self, multiplexer, is_inside=True):
        self.multiplexer = multiplexer
        self.is_inside = is_inside
        self.channel = INSIDE_NFC_CHANNEL if is_inside else OUTSIDE_NFC_CHANNEL
        
        # I2C bağlantısı
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # NFC okuyucuyu başlat
        self.multiplexer.select_channel(self.channel)
        self.pn532 = PN532_I2C(self.i2c)
        
    def read_card(self):
        """Kart okuma işlemi yapar"""
        self.multiplexer.select_channel(self.channel)
        try:
            uid = self.pn532.read_passive_target(timeout=0.1)
            if uid:
                return ''.join([hex(i)[2:].zfill(2) for i in uid])
            return None
        except Exception as e:
            print(f"NFC okuma hatası: {e}")
            return None 