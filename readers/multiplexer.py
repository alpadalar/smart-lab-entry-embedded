import time
import yaml
import os

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

MUX_ADDRESS = config['multiplexer_address']

if SIMULATION_MODE:
    # Simülasyon modu
    from utils.dummy_smbus import SMBus
    print("[MULTIPLEXER] Simülasyon modu kullanılıyor")
else:
    # Gerçek donanım modu
    from smbus2 import SMBus

def select_channel(channel: int):
    """I2C multiplexer kanalı seçme"""
    bus = SMBus(1)
    bus.write_byte(MUX_ADDRESS, 1 << channel)
    time.sleep(0.01) 