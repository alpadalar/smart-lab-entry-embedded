import logging
from datetime import datetime
from src.config import LOG_FILE

class Logger:
    def __init__(self):
        # Log dosyası adını tarih ile oluştur
        log_filename = f"{LOG_FILE}_{datetime.now().strftime('%Y%m%d')}.txt"
        
        # Logger'ı yapılandır
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def info(self, message):
        """Bilgi mesajı logla"""
        self.logger.info(message)
        
    def error(self, message):
        """Hata mesajı logla"""
        self.logger.error(message)
        
    def warning(self, message):
        """Uyarı mesajı logla"""
        self.logger.warning(message)
        
    def debug(self, message):
        """Debug mesajı logla"""
        self.logger.debug(message)

    def log_access(self, card_uid, is_inside, door_opened):
        """Geçiş denemesini loglar"""
        direction = "İçeri" if is_inside else "Dışarı"
        status = "Başarılı" if door_opened else "Başarısız"
        message = f"Kart {card_uid} - {direction} yönünde geçiş denemesi - {status}"
        self.logger.info(message)
        
    def log_error(self, error_message):
        """Hata mesajını loglar"""
        self.logger.error(error_message) 