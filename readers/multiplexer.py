import smbus2
import time
import yaml

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

MUX_ADDRESS = config['multiplexer_address']

def select_channel(channel: int):
    bus = smbus2.SMBus(1)
    bus.write_byte(MUX_ADDRESS, 1 << channel)
    time.sleep(0.01) 