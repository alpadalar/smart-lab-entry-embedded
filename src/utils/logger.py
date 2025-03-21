import logging
from datetime import datetime
from config import LOG_FILE

class Logger:
    def __init__(self):
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def log_access(self, card_uid, is_inside, door_opened):
        """Geçiş denemesini loglar"""
        direction = "İçeri" if is_inside else "Dışarı"
        status = "Başarılı" if door_opened else "Başarısız"
        message = f"Kart {card_uid} - {direction} yönünde geçiş denemesi - {status}"
        logging.info(message)
        
    def log_error(self, error_message):
        """Hata mesajını loglar"""
        logging.error(error_message) 