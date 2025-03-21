import time
import yaml
import os
import logging
import threading

# Logger kurulumu
logger = logging.getLogger(__name__)

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

# Konfigürasyon yükleme
try:
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    MUX_ADDRESS = config['multiplexer_address']
except Exception as e:
    logger.error(f"Config dosyası yüklenemedi: {str(e)}")
    MUX_ADDRESS = 0x70  # Varsayılan adres

# I2C bus kilit mekanizması - thread güvenliği için
i2c_lock = threading.Lock()
current_channel = None

if SIMULATION_MODE:
    # Simülasyon modu
    try:
        from utils.dummy_smbus import SMBus
        logger.info("Multiplexer simülasyon modu kullanılıyor")
        print("[MULTIPLEXER] Simülasyon modu kullanılıyor")
    except ImportError as e:
        logger.error(f"Dummy SMBus modülü yüklenemedi: {str(e)}")
        raise ImportError("Simülasyon için gerekli dummy_smbus modülü yüklenemedi")
else:
    # Gerçek donanım modu
    try:
        from smbus2 import SMBus
        logger.info("SMBus2 başarıyla içe aktarıldı")
    except ImportError as e:
        try:
            # Alternatif olarak smbus dene
            from smbus import SMBus
            logger.warning("smbus2 yerine smbus kullanılıyor")
        except ImportError:
            logger.error("Hem smbus2 hem de smbus yüklenemedi")
            raise ImportError("I2C erişimi için smbus2 veya smbus modülü gerekli")

def select_channel(channel: int):
    """
    I2C multiplexer kanalı seçme
    
    Args:
        channel (int): Seçilecek kanal (0-7)
    
    Returns:
        bool: Başarılı ise True, hata durumunda False
    """
    global current_channel
    
    if not 0 <= channel <= 7:
        logger.error(f"Geçersiz multiplexer kanalı: {channel}. 0-7 arasında olmalı.")
        return False
    
    # Aynı kanal tekrar seçilmek isteniyorsa işlem yapmaya gerek yok
    if current_channel == channel:
        return True
    
    if SIMULATION_MODE:
        # Simülasyon modunda gerçek I2C işlemi yapılmaz
        current_channel = channel
        logger.debug(f"Simülasyon: Multiplexer kanal {channel} seçildi")
        return True
        
    # I2C bus'a erişim için lock kullan
    with i2c_lock:
        try:
            bus = SMBus(1)  # Raspberry Pi'de genellikle bus 1 kullanılır
            
            # Belirtilen kanalı seç (1 << channel ile bit maskeleme)
            bus.write_byte(MUX_ADDRESS, 1 << channel)
            
            # Biraz bekle - cihazlar arası iletişim için
            time.sleep(0.01)
            
            # İşlem tamamlandığında bus'ı kapat
            bus.close()
            
            # Güncel kanalı güncelle
            current_channel = channel
            
            logger.debug(f"Multiplexer kanal {channel} başarıyla seçildi")
            return True
            
        except Exception as e:
            logger.error(f"Multiplexer kanal {channel} seçimi başarısız: {str(e)}")
            return False

def reset_multiplexer():
    """
    Multiplexer'ı sıfırla - tüm kanalları kapat
    
    Returns:
        bool: Başarılı ise True, hata durumunda False
    """
    global current_channel
    
    if SIMULATION_MODE:
        current_channel = None
        logger.debug("Simülasyon: Multiplexer sıfırlandı")
        return True
        
    with i2c_lock:
        try:
            bus = SMBus(1)
            
            # 0 değeri yazarak tüm kanalları kapat
            bus.write_byte(MUX_ADDRESS, 0)
            
            time.sleep(0.01)
            bus.close()
            
            current_channel = None
            
            logger.debug("Multiplexer başarıyla sıfırlandı")
            return True
            
        except Exception as e:
            logger.error(f"Multiplexer sıfırlama başarısız: {str(e)}")
            return False 