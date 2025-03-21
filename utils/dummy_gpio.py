"""
GPIO simülasyon modülü - gerçek GPIO olmayan ortamlarda kullanmak için
"""

import time
import threading

# GPIO modları
BCM = "BCM"
BOARD = "BOARD"
OUT = "OUT"
IN = "IN"
HIGH = 1
LOW = 0

_current_mode = None
_pin_states = {}
_warnings = True

def setmode(mode):
    global _current_mode
    _current_mode = mode
    print(f"[DummyGPIO] GPIO modu {mode} olarak ayarlandı")

def setwarnings(state):
    global _warnings
    _warnings = state
    if not state:
        print("[DummyGPIO] GPIO uyarıları kapatıldı")

def setup(pin, direction, initial=LOW, pull_up_down=None):
    global _pin_states
    _pin_states[pin] = initial
    print(f"[DummyGPIO] Pin {pin} {direction} olarak ayarlandı, başlangıç: {initial}")

def output(pin, state):
    global _pin_states
    if pin in _pin_states:
        _pin_states[pin] = state
        print(f"[DummyGPIO] Pin {pin} {state} değerine ayarlandı")
    else:
        print(f"[DummyGPIO] HATA: Pin {pin} henüz kurulmamış")

def input(pin):
    global _pin_states
    if pin in _pin_states:
        return _pin_states[pin]
    else:
        print(f"[DummyGPIO] HATA: Pin {pin} henüz kurulmamış")
        return LOW

def cleanup(pins=None):
    global _pin_states
    if pins is None:
        _pin_states = {}
        print("[DummyGPIO] Tüm GPIO pinleri temizlendi")
    else:
        if isinstance(pins, list):
            for pin in pins:
                if pin in _pin_states:
                    del _pin_states[pin]
            print(f"[DummyGPIO] Pinler {pins} temizlendi")
        else:
            if pins in _pin_states:
                del _pin_states[pins]
            print(f"[DummyGPIO] Pin {pins} temizlendi")

class PWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = 0
        self.running = False
        print(f"[DummyGPIO] PWM: Pin {pin}, Frekans {frequency}Hz")
    
    def start(self, duty_cycle):
        self.duty_cycle = duty_cycle
        self.running = True
        print(f"[DummyGPIO] PWM: Pin {self.pin} başlatıldı, duty cycle: %{duty_cycle}")
    
    def ChangeDutyCycle(self, duty_cycle):
        self.duty_cycle = duty_cycle
        if self.running:
            print(f"[DummyGPIO] PWM: Pin {self.pin} duty cycle %{duty_cycle} olarak değiştirildi")
    
    def ChangeFrequency(self, frequency):
        self.frequency = frequency
        if self.running:
            print(f"[DummyGPIO] PWM: Pin {self.pin} frekansı {frequency}Hz olarak değiştirildi")
    
    def stop(self):
        self.running = False
        print(f"[DummyGPIO] PWM: Pin {self.pin} durduruldu") 