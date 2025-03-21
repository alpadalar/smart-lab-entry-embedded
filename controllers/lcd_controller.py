from datetime import datetime
from readers.multiplexer import select_channel
import yaml
import time
import threading
import os
import logging
import unicodedata

# Logger kurulumu
logger = logging.getLogger(__name__)

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

try:
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Config dosyası yüklenemedi: {str(e)}")
    config = {"lcd_channel": 2, "lcd_address": 0x27}  # Varsayılan değerler

# Türkçe gün isimleri ve ASCII karşılıkları
days_tr = ['Pzt', 'Sal', 'Car', 'Per', 'Cum', 'Cmt', 'Paz']

# Özel Türkçe karakterler için özel karakterler ve eşleşmeleri
tr_to_ascii = {
    'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
    'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
    'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C',
    'â': 'a', 'î': 'i', 'û': 'u'
}

# Özel karakterler için harita
custom_chars = {}  # boş, özel karakter gerekirse eklenebilir

lcd = None
idle_thread = None
idle_thread_running = False
lcd_lock = threading.Lock()  # LCD'ye erişim için thread kilidi
lcd_error_count = 0
max_lcd_errors = 5  # Bu sayıda ardışık hata sonrası LCD devre dışı bırakılır
lcd_disabled = False

def convert_to_ascii(text):
    """Türkçe karakterleri ASCII eşdeğerlerine dönüştürür"""
    result = ""
    for char in text:
        if char in tr_to_ascii:
            result += tr_to_ascii[char]
        else:
            # Diğer özel karakterleri yakın ASCII eşdeğerlerine dönüştür
            result += unicodedata.normalize('NFKD', char).encode('ASCII', 'ignore').decode('ASCII')
    return result

def init_lcd():
    """LCD'yi başlatır"""
    global lcd, lcd_disabled, lcd_error_count
    
    # LCD zaten devre dışı bırakılmışsa, tekrar deneme
    if lcd_disabled:
        logger.warning("LCD daha önce devre dışı bırakıldı, tekrar deniyorum...")
        lcd_disabled = False
        lcd_error_count = 0
    
    try:
        if SIMULATION_MODE:
            # Simülasyon modu
            from utils.dummy_lcd import CharLCD
            logger.info("LCD simülasyon modu kullanılıyor")
            print("[LCD] Simülasyon modu kullanılıyor")
        else:
            # Gerçek donanım modu
            from RPLCD.i2c import CharLCD
            logger.info("LCD gerçek donanım modu kullanılıyor")
            print("[LCD] Gerçek donanım modu kullanılıyor")
        
        with lcd_lock:
            if not SIMULATION_MODE:
                # I2C multiplexer kanalını seç
                if not select_channel(config['lcd_channel']):
                    logger.error("LCD için multiplexer kanalı seçilemedi")
                    print("[HATA] LCD için multiplexer kanalı seçilemedi")
                    return False
                
                # I2C bağlantı testi
                import smbus2
                try:
                    bus = smbus2.SMBus(1)
                    bus.read_byte(config['lcd_address'])
                    bus.close()
                except Exception as e:
                    logger.error(f"LCD I2C testi başarısız: {str(e)}")
                    print(f"[HATA] LCD I2C testi başarısız: {str(e)}")
                    return False
            
            # LCD'yi farklı parametre seçenekleriyle dene
            try:
                lcd = CharLCD('PCF8574', config['lcd_address'], cols=20, rows=4, charmap='A00')
            except Exception as e:
                logger.warning(f"LCD A00 charmap ile başlatılamadı: {str(e)}, A02 deniyorum...")
                try:
                    lcd = CharLCD('PCF8574', config['lcd_address'], cols=20, rows=4, charmap='A02')
                except Exception as e2:
                    logger.warning(f"LCD A02 charmap ile başlatılamadı: {str(e2)}, varsayılan deniyorum...")
                    lcd = CharLCD('PCF8574', config['lcd_address'], cols=20, rows=4)
            
            # LCD'yi temizle
            try:
                lcd.clear()
                lcd.home()
                lcd.write_string("LCD hazir...")
                time.sleep(1)
                lcd.clear()
                lcd_error_count = 0  # Başarılı başlatma, hata sayacını sıfırla
                print("[LCD] LCD başarıyla başlatıldı")
                return True
            except Exception as e:
                logger.error(f"LCD temizleme hatası: {str(e)}")
                print(f"[HATA] LCD temizleme hatası: {str(e)}")
                return False
            
    except Exception as e:
        logger.error(f"LCD başlatma hatası: {str(e)}")
        print(f"[HATA] LCD başlatılamadı: {str(e)}")
        return False

def _safe_lcd_operation(func):
    """LCD işlemlerini güvenli şekilde gerçekleştiren dekoratör"""
    global lcd_error_count, lcd_disabled, lcd
    
    def wrapper(*args, **kwargs):
        global lcd_disabled
        
        if lcd_disabled:
            return False
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            lcd_error_count += 1
            logger.error(f"LCD işlem hatası ({lcd_error_count}/{max_lcd_errors}): {str(e)}")
            
            # Belirli sayıda hata sonrası LCD'yi devre dışı bırak
            if lcd_error_count >= max_lcd_errors:
                lcd_disabled = True
                logger.error(f"Çok fazla LCD hatası, LCD devre dışı bırakıldı.")
                print(f"[HATA] Çok fazla LCD hatası, LCD devre dışı bırakıldı.")
                stop_idle_screen()
                
                # LCD'yi yeniden başlatmayı dene
                threading.Timer(30.0, init_lcd).start()
            
            return False
    
    return wrapper

def start_idle_screen():
    """Boş ekranı gösterecek bir arka plan thread'i başlatır"""
    global idle_thread, idle_thread_running
    
    if lcd_disabled:
        logger.warning("LCD devre dışı, boş ekran başlatılamıyor")
        return False
    
    if idle_thread is not None and idle_thread.is_alive():
        return True  # Thread zaten çalışıyor
    
    idle_thread_running = True
    idle_thread = threading.Thread(target=update_idle_screen, daemon=True)
    idle_thread.start()
    logger.info("LCD boş ekran thread'i başlatıldı")
    print("[LCD] Boş ekran modu başlatıldı")
    return True

def stop_idle_screen():
    """Boş ekran thread'ini durdurur"""
    global idle_thread_running
    idle_thread_running = False
    logger.info("LCD boş ekran thread'i durduruldu")
    print("[LCD] Boş ekran modu durduruldu")
    return True

@_safe_lcd_operation
def update_idle_screen():
    """LCD'de sürekli güncellenen boş ekranı gösterir"""
    global idle_thread_running
    
    if lcd is None:
        logger.error("LCD başlatılmadan update_idle_screen çağrıldı")
        return
    
    while idle_thread_running and not lcd_disabled:
        try:
            now = datetime.now()
            with lcd_lock:
                if not SIMULATION_MODE:
                    if not select_channel(config['lcd_channel']):
                        time.sleep(1)
                        continue
                
                lcd.cursor_pos = (0, 0)
                lcd.write_string(f"[{days_tr[now.weekday()]} {now.strftime('%Y-%m-%d')}]".ljust(20))
                lcd.cursor_pos = (1, 0)
                lcd.write_string(now.strftime('%H:%M:%S').center(20))
                lcd.cursor_pos = (2, 0)
                lcd.write_string("AI LAB".center(20))
                lcd.cursor_pos = (3, 0)
                lcd.write_string(convert_to_ascii("Kartinizi okutunuz".center(20)))
        except Exception as e:
            logger.error(f"LCD güncellemesi sırasında hata: {str(e)}")
            print(f"[HATA] LCD güncellemesi sırasında hata: {str(e)}")
            time.sleep(3)  # Hata durumunda biraz daha uzun bekle
            continue
        
        time.sleep(1)

@_safe_lcd_operation
def show_scan_result(direction, opened):
    """Kart tarama sonucunu LCD'de gösterir"""
    if lcd is None or lcd_disabled:
        logger.error("LCD başlatılmadan veya devre dışıyken show_scan_result çağrıldı")
        return
    
    try:
        with lcd_lock:
            if not SIMULATION_MODE:
                if not select_channel(config['lcd_channel']):
                    return
            
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(convert_to_ascii("Kart okundu!".center(20)))
            lcd.cursor_pos = (1, 0)
            lcd.write_string(convert_to_ascii(direction.center(20)))
            lcd.cursor_pos = (2, 0)
            lcd.write_string(convert_to_ascii(("Kapi acildi" if opened else "Kapi acilmadi").center(20)))
        
        # Belirlenen süre kadar bekle
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"LCD tarama sonucu gösterimi sırasında hata: {str(e)}")
        print(f"[HATA] LCD tarama sonucu gösterimi sırasında hata: {str(e)}")
        return False

def cleanup():
    """
    LCD kaynaklarını temizler ve serbest bırakır.
    Ana program sonlandığında çağrılır.
    """
    global lcd, idle_thread_running
    
    # Boş ekran thread'ini durdur
    stop_idle_screen()
    
    if lcd is not None and not lcd_disabled:
        try:
            with lcd_lock:
                if not SIMULATION_MODE:
                    select_channel(config['lcd_channel'])
                
                lcd.clear()
                lcd.write_string(convert_to_ascii("Sistem kapatiliyor...".center(20)))
                time.sleep(1)
                lcd.clear()
                
                # LCD'yi kapat (backlight vs.)
                if hasattr(lcd, 'close'):
                    lcd.close()
            
            return True
        except Exception as e:
            logger.error(f"LCD cleanup işlemi sırasında hata: {str(e)}")
            print(f"[HATA] LCD cleanup işlemi sırasında hata: {str(e)}")
            return False
    
    return True 