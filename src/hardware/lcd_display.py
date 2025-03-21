import time
from config import LCD_CHANNEL, LCD_WIDTH, LCD_HEIGHT, LCD_ADDR

class LCDDisplay:
    def __init__(self, multiplexer):
        self.multiplexer = multiplexer
        self.multiplexer.select_channel(LCD_CHANNEL)
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        self.addr = LCD_ADDR
        
        # LCD başlatma
        self._init_lcd()
        
    def _init_lcd(self):
        """LCD ekranı başlatır"""
        # TODO: LCD başlatma kodları buraya gelecek
        pass
        
    def clear(self):
        """Ekranı temizler"""
        # TODO: Ekran temizleme kodu
        pass
        
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