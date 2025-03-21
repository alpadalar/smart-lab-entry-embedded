import usbrelay_py
import time
import os
import logging

# Alternatif röle kontrolü için gpiozero'yu içe aktar
try:
    from gpiozero import OutputDevice
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

# Logger kurulumu
logger = logging.getLogger(__name__)

def trigger_relay(duration=3):
    """
    USB röleyi tetikler veya GPIO röle kullanıyorsa onu etkinleştirir.
    
    Args:
        duration (int): Rölenin aktif kalma süresi (saniye)
    """
    if SIMULATION_MODE:
        logger.info("Simülasyon modunda röle tetikleniyor (USB veya GPIO)")
        print(f"[RELAY] Röle {duration} saniye boyunca etkinleştirildi (simülasyon)")
        time.sleep(duration)
        return True
    
    # USB röle kontrolü dene
    try:
        boards = usbrelay_py.board_details()
        if boards:
            logger.info(f"USB röle bulundu: {boards}")
            for board_id, num_relays in boards:
                for relay in range(1, num_relays + 1):
                    usbrelay_py.board_control(board_id, relay, 1)
                time.sleep(duration)
                for relay in range(1, num_relays + 1):
                    usbrelay_py.board_control(board_id, relay, 0)
            return True
    except Exception as e:
        logger.warning(f"USB röle kontrolü başarısız: {str(e)}")
    
    # USB röle bulunamadıysa ve gpiozero mevcutsa, GPIO pinine bağlı röleyi kontrol et
    if GPIOZERO_AVAILABLE:
        try:
            # Röle GPIO pinini yapılandırmadan okuyun
            import yaml
            with open("config/config.yaml") as f:
                config = yaml.safe_load(f)
            
            relay_pin = config.get('relay_pin', 17)  # Varsayılan olarak GPIO 17
            logger.info(f"GPIO röle pin {relay_pin} üzerinden kontrol ediliyor")
            
            # active_high=False, çünkü çoğu röle modülü düşük seviyede tetiklenir
            relay = OutputDevice(relay_pin, active_high=False, initial_value=False)
            relay.on()
            time.sleep(duration)
            relay.off()
            relay.close()
            return True
        except Exception as e:
            logger.error(f"GPIO röle kontrolü başarısız: {str(e)}")
    
    logger.error("Hiçbir röle mekanizması çalışmadı")
    return False 