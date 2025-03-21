"""
USB veya GPIO üzerinden röle kontrolü için modül.
Hem donanım hem de simülasyon modunda çalışır.
"""

import logging
import time
import os
import threading
from utils.simulation import is_simulation_mode
from utils.exceptions import RelayInitializationError

# USB röle kartı için
try:
    import usbrelay_py
except ImportError:
    usbrelay_py = None

# GPIO röle kontrolü için
try:
    from gpiozero import OutputDevice
except ImportError:
    OutputDevice = None


class RelayController:
    """
    Röle kontrol sınıfı. USB veya GPIO üzerinden röle kontrolü sağlar.
    """
    
    def __init__(self, relay_type="usb", pin_or_id=None, normally_open=True, simulation_mode=None):
        """
        Röle kontrolcüsü başlatma.
        
        Args:
            relay_type: Röle tipi ("usb" veya "gpio")
            pin_or_id: GPIO pin numarası veya USB röle ID'si
            normally_open: Rölenin normalde açık (NO) veya kapalı (NC) olduğunu belirtir
            simulation_mode: Simülasyon modu zorlaması (None ise global ayarı kullan)
        """
        self.logger = logging.getLogger(__name__)
        
        # Parametreleri kaydet
        self.relay_type = relay_type.lower()
        self.pin_or_id = pin_or_id
        self.normally_open = normally_open
        
        # Simülasyon modu kontrolü
        self.simulation_mode = simulation_mode if simulation_mode is not None else is_simulation_mode()
        self.logger.info(f"Röle kontrolcüsü {'simülasyon modunda' if self.simulation_mode else 'gerçek donanım modunda'} başlatılıyor")
        
        # Röle durumu
        self.state = False  # Kapalı (non-activated)
        self.lock = threading.Lock()
        
        # Röle tipini kontrol et
        if not self.simulation_mode:
            if self.relay_type == "usb":
                self._init_usb_relay()
            elif self.relay_type == "gpio":
                self._init_gpio_relay()
            else:
                self.logger.error(f"Geçersiz röle tipi: {self.relay_type}")
                raise ValueError(f"Geçersiz röle tipi: {self.relay_type}")
        else:
            self.logger.info(f"Simülasyon modu: {self.relay_type} röle simüle ediliyor")

    def _init_usb_relay(self):
        """
        USB röle kartını başlat
        """
        try:
            if usbrelay_py is None:
                self.logger.error("usbrelay_py modülü bulunamadı")
                raise RelayInitializationError("usbrelay_py modülü bulunamadı - 'pip install usbrelay-py' komutunu çalıştırın")
            
            # USB röle listesi al
            relays = usbrelay_py.board_details()
            if not relays:
                self.logger.warning("USB röle kartı bulunamadı, simülasyon moduna geçiliyor")
                self.simulation_mode = True
                return
                
            # Belirli bir röle ID'si verilmediyse ilk röleyi kullan
            if self.pin_or_id is None:
                # İlk röle kartından ilk röleyi al
                first_board = relays[0]
                self.pin_or_id = f"{first_board[0]}_{1}"  # board_id_relay_number
                self.logger.info(f"Röle ID'si belirtilmedi, ilk röleyi kullanıyorum: {self.pin_or_id}")
            
            # Röle ID formatını kontrol et
            if not isinstance(self.pin_or_id, str) or '_' not in self.pin_or_id:
                self.logger.error(f"Geçersiz USB röle ID'si formatı: {self.pin_or_id}")
                self.simulation_mode = True
                return
                
            # Rölenin gerçekten var olduğunu kontrol et
            board_id, relay_num = self.pin_or_id.split('_', 1)
            found = False
            
            for board in relays:
                if board[0] == board_id:
                    found = True
                    break
                    
            if not found:
                self.logger.warning(f"USB röle ID'si {board_id} bulunamadı, simülasyon moduna geçiliyor")
                self.simulation_mode = True
                return
                
            self.logger.info(f"USB röle başlatıldı: {self.pin_or_id}")
            
        except Exception as e:
            self.logger.error(f"USB röle başlatma hatası: {e}")
            self.simulation_mode = True

    def _init_gpio_relay(self):
        """
        GPIO röle kartını başlat
        """
        try:
            if OutputDevice is None:
                self.logger.error("gpiozero modülü bulunamadı")
                raise RelayInitializationError("gpiozero modülü bulunamadı - 'pip install gpiozero' komutunu çalıştırın")
            
            # GPIO pin numarası kontrol et
            if self.pin_or_id is None:
                self.logger.error("GPIO pin numarası belirtilmedi")
                raise RelayInitializationError("GPIO pin numarası belirtilmedi")
                
            # Pin numarasını tamsayıya çevir
            try:
                pin_num = int(self.pin_or_id)
            except ValueError:
                self.logger.error(f"Geçersiz GPIO pin numarası: {self.pin_or_id}")
                raise RelayInitializationError(f"Geçersiz GPIO pin numarası: {self.pin_or_id}")
                
            # GPIO çıkış cihazını oluştur
            try:
                self.gpio_relay = OutputDevice(pin_num, active_high=self.normally_open)
                self.logger.info(f"GPIO röle başlatıldı: Pin {pin_num} (active_high={self.normally_open})")
            except Exception as e:
                self.logger.error(f"GPIO çıkış cihazı oluşturma hatası: {e}")
                raise RelayInitializationError(f"GPIO çıkış cihazı oluşturma hatası: {e}")
                
        except Exception as e:
            self.logger.error(f"GPIO röle başlatma hatası: {e}")
            self.simulation_mode = True

    def set_state(self, state):
        """
        Röle durumunu ayarla.
        
        Args:
            state: True (aktif) veya False (deaktif)
        
        Returns:
            bool: İşlem başarılı ise True
        """
        with self.lock:
            self.state = state
            
            if self.simulation_mode:
                self.logger.info(f"Simülasyon modu: Röle {self.pin_or_id} {'aktif' if state else 'deaktif'}")
                return True
                
            try:
                if self.relay_type == "usb":
                    return self._set_usb_relay_state(state)
                elif self.relay_type == "gpio":
                    return self._set_gpio_relay_state(state)
                else:
                    self.logger.error(f"Geçersiz röle tipi: {self.relay_type}")
                    return False
            except Exception as e:
                self.logger.error(f"Röle durumu ayarlama hatası: {e}")
                return False

    def _set_usb_relay_state(self, state):
        """
        USB röle durumunu ayarla.
        
        Args:
            state: True (aktif) veya False (deaktif)
        
        Returns:
            bool: İşlem başarılı ise True
        """
        try:
            if usbrelay_py is None:
                self.logger.error("usbrelay_py modülü bulunamadı")
                return False
                
            # Röle ID'sini ayrıştır
            board_id, relay_num = self.pin_or_id.split('_', 1)
            relay_num = int(relay_num)
            
            # Normally Open (NO) röle için durum mantığını kontrol et
            relay_state = 1 if state else 0
            if not self.normally_open:
                relay_state = 1 - relay_state  # Tersini al (0->1, 1->0)
                
            # Röle durumunu ayarla
            result = usbrelay_py.board_control(board_id, relay_num, relay_state)
            
            if result == 0:
                self.logger.info(f"USB röle {self.pin_or_id} {'aktif' if state else 'deaktif'}")
                return True
            else:
                self.logger.error(f"USB röle kontrolü başarısız oldu: Hata kodu {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"USB röle durumu ayarlama hatası: {e}")
            return False

    def _set_gpio_relay_state(self, state):
        """
        GPIO röle durumunu ayarla.
        
        Args:
            state: True (aktif) veya False (deaktif)
        
        Returns:
            bool: İşlem başarılı ise True
        """
        try:
            if not hasattr(self, 'gpio_relay'):
                self.logger.error("GPIO röle başlatılmadı")
                return False
                
            # Röle durumunu ayarla
            if state:
                self.gpio_relay.on()
            else:
                self.gpio_relay.off()
                
            self.logger.info(f"GPIO röle Pin {self.pin_or_id} {'aktif' if state else 'deaktif'}")
            return True
            
        except Exception as e:
            self.logger.error(f"GPIO röle durumu ayarlama hatası: {e}")
            return False

    def activate(self):
        """
        Röleyi aktifleştir.
        
        Returns:
            bool: İşlem başarılı ise True
        """
        return self.set_state(True)

    def deactivate(self):
        """
        Röleyi deaktifleştir.
        
        Returns:
            bool: İşlem başarılı ise True
        """
        return self.set_state(False)

    def toggle(self):
        """
        Röle durumunu tersine çevir.
        
        Returns:
            bool: İşlem başarılı ise True
        """
        with self.lock:
            return self.set_state(not self.state)

    def pulse(self, duration=1.0):
        """
        Röleyi belirli bir süre için aktifleştir, sonra deaktifleştir.
        
        Args:
            duration: Aktivasyon süresi (saniye)
        
        Returns:
            bool: İşlem başarılı ise True
        """
        success = self.activate()
        time.sleep(duration)
        return self.deactivate() and success

    def get_state(self):
        """
        Rölenin mevcut durumunu döndür.
        
        Returns:
            bool: Röle durumu (True: aktif, False: deaktif)
        """
        with self.lock:
            return self.state

    def close(self):
        """
        Röle kontrolcüsünü kapat ve kaynakları temizle.
        """
        try:
            if not self.simulation_mode and self.relay_type == "gpio" and hasattr(self, 'gpio_relay'):
                # GPIO röleyi deaktifleştir ve kapat
                self.gpio_relay.off()
                self.gpio_relay.close()
                self.logger.info(f"GPIO röle Pin {self.pin_or_id} kapatıldı")
                
            # USB röle için özel bir kapanış işlemi yok
            if not self.simulation_mode and self.relay_type == "usb":
                # Kapanırken röleyi deaktifleştir
                self.deactivate()
                self.logger.info(f"USB röle {self.pin_or_id} kapatıldı")
                
        except Exception as e:
            self.logger.error(f"Röle kapatma hatası: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# USB röle bağlantılarını listeleyen yardımcı fonksiyon
def list_usb_relays():
    """
    Bağlı USB röle kartlarını listele.
    
    Returns:
        list: Röle kartları listesi
    """
    if is_simulation_mode():
        print("Simülasyon modu: Sanal USB röleler listeleniyor")
        return [("SIMULATED_1", 2), ("SIMULATED_2", 4)]
        
    try:
        if usbrelay_py is None:
            print("usbrelay_py modülü bulunamadı - 'pip install usbrelay-py' komutunu çalıştırın")
            return []
            
        relays = usbrelay_py.board_details()
        
        if not relays:
            print("USB röle kartı bulunamadı")
        else:
            for idx, relay in enumerate(relays):
                print(f"{idx+1}. Röle Kartı: ID={relay[0]}, Kanal Sayısı={relay[1]}")
                for i in range(1, relay[1] + 1):
                    print(f"   Röle {i} ID: {relay[0]}_{i}")
                    
        return relays
        
    except Exception as e:
        print(f"USB röle listeleme hatası: {e}")
        return [] 