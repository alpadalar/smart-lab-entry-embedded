"""
NFC okuyucu simülasyon modülü - gerçek NFC donanımı olmayan ortamlarda kullanmak için
"""
import time
import random
import threading

class DummyNFC:
    def __init__(self, i2c=None, debug=False):
        self.debug = debug
        self.i2c = i2c
        self._uid = None
        self._last_read_time = 0
        self._simulated_cards = [
            bytes([0x04, 0xE6, 0x8F, 0x2A, 0x5C, 0x4D, 0x80]),
            bytes([0x04, 0xE8, 0x12, 0xDC, 0x1A, 0x8F, 0x02]),
            bytes([0x04, 0xEE, 0xA5, 0x37, 0xCB, 0x12, 0x45])
        ]
        print("[DummyNFC] NFC okuyucu simülatörü başlatıldı")
        
        # Simüle edilmiş kart okumalarını başlat
        threading.Thread(target=self._simulate_card_readings, daemon=True).start()
    
    def _simulate_card_readings(self):
        while True:
            # Rastgele aralıklarla kart okuma simülasyonu
            time.sleep(random.uniform(5, 15))
            
            # %30 olasılıkla bir kart okundu olarak işaretle
            if random.random() < 0.3:
                self._uid = random.choice(self._simulated_cards)
                self._last_read_time = time.time()
                print(f"[DummyNFC] Simüle edilmiş kart okuması: {self._uid.hex()}")
            else:
                self._uid = None
    
    def read_passive_target(self, timeout=0.5):
        # Simüle edilmiş kart okuması
        current_time = time.time()
        
        # Son okumadan bu yana 3 saniyeden az zaman geçtiyse kartı döndür
        if self._uid is not None and (current_time - self._last_read_time) < 3:
            return self._uid
        
        # Eğer timeout süresi dolmamışsa ve okuma olasılığı düşükse
        # beklemeden None döndür (kart tespit edilmedi)
        time.sleep(timeout)
        return None 