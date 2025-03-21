import threading
import time
import yaml
import os
import sys
import signal
import logging
import atexit
from readers.nfc_reader import handle_reader
from readers.multiplexer import reset_multiplexer
from controllers.lcd_controller import init_lcd, start_idle_screen, stop_idle_screen
from controllers.led_controller import cleanup as led_cleanup
from controllers.buzzer_controller import cleanup as buzzer_cleanup

# Logger kurulumu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("smart_lab.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Simülasyon modunu kontrol et
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')
PIN_FACTORY = os.environ.get('GPIOZERO_PIN_FACTORY', 'native')

# Çalıştırma ayrıntılarını logla
logger.info(f"Sistem başlatılıyor - Simülasyon modu: {SIMULATION_MODE}, Pin Factory: {PIN_FACTORY}")

# Thread yönetimi
nfc_threads = []
running = True

def cleanup():
    """
    Program sonlandığında temizlik işlemleri
    """
    global running
    running = False
    
    logger.info("Sistem kapatılıyor...")
    
    # LCD ekran döngüsünü durdur
    try:
        stop_idle_screen()
        logger.info("LCD ekran döngüsü durduruldu")
    except Exception as e:
        logger.error(f"LCD ekran durdurma hatası: {str(e)}")
    
    # LED'leri temizle
    try:
        led_cleanup()
        logger.info("LED'ler temizlendi")
    except Exception as e:
        logger.error(f"LED temizleme hatası: {str(e)}")
    
    # Buzzer'ları temizle
    try:
        buzzer_cleanup()
        logger.info("Buzzer'lar temizlendi")
    except Exception as e:
        logger.error(f"Buzzer temizleme hatası: {str(e)}")
    
    # Multiplexer'ı sıfırla
    try:
        reset_multiplexer()
        logger.info("Multiplexer sıfırlandı")
    except Exception as e:
        logger.error(f"Multiplexer sıfırlama hatası: {str(e)}")
    
    logger.info("Temizlik işlemleri tamamlandı. Program sonlandırılıyor.")
    print("Program güvenli bir şekilde sonlandırıldı.")

def signal_handler(sig, frame):
    """
    Sinyal işleyicisi (Ctrl+C)
    """
    print("\nKapatma sinyali alındı. Sistem güvenli bir şekilde kapatılıyor...")
    cleanup()
    sys.exit(0)

# Sinyal işleyicilerini kaydet
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
atexit.register(cleanup)

def main():
    """
    Ana program
    """
    try:
        # Pin factory bilgisini göster
        if not SIMULATION_MODE:
            print(f"GPIO Pin Factory: {PIN_FACTORY}")
            
        # Konfigürasyon dosyasını yükle
        try:
            with open("config/config.yaml") as f:
                config = yaml.safe_load(f)
            logger.info("Konfigürasyon dosyası başarıyla yüklendi")
        except Exception as e:
            logger.error(f"Konfigürasyon dosyası yüklenirken hata: {str(e)}")
            print(f"Konfigürasyon dosyası yüklenemedi: {str(e)}")
            return
            
        # Çalışma modunu göster
        if SIMULATION_MODE:
            print("Sistem simülasyon modunda çalışıyor. Gerçek donanım kullanılmayacak.")
        else:
            print("Sistem gerçek donanım modunda çalışıyor.")
        
        # LCD başlat
        if init_lcd():
            logger.info("LCD başarıyla başlatıldı")
        else:
            logger.warning("LCD başlatılamadı, devam ediliyor")
        
        # LCD boş ekran thread'ini başlat
        start_idle_screen()
        
        # NFC okuyucu thread'leri başlat
        inside_thread = threading.Thread(
            target=handle_reader, 
            args=("inside", config['nfc_channels']['inside'], True),
            daemon=True
        )
        inside_thread.start()
        nfc_threads.append(inside_thread)
        
        outside_thread = threading.Thread(
            target=handle_reader, 
            args=("outside", config['nfc_channels']['outside'], False, True),
            daemon=True
        )
        outside_thread.start()
        nfc_threads.append(outside_thread)
        
        # Sonsuz döngü
        print("Sistem başlatıldı. Çıkmak için Ctrl+C tuşlarına basın.")
        while running:
            time.sleep(1)
            
    except Exception as e:
        logger.critical(f"Ana program hatası: {str(e)}")
        print(f"Kritik hata: {str(e)}")
        cleanup()

if __name__ == "__main__":
    main() 