"""
gpiozero simülasyon modülü - gerçek GPIO olmayan ortamlarda kullanmak için
"""

import time
import threading

class LED:
    def __init__(self, pin):
        self.pin = pin
        self.value = 0
        self.active = True
        self._blink_thread = None
        self._pulse_thread = None
        print(f"[DummyGPIOZero] LED pin {pin} başlatıldı")
        
    def on(self):
        self.value = 1
        print(f"[DummyGPIOZero] LED pin {self.pin} açık")
        
    def off(self):
        self.value = 0
        print(f"[DummyGPIOZero] LED pin {self.pin} kapalı")
        
    def toggle(self):
        self.value = 1 - self.value
        print(f"[DummyGPIOZero] LED pin {self.pin} durumu değiştirildi: {'açık' if self.value else 'kapalı'}")
        
    def _blink_loop(self, on_time, off_time, n, background):
        remaining = n
        while remaining is None or remaining > 0:
            self.on()
            time.sleep(on_time)
            self.off()
            time.sleep(off_time)
            if remaining is not None:
                remaining -= 1
                
    def blink(self, on_time=1, off_time=1, n=None, background=True):
        if self._blink_thread is not None:
            self._blink_thread = None
            
        if background:
            self._blink_thread = threading.Thread(
                target=self._blink_loop, args=(on_time, off_time, n, background), daemon=True)
            self._blink_thread.start()
            print(f"[DummyGPIOZero] LED pin {self.pin} yanıp sönüyor (arka planda)")
        else:
            print(f"[DummyGPIOZero] LED pin {self.pin} yanıp sönüyor")
            self._blink_loop(on_time, off_time, n, background)
            
    def _pulse_loop(self, fade_in_time, fade_out_time, n, background):
        remaining = n
        while remaining is None or remaining > 0:
            # Parlaklığı arttır
            for i in range(0, 101, 5):
                self.value = i / 100
                time.sleep(fade_in_time / 20)
            # Parlaklığı azalt
            for i in range(100, -1, -5):
                self.value = i / 100
                time.sleep(fade_out_time / 20)
            if remaining is not None:
                remaining -= 1
                
    def pulse(self, fade_in_time=1, fade_out_time=1, n=None, background=True):
        if self._pulse_thread is not None:
            self._pulse_thread = None
            
        if background:
            self._pulse_thread = threading.Thread(
                target=self._pulse_loop, args=(fade_in_time, fade_out_time, n, background), daemon=True)
            self._pulse_thread.start()
            print(f"[DummyGPIOZero] LED pin {self.pin} nefes efekti (arka planda)")
        else:
            print(f"[DummyGPIOZero] LED pin {self.pin} nefes efekti")
            self._pulse_loop(fade_in_time, fade_out_time, n, background)
            
class PWMLED(LED):
    def __init__(self, pin, frequency=100):
        super().__init__(pin)
        self.frequency = frequency
        print(f"[DummyGPIOZero] PWMLED pin {pin}, frekans {frequency}Hz")
        
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        self._value = max(0, min(1, value))  # 0 ile 1 arasında sınırla
        print(f"[DummyGPIOZero] PWMLED pin {self.pin} değeri: {self._value:.2f}")

class Buzzer(LED):
    def __init__(self, pin):
        super().__init__(pin)
        print(f"[DummyGPIOZero] Buzzer pin {pin} başlatıldı")
        
    def beep(self, on_time=1, off_time=1, n=None, background=True):
        # LED'in blink metodunu kullan
        super().blink(on_time, off_time, n, background)
        
class Device(LED):  # Temel Device sınıfı olarak LED'i kullan
    pass

class DigitalOutputDevice(LED):
    """Genel dijital çıkış cihazı simülasyonu"""
    def __init__(self, pin, active_high=True, initial_value=False):
        super().__init__(pin)
        self.active_high = active_high
        self.value = 0
        if initial_value:
            self.on()
        else:
            self.off()
        print(f"[DummyGPIOZero] DigitalOutputDevice pin {pin} başlatıldı, active_high={active_high}")
    
    def on(self):
        self.value = 1 if self.active_high else 0
        print(f"[DummyGPIOZero] DigitalOutputDevice pin {self.pin} açık")
    
    def off(self):
        self.value = 0 if self.active_high else 1
        print(f"[DummyGPIOZero] DigitalOutputDevice pin {self.pin} kapalı") 