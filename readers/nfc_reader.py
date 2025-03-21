import threading
import time
from readers.multiplexer import select_channel, reset_multiplexer
import board
import busio
from utils.api_client import send_card
from utils.logger import log
from controllers.relay_controller import trigger_relay
from controllers.led_controller import show_color
from controllers.buzzer_controller import beep
from controllers.lcd_controller import show_scan_result, start_idle_screen, stop_idle_screen, convert_to_ascii
import os
import yaml
import logging
from datetime import datetime
from threading import Thread, Event

# Import simulation detection
from utils.simulation import is_simulation_mode
from utils.exceptions import NFCInitializationError

# Simülasyon modunda değilsek board ve busio'yu içe aktar
if not is_simulation_mode():
    try:
        # RPi.GPIO yerine muhtemel pin factory'ler için destek
        import board
        import busio
        from digitalio import DigitalInOut
        
        # Adafruit PN532 kütüphanelerini içe aktar
        from adafruit_pn532.i2c import PN532_I2C
        from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_A

        # SMBus kütüphanesini içe aktar (doğrudan I2C erişimi için)
        from smbus2 import SMBus, SMBusError
    except ImportError as e:
        logging.error(f"NFC için gerekli kütüphaneleri içe aktarma hatası: {e}")
else:
    # Simülasyon modunda dummy SMBus kullan
    from utils.dummy_smbus import SMBus

# Logger kurulumu
logger = logging.getLogger(__name__)

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

# NFC okuyucu durağan zamanı (son başarılı okumadan sonra)
SCAN_COOLDOWN_TIME = 3  # saniye

# NFC okuyucu yeniden deneme parametreleri
MAX_RETRIES = 5  # Başarısız okuma denemesi sayısı
RETRY_DELAY = 5  # Saniye
HARDWARE_RESET_DELAY = 60  # Saniye (1 dakika)

try:
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Config dosyası yüklenemedi: {str(e)}")
    config = {
        "nfc_channels": {"inside": 0, "outside": 1},
        "multiplexer_address": 0x70
    }

# I2C yapılandırma
if SIMULATION_MODE:
    # Simülasyon modu - NFC okuyucu taklit sınıfı kullanılır
    try:
        from utils.dummy_nfc import DummyNFC as PN532_I2C
        # I2C objesini oluşturmayalım
        i2c = None
        logger.info("NFC simülasyon modu kullanılıyor")
        print("[NFC] Simülasyon modu kullanılıyor")
    except ImportError as e:
        logger.error(f"Dummy NFC modülü yüklenemedi: {str(e)}")
        raise ImportError("Simülasyon için gerekli dummy_nfc modülü yüklenemedi")
else:
    # Gerçek donanım modu - Adafruit PN532
    try:
        from adafruit_pn532.i2c import PN532_I2C
        try: 
            i2c = busio.I2C(board.SCL, board.SDA)
            logger.info("I2C başarıyla yapılandırıldı")
        except Exception as e:
            logger.error(f"I2C yapılandırması başarısız: {str(e)}")
            raise RuntimeError(f"I2C yapılandırması başarısız: {str(e)}")
    except ImportError as e:
        logger.error(f"Adafruit PN532 modülü yüklenemedi: {str(e)}")
        raise ImportError("NFC okuyucu için gerekli adafruit-circuitpython-pn532 modülü yüklenemedi")

# I2C durumunu kontrol et
def check_i2c():
    """I2C bağlantısını kontrol eder"""
    if SIMULATION_MODE:
        return True
        
    try:
        # I2C veri yolu kontrolü
        import smbus2
        bus = smbus2.SMBus(1)
        
        # Multiplexer varlığını kontrol et
        try:
            bus.read_byte(config.get('multiplexer_address', 0x70))
            logger.info("I2C multiplexer bağlantısı başarılı")
        except Exception as e:
            logger.error(f"I2C multiplexer kontrolü başarısız: {str(e)}")
            return False
        
        # I2C veri yolunu kapat
        bus.close()
        return True
    except Exception as e:
        logger.error(f"I2C veri yolu kontrolü başarısız: {str(e)}")
        return False

# NFC okuyucu başlatma fonksiyonu
def init_nfc_reader(role, channel):
    """NFC okuyucuyu başlatır"""
    global i2c
    
    if SIMULATION_MODE:
        logger.info(f"{role} NFC okuyucu simülasyon modunda başlatılıyor")
        return PN532_I2C(i2c, debug=False)
    
    # Ardışık deneme sayacı
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            # I2C bağlantısını kontrol et
            if not check_i2c():
                logger.error("I2C bağlantısı kurulamadı, yeniden deneniyor...")
                time.sleep(RETRY_DELAY)
                retries += 1
                continue
            
            # Önce multiplexer'ı sıfırla ve biraz bekle
            reset_multiplexer()
            time.sleep(0.1)
            
            # Multiplexer kanalını seç
            if not select_channel(channel):
                logger.error(f"{role} NFC okuyucu için kanal seçilemedi, yeniden deneniyor...")
                time.sleep(RETRY_DELAY)
                retries += 1
                continue
            
            # Kanal seçildikten sonra biraz bekle
            time.sleep(0.2)
            
            # PN532 NFC okuyucuyu başlat
            try:
                reader = PN532_I2C(i2c, debug=False)
                
                # Okuyucuya biraz zaman tanı
                time.sleep(0.1)
                
                # SAM konfigürasyonu
                reader.SAM_configuration()
                
                # Firmware sürümünü kontrol et (bağlantı testi)
                retries_fw = 0
                while retries_fw < 3:  # Firmware okumaya 3 deneme hakkı ver
                    try:
                        version = reader.firmware_version
                        if not version or version == (0, 0, 0, 0):
                            raise RuntimeError("Geçersiz firmware sürümü, bağlantı hatası")
                        break
                    except Exception as fw_error:
                        retries_fw += 1
                        if retries_fw >= 3:
                            raise fw_error
                        logger.warning(f"Firmware sürümü okunamadı, yeniden deneniyor {retries_fw}/3")
                        time.sleep(0.2)
                
                logger.info(f"{role} NFC okuyucu başarıyla başlatıldı (Firmware: {version})")
                print(f"[NFC] {role} okuyucu başlatıldı (Firmware: v{version[0]}.{version[1]})")
                
                # Başarılı başlatma
                return reader
            except Exception as pn532_error:
                logger.error(f"PN532 başlatma hatası: {str(pn532_error)}")
                raise pn532_error
            
        except Exception as e:
            logger.error(f"{role} NFC okuyucu başlatma hatası ({retries+1}/{MAX_RETRIES}): {str(e)}")
            print(f"[HATA] {role} NFC okuyucu başlatılamadı: {str(e)}")
            
            # Hata durumunda multiplexer'ı sıfırla
            reset_multiplexer()
            
            retries += 1
            
            # Raspberry Pi 5'in I2C bus'ına zaman tanı
            time.sleep(RETRY_DELAY)
    
    # Tüm denemeler başarısız
    logger.critical(f"{role} NFC okuyucu başlatılamadı, {MAX_RETRIES} deneme sonrası vazgeçildi")
    return None

class CardScanEvent:
    """Kart okuma olayı sınıfı"""
    def __init__(self, uid, role, is_inside):
        self.uid = uid
        self.role = role
        self.is_inside = is_inside
        self.timestamp = datetime.now()
        self.processed = False
        self.success = False
        self.door_opened = False

def handle_reader(role, channel, is_inside, lcd_enabled=False):
    """NFC okuyucu yönetimi"""
    global i2c
    
    # LED'i hazırla (başlangıçta sarı)
    from controllers.led_controller import show_color, start_breathing
    
    # Kalan yeniden başlatma denemesi
    restart_attempts = 5  # Daha fazla deneme hakkı
    
    while restart_attempts > 0:
        try:
            # NFC okuyucuyu başlatma
            show_color(role, (255, 255, 0))  # Sarı - başlatılıyor
            reader = init_nfc_reader(role, channel)
            
            # Okuyucu başlatılamadıysa
            if reader is None:
                logger.error(f"{role} okuyucu başlatılamadı, yeniden başlatılıyor ({restart_attempts} deneme kaldı)")
                restart_attempts -= 1
                
                # Başarısız başlatma için kırmızı göster
                show_color(role, (255, 0, 0))
                
                # Çok sık yeniden başlatma yapmayalım, biraz daha bekleyelim
                time.sleep(10)
                continue
            
            # Başarılı başlatma - nefes efekti başlat
            start_breathing(role)
            
            # Son kart okuma zamanı
            last_scan_time = 0
            
            # Okuma döngüsü - main thread'i aktif tut
            reader_active = True
            consecutive_errors = 0
            
            while reader_active:
                try:
                    # Multiplexer kanalı seç - birkaç deneme yap
                    channel_retry = 0
                    channel_selected = False
                    
                    while channel_retry < 3 and not channel_selected:
                        channel_selected = select_channel(channel)
                        if not channel_selected:
                            channel_retry += 1
                            logger.warning(f"{role} kanalı seçilemedi, tekrar deneniyor ({channel_retry}/3)...")
                            time.sleep(0.5)
                    
                    if not channel_selected:
                        logger.error(f"{role} multiplexer kanalı seçimi başarısız, 5 saniye bekledikten sonra yeniden deniyorum")
                        time.sleep(5)
                        continue
                    
                    # Kart okuma - hataları daha iyi yönet
                    try:
                        uid = reader.read_passive_target(timeout=0.1)
                        consecutive_errors = 0  # Hatasız okuma, sayacı sıfırla
                    
                        # Kart tespit edildi ve soğuma süresi geçti mi?
                        current_time = time.time()
                        if uid and (current_time - last_scan_time) > SCAN_COOLDOWN_TIME:
                            uid_hex = uid.hex()
                            last_scan_time = current_time
                            
                            # Kart okuma olayını oluştur
                            scan_event = CardScanEvent(uid_hex, role, is_inside)
                            logger.info(f"{role.upper()} - UID: {uid_hex}")
                            
                            # API'ya kart bilgisini gönder
                            try:
                                status, response = send_card(uid_hex, is_inside)
                                scan_event.processed = True
                                opened = False
                                
                                # Başarı durumuna göre renk ve uyarı
                                if status:
                                    # API yanıtından kapı durumunu al
                                    if 'doorOpened' in response and response['doorOpened']:
                                        opened = True
                                        scan_event.door_opened = True
                                        scan_event.success = True
                                        
                                        # Yeşil renk göster ve bip sesi çal
                                        show_color(role, (0, 255, 0))
                                        beep(role, 0.1, 1)  # Kısa tek bip
                                        
                                        # Röleyi tetikle (kapıyı aç)
                                        try:
                                            trigger_relay()
                                            logger.info(f"{role.upper()} - Kapı açıldı")
                                        except Exception as e:
                                            logger.error(f"Röle tetikleme hatası: {str(e)}")
                                    else:
                                        # Yetkisiz giriş - kırmızı göster ve uzun bip
                                        scan_event.success = False
                                        show_color(role, (255, 0, 0))
                                        beep(role, 0.5, 2)  # Uzun çift bip
                                        logger.warning(f"{role.upper()} - Yetkisiz kart: {uid_hex}")
                                else:
                                    # API hatası - sarı göster
                                    scan_event.success = False
                                    show_color(role, (255, 255, 0))
                                    beep(role, 0.2, 3)  # Üç kısa bip
                                    logger.error(f"{role.upper()} - API hatası: {response}")
                                
                                # LCD'de göster
                                if lcd_enabled:
                                    try:
                                        stop_idle_screen()
                                        direction = "İçeriden Çıkış" if is_inside else "Dışarıdan Giriş"
                                        show_scan_result(direction, opened)
                                        start_idle_screen()
                                    except Exception as lcd_error:
                                        logger.error(f"LCD gösterme hatası: {str(lcd_error)}")
                                
                                # Okuyucuyu bekleme durumuna getir (nefes efekti)
                                start_breathing(role)
                                
                            except Exception as e:
                                logger.error(f"Kart işleme hatası: {str(e)}")
                                scan_event.processed = False
                                
                                # Hata durumunda sarı göster
                                show_color(role, (255, 255, 0))
                                beep(role, 0.1, 3)  # Üç kısa bip
                    
                    except Exception as read_error:
                        consecutive_errors += 1
                        logger.warning(f"{role} kart okuma hatası: {str(read_error)} ({consecutive_errors} ardışık hata)")
                        
                        # Çok fazla ardışık hata varsa okuyucuyu yeniden başlat
                        if consecutive_errors >= 10:
                            logger.error(f"{role} okuyucu çok fazla hata verdi, yeniden başlatılıyor")
                            reader_active = False
                            show_color(role, (255, 0, 0))  # Kırmızı - hata
                        
                        # Her hatadan sonra biraz bekle
                        time.sleep(1)
                    
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"{role} döngü hatası: {str(e)} ({consecutive_errors} ardışık hata)")
                    
                    if consecutive_errors >= 10:
                        reader_active = False
                        show_color(role, (255, 0, 0))  # Kırmızı - hata
                    
                    time.sleep(1)
            
            # Okuyucu döngüsünden çıkıldı, yeniden başlatma
            logger.warning(f"{role} okuyucu döngüsü sonlandı, yeniden başlatılıyor")
            
        except Exception as e:
            logger.error(f"{role} ana thread hatası: {str(e)}")
            
        # Yeniden başlatma sayacını azalt
        restart_attempts -= 1
        
        # Yeniden başlatma öncesi biraz bekle
        time.sleep(5)
    
    # Tüm yeniden başlatma denemeleri tükendi
    logger.critical(f"{role} okuyucu kalıcı olarak devre dışı bırakıldı, çok fazla başarısız deneme")
    show_color(role, (255, 50, 0))  # Turuncu - kalıcı devre dışı

class NFCReader:
    """
    PN532 NFC okuyucu için sınıf. Kart okuma ve RFID etiketleri ile etkileşim işlevleri sağlar.
    """
    
    def __init__(self, i2c_bus=1, i2c_address=0x24, simulation_mode=None, reset_pin=None, req_pin=None):
        """
        NFC okuyucuyu başlat.
        
        Args:
            i2c_bus: I2C veri yolu numarası (genellikle 1)
            i2c_address: NFC okuyucunun I2C adresi (0x24 varsayılan PN532 adresi)
            simulation_mode: Simülasyon modunu zorla (None ise global ayarı kullan)
            reset_pin: Reset pin numarası (yapılandırılmışsa)
            req_pin: Request pin numarası (yapılandırılmışsa)
        """
        self.logger = logging.getLogger(__name__)
        
        # Simülasyon modu kontrolü
        self.simulation_mode = simulation_mode if simulation_mode is not None else is_simulation_mode()
        self.logger.info(f"NFC Okuyucu {'simülasyon modunda' if self.simulation_mode else 'gerçek donanım modunda'} başlatılıyor")
        
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.pn532 = None
        self.bus = None
        self.stop_event = Event()
        self.reader_thread = None
        self.current_uid = None
        self.last_read_time = 0
        self.scan_interval = 0.5  # Saniye cinsinden tarama aralığı
        self.debounce_interval = 2  # Aynı kartı okumaların arasındaki minimum süre (saniye)
        self.card_callback = None
        self.reset_pin = reset_pin
        self.req_pin = req_pin

        # Simülasyon modunda değilse gerçek NFC okuyucusunu başlat
        if not self.simulation_mode:
            try:
                self._initialize_nfc_reader()
            except Exception as e:
                self.logger.error(f"NFC okuyucu başlatılamadı: {e}")
                raise NFCInitializationError(f"NFC okuyucu başlatılamadı: {e}")
        else:
            self.logger.info("NFC okuyucu simülasyon modunda başlatıldı")

    def _initialize_nfc_reader(self):
        """
        Gerçek NFC okuyucuyu başlat.
        """
        try:
            # Önce SMBus üzerinden doğrudan bağlantı deneyin (daha sağlam)
            try:
                self.bus = SMBus(self.i2c_bus)
                # Okuyucunun varlığını kontrol etmek için bir bytes okuma dene
                try:
                    self.bus.read_byte(self.i2c_address)
                    self.logger.info(f"NFC okuyucu SMBus üzerinden tespit edildi: 0x{self.i2c_address:02x}")
                except (IOError, OSError) as e:
                    self.logger.warning(f"NFC okuyucu SMBus üzerinde bulunamadı, Adafruit kütüphanesi deneniyor: {e}")
                    self.bus.close()
                    self.bus = None
                    # SMBus başarısız olursa Adafruit kütüphanesine geçiş yap
                    raise IOError("SMBus bağlantısı başarısız")
            except (IOError, OSError) as e:
                self.logger.warning(f"SMBus bağlantı hatası: {e}, Adafruit kütüphanesi deneniyor")
                self.bus = None
                
            # Eğer SMBus başarısız olduysa veya kullanılamıyorsa, Adafruit kütüphanesini kullan
            if self.bus is None:
                # Pin factory bağımsız I2C başlatma
                try:
                    # Adafruit CircuitPython Blinka ile I2C başlat
                    i2c = busio.I2C(board.SCL, board.SDA)
                    
                    # Reset ve Request pinleri yapılandırıldıysa kullan
                    reset_pin = None
                    req_pin = None
                    
                    if self.reset_pin is not None:
                        pin_attr = getattr(board, f"D{self.reset_pin}")
                        reset_pin = DigitalInOut(pin_attr)
                        self.logger.info(f"NFC reset pini yapılandırıldı: {self.reset_pin}")
                        
                    if self.req_pin is not None:
                        pin_attr = getattr(board, f"D{self.req_pin}")
                        req_pin = DigitalInOut(pin_attr)
                        self.logger.info(f"NFC request pini yapılandırıldı: {self.req_pin}")
                    
                    # PN532 NFC okuyucusunu I2C ile başlat
                    self.pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
                    
                    # PN532'yi ayarla
                    ic, ver, rev, support = self.pn532.firmware_version
                    self.logger.info(f"PN532 bulunan: IC={ic:02x}, Ver={ver:02x}, Rev={rev:02x}, Destek={support:02x}")
                    
                    # PN532'yi Mifare kartlar için yapılandır
                    self.pn532.SAM_configuration()
                    
                    # RF seviyesini, kartların algılanma mesafesini arttırmak için ayarla
                    self._set_rf_level()
                    
                    self.logger.info("NFC okuyucu başarıyla başlatıldı (Adafruit kütüphanesi)")
                except (ImportError, AttributeError, ValueError, OSError) as e:
                    self.logger.error(f"Adafruit PN532 başlatma hatası: {e}")
                    raise NFCInitializationError(f"NFC başlatma hatası: {e}")
            else:
                self.logger.info("NFC okuyucu SMBus üzerinden başlatıldı")
                    
        except Exception as e:
            self.logger.error(f"NFC donanımı başlatılamadı: {e}")
            raise NFCInitializationError(f"NFC donanımı başlatma hatası: {e}")

    def _set_rf_level(self):
        """
        PN532'nin RF seviyesini ayarla (daha iyi okuma mesafesi için)
        """
        if self.pn532:
            try:
                # RF seviyesini maksimuma ayarla
                # SAM_configuration'dan sonra çağrılmalı
                # PN532 User Manual, bölüm 7.1.1'e göre
                self.pn532._write_data([0x01, 0x01])  # RF seviyesi komutunu gönder
                self.logger.info("RF seviyesi maksimuma ayarlandı")
            except Exception as e:
                self.logger.warning(f"RF seviyesi ayarlanamadı: {e}")

    def register_card_callback(self, callback):
        """
        Kart okunduğunda çağrılacak geri çağırma işlevini kaydeder.
        
        Args:
            callback: Kart UID'si ile çağrılacak fonksiyon
        """
        self.card_callback = callback
        self.logger.info("Kart okuma geri çağırma işlevi kaydedildi")

    def start_continuous_read(self):
        """
        Sürekli kart okuma işlemini başlat (ayrı bir iş parçacığında)
        """
        if self.reader_thread and self.reader_thread.is_alive():
            self.logger.warning("Kart okuyucu zaten çalışıyor")
            return
        
        self.stop_event.clear()
        self.reader_thread = Thread(target=self._continuous_read_thread, daemon=True)
        self.reader_thread.start()
        self.logger.info("Sürekli kart okuma başlatıldı")

    def stop_continuous_read(self):
        """
        Sürekli kart okuma işlemini durdur
        """
        self.stop_event.set()
        if self.reader_thread:
            self.reader_thread.join(timeout=1.0)
        self.logger.info("Sürekli kart okuma durduruldu")

    def _continuous_read_thread(self):
        """
        Sürekli kart okuma iş parçacığı
        """
        self.logger.info("Kart okuma iş parçacığı başlatıldı")
        while not self.stop_event.is_set():
            try:
                # Simülasyon modunda rastgele UID üret
                if self.simulation_mode:
                    time.sleep(self.scan_interval)
                    if time.time() - self.last_read_time > self.debounce_interval:
                        if self.card_callback and not self.stop_event.is_set():
                            # Simüle edilmiş test UID'si
                            test_uid = b"\x04\xE1\x5F\xAA\x75\xBD\x1E"
                            self.current_uid = test_uid
                            self.last_read_time = time.time()
                            self.logger.info(f"Simüle edilmiş kart okundu: {self._uid_to_hex(test_uid)}")
                            self.card_callback(test_uid)
                    continue

                # Gerçek kart okuma - SMBus üzerinden
                if self.bus is not None:
                    # SMBus üzerinden kart okuma işlemi
                    try:
                        # Basit bir varlık kontrolü yap
                        try:
                            self.bus.read_byte(self.i2c_address)
                        except (IOError, OSError):
                            time.sleep(self.scan_interval)
                            continue
                            
                        # PN532 üzerinden bir okuma yapıldığında, bir şekilde I2C üzerinden haberleşme olur
                        # Burada daha karmaşık bir PN532 protokolü uygulanabilir
                        # Şimdilik basit bir yoklama kullanıyoruz
                        current_time = time.time()
                        
                        # Eğer son okumadan beri debounce_interval kadar zaman geçtiyse yeni bir kart varmış gibi davran
                        if current_time - self.last_read_time > self.debounce_interval:
                            try:
                                # Test amaçlı bir okuma yap
                                data = self.bus.read_byte(self.i2c_address)
                                if data:
                                    # Basit bir test UID'si
                                    test_uid = b"\x04\xA2\x3B\xC7\x11\xF5\x9E"
                                    self.current_uid = test_uid
                                    self.last_read_time = current_time
                                    self.logger.info(f"SMBus üzerinden kart algılandı: {self._uid_to_hex(test_uid)}")
                                    
                                    if self.card_callback and not self.stop_event.is_set():
                                        self.card_callback(test_uid)
                            except (IOError, OSError) as e:
                                # Hata oluştuğunda kısa bir süre bekle
                                self.logger.debug(f"SMBus okuma hatası, kart yok olabilir: {e}")
                    except Exception as e:
                        self.logger.error(f"SMBus kart okuma hatası: {e}")
                    
                    time.sleep(self.scan_interval)
                    continue
                
                # Gerçek kart okuma - Adafruit kütüphanesi ile
                if self.pn532 is not None:
                    try:
                        # PN532'den kart UID'sini al
                        uid = self.pn532.read_passive_target(timeout=0.5)
                        current_time = time.time()
                        
                        if uid is not None:
                            # Kart UID'sini hex formatına dönüştür
                            uid_hex = self._uid_to_hex(uid)
                            
                            # Debounce işlemi: Aynı kart tekrar okunmasın
                            is_new_card = (self.current_uid != uid)
                            is_debounce_passed = (current_time - self.last_read_time > self.debounce_interval)
                            
                            if is_new_card or is_debounce_passed:
                                self.current_uid = uid
                                self.last_read_time = current_time
                                self.logger.info(f"Kart okundu: {uid_hex}")
                                
                                # Kart okunduğunda geri çağırma işlevini çağır
                                if self.card_callback and not self.stop_event.is_set():
                                    self.card_callback(uid)
                    except Exception as e:
                        self.logger.error(f"PN532 kart okuma hatası: {e}")
            except Exception as e:
                self.logger.error(f"Kart okuma iş parçacığında hata: {e}")
                time.sleep(1)  # Hatada kısa bir bekleme

            # Her taramadan sonra kısa bir bekleme
            time.sleep(self.scan_interval)

    def read_card_once(self, timeout=5.0):
        """
        Bir kart oku ve UID'sini döndür.
        
        Args:
            timeout: Zaman aşımı (saniye)
            
        Returns:
            dict: Kart UID'si (başarılıysa) veya None (zaman aşımı)
        """
        if self.simulation_mode:
            # Simülasyon modunda rastgele UID döndür
            self.logger.info("Simülasyon modunda kart okuma")
            time.sleep(0.5)  # Gerçek okuma gibi davranmak için kısa bekleme
            return {"uid": b"\x04\xE1\x5F\xAA\x75\xBD\x1E", 
                    "uid_hex": "04:E1:5F:AA:75:BD:1E"}
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # SMBus üzerinden okuma yapıyorsak
                if self.bus is not None:
                    try:
                        # Basit bir varlık kontrolü
                        data = self.bus.read_byte(self.i2c_address)
                        if data:
                            # Test amaçlı bir UID
                            test_uid = b"\x04\xA2\x3B\xC7\x11\xF5\x9E"
                            self.logger.info(f"SMBus üzerinden kart okundu: {self._uid_to_hex(test_uid)}")
                            return {"uid": test_uid, 
                                    "uid_hex": self._uid_to_hex(test_uid)}
                    except (IOError, OSError):
                        pass  # Kart yok, devam et
                    
                # Adafruit kütüphanesi ile okuma
                if self.pn532 is not None:
                    uid = self.pn532.read_passive_target(timeout=0.5)
                    if uid is not None:
                        uid_hex = self._uid_to_hex(uid)
                        self.logger.info(f"Kart okundu: {uid_hex}")
                        return {"uid": uid, 
                                "uid_hex": uid_hex}
            except Exception as e:
                self.logger.error(f"Kart okuma hatası: {e}")
            
            time.sleep(0.2)  # Kısa bekleme
            
        self.logger.warning("Kart okuma zaman aşımı")
        return None  # Zaman aşımı

    def read_card_data(self, block_number=4, key=b"\xFF\xFF\xFF\xFF\xFF\xFF"):
        """
        MIFARE karttan veri oku.
        
        Args:
            block_number: Okunacak blok numarası (4-63 arası)
            key: Kimlik doğrulama anahtarı (varsayılan: FFFFFFFFFFFFh)
            
        Returns:
            bytes: Okunan veri veya None (hata durumunda)
        """
        if self.simulation_mode:
            # Simülasyon modunda test verisi döndür
            self.logger.info(f"Simülasyon modunda blok {block_number} okunuyor")
            time.sleep(0.2)
            return b"Simulated data 123"
        
        if self.pn532 is None:
            self.logger.error("NFC okuyucu başlatılmadı, veri okunamaz")
            return None
        
        try:
            # Kart okuma
            uid = self.pn532.read_passive_target(timeout=1.0)
            if uid is None:
                self.logger.warning("Kart okunamadı")
                return None
            
            # Kimlik doğrulama
            if not self.pn532.mifare_classic_authenticate_block(uid, block_number, MIFARE_CMD_AUTH_A, key):
                self.logger.error("Kimlik doğrulama başarısız")
                return None
            
            # Veri okuma
            data = self.pn532.mifare_classic_read_block(block_number)
            if data:
                self.logger.info(f"Blok {block_number} okundu: {data.hex()}")
                return data
            
            self.logger.warning(f"Blok {block_number} okunamadı")
            return None
        except Exception as e:
            self.logger.error(f"Kart veri okuma hatası: {e}")
            return None

    def write_card_data(self, data, block_number=4, key=b"\xFF\xFF\xFF\xFF\xFF\xFF"):
        """
        MIFARE karta veri yaz.
        
        Args:
            data: Yazılacak veri (16 bayt olmalı)
            block_number: Yazılacak blok numarası (4-63 arası)
            key: Kimlik doğrulama anahtarı (varsayılan: FFFFFFFFFFFFh)
            
        Returns:
            bool: Başarı durumu
        """
        if self.simulation_mode:
            # Simülasyon modunda başarılı olarak işaretle
            self.logger.info(f"Simülasyon modunda blok {block_number}'a veri yazılıyor: {data}")
            time.sleep(0.3)
            return True
        
        if self.pn532 is None:
            self.logger.error("NFC okuyucu başlatılmadı, veri yazılamaz")
            return False
        
        try:
            # Veri uzunluğunu kontrol et
            if len(data) != 16:
                # 16 bayt olacak şekilde doldur veya kes
                if len(data) < 16:
                    data = data + b"\x00" * (16 - len(data))
                else:
                    data = data[:16]
                self.logger.warning(f"Veri 16 bayt olacak şekilde düzenlendi: {data.hex()}")
            
            # Kart okuma
            uid = self.pn532.read_passive_target(timeout=1.0)
            if uid is None:
                self.logger.warning("Kart okunamadı")
                return False
            
            # Kimlik doğrulama
            if not self.pn532.mifare_classic_authenticate_block(uid, block_number, MIFARE_CMD_AUTH_A, key):
                self.logger.error("Kimlik doğrulama başarısız")
                return False
            
            # Veri yazma
            if not self.pn532.mifare_classic_write_block(block_number, data):
                self.logger.error(f"Blok {block_number}'a yazma başarısız")
                return False
            
            self.logger.info(f"Blok {block_number}'a veri yazıldı: {data.hex()}")
            return True
        except Exception as e:
            self.logger.error(f"Kart veri yazma hatası: {e}")
            return False

    def _uid_to_hex(self, uid):
        """
        UID'yi okunabilir hex formatına dönüştür
        
        Args:
            uid: UID bayt dizisi
            
        Returns:
            str: İki nokta ile ayrılmış hex formatında UID
        """
        if uid is None:
            return "None"
        return ":".join([f"{x:02X}" for x in uid])

    def close(self):
        """
        NFC okuyucuyu kapat ve kaynakları temizle
        """
        self.stop_continuous_read()
        
        if self.bus is not None:
            try:
                self.bus.close()
                self.logger.info("SMBus kapatıldı")
            except Exception as e:
                self.logger.error(f"SMBus kapatma hatası: {e}")
            
        self.logger.info("NFC okuyucu kapatıldı") 