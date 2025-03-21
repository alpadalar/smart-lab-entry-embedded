import usbrelay_py
import time
from src.config import RELAY_DURATION

class Relay:
    def __init__(self):
        self.boards = usbrelay_py.board_details()
        if not self.boards:
            raise RuntimeError("USB röle kartı bulunamadı!")
            
        self.board_id = self.boards[0][0]
        self.relay_count = self.boards[0][1]
        
    def trigger(self, duration=0.5):
        """Röleyi tetikler"""
        try:
            # İlk röleyi aç
            usbrelay_py.board_control(self.board_id, 1, 1)
            time.sleep(duration)
            # Röleyi kapat
            usbrelay_py.board_control(self.board_id, 1, 0)
            return True
        except Exception as e:
            print(f"Röle hatası: {e}")
            return False 