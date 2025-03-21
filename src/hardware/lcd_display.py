import time
import smbus
from lcd1602 import LCD1602
from src.config import LCD_CHANNEL, LCD_WIDTH, LCD_HEIGHT, LCD_ADDR

class LCDDisplay:
    def __init__(self, multiplexer):
        self.multiplexer = multiplexer
        self.channel = LCD_CHANNEL
        
        # I2C bağlantısı
        self.bus = smbus.SMBus(1)  # I2C-1 kullanıyoruz
        
        # LCD ekranı başlat
        self.multiplexer.select_channel(self.channel)
        self.lcd = LCD1602(self.bus, LCD_ADDR)
        self.lcd.clear()
        self.lcd.backlight(True)
        
    def show_message(self, line1, line2="", line3="", line4=""):
        """LCD ekranda mesaj gösterir"""
        self.multiplexer.select_channel(self.channel)
        self.lcd.clear()
        
        # Her satırı göster
        if line1:
            self.lcd.write(0, 0, line1)
        if line2:
            self.lcd.write(0, 1, line2)
        if line3:
            self.lcd.write(0, 2, line3)
        if line4:
            self.lcd.write(0, 3, line4)
            
    def clear(self):
        """LCD ekranı temizler"""
        self.multiplexer.select_channel(self.channel)
        self.lcd.clear()
        
    def set_backlight(self, on=True):
        """LCD arka ışığını açıp kapatır"""
        self.multiplexer.select_channel(self.channel)
        self.lcd.backlight(on)
        
    def show_welcome(self):
        """Karşılama ekranını gösterir"""
        self.clear()
        # TODO: Karşılama ekranı kodları
        
    def show_access_info(self, direction, door_status):
        """Geçiş bilgilerini gösterir"""
        self.clear()
        # TODO: Geçiş bilgileri kodları
        
    def show_error(self, message):
        """Hata mesajını gösterir"""
        self.clear()
        # TODO: Hata mesajı kodları 