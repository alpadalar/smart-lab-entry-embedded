import time
from RPLCD.i2c import CharLCD
from src.config import LCD_CHANNEL, LCD_WIDTH, LCD_HEIGHT, LCD_ADDR

class LCDDisplay:
    def __init__(self, multiplexer):
        self.multiplexer = multiplexer
        self.channel = LCD_CHANNEL
        
        # LCD ekranı başlat
        self.multiplexer.select_channel(self.channel)
        self.lcd = CharLCD(i2c_expander='PCF8574', address=LCD_ADDR, port=1,
                          cols=LCD_WIDTH, rows=LCD_HEIGHT, dotsize=8)
        self.lcd.clear()
        self.lcd.backlight_enabled = True
        
    def show_message(self, line1, line2="", line3="", line4=""):
        """LCD ekranda mesaj gösterir"""
        self.multiplexer.select_channel(self.channel)
        self.lcd.clear()
        
        # Her satırı göster
        if line1:
            self.lcd.write_string(line1)
            self.lcd.cursor_pos = (1, 0)
        if line2:
            self.lcd.write_string(line2)
            self.lcd.cursor_pos = (2, 0)
        if line3:
            self.lcd.write_string(line3)
            self.lcd.cursor_pos = (3, 0)
        if line4:
            self.lcd.write_string(line4)
            
    def clear(self):
        """LCD ekranı temizler"""
        self.multiplexer.select_channel(self.channel)
        self.lcd.clear()
        
    def set_backlight(self, on=True):
        """LCD arka ışığını açıp kapatır"""
        self.multiplexer.select_channel(self.channel)
        self.lcd.backlight_enabled = on
        
    def show_welcome(self):
        """Karşılama ekranını gösterir"""
        self.show_message(
            "Smart Lab Entry",
            "System Ready",
            "Waiting for card...",
            "=================="
        )
        
    def show_access_info(self, direction, door_status):
        """Geçiş bilgilerini gösterir"""
        status = "OPEN" if door_status else "CLOSED"
        self.show_message(
            f"Access: {direction}",
            f"Status: {status}",
            "==================",
            "Waiting for card..."
        )
        
    def show_error(self, message):
        """Hata mesajını gösterir"""
        self.show_message(
            "ERROR!",
            message[:20],
            message[20:40] if len(message) > 20 else "",
            "=================="
        ) 