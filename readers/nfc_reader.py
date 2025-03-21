import threading
import time
from readers.multiplexer import select_channel
from adafruit_pn532.i2c import PN532_I2C
import board
import busio
from utils.api_client import send_card
from utils.logger import log
from controllers.relay_controller import trigger_relay
from controllers.led_controller import show_color
from controllers.buzzer_controller import beep
from controllers.lcd_controller import show_scan_result

import yaml
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

i2c = busio.I2C(board.SCL, board.SDA)

def handle_reader(role, channel, is_inside, lcd_enabled=False):
    select_channel(channel)
    reader = PN532_I2C(i2c, debug=False)
    from controllers.led_controller import start_breathing
    start_breathing(role)

    while True:
        select_channel(channel)
        uid = reader.read_passive_target(timeout=0.1)
        if uid:
            uid_hex = uid.hex()
            log.info(f"{role.upper()} - UID: {uid_hex}")
            status, response = send_card(uid_hex, is_inside)
            opened = False
            if status == 200 and response:
                if response.get("openDoor"):
                    trigger_relay()
                    show_color(role, (0, 255, 0))
                    beep(role, [0.1, 0.1])
                    opened = True
                else:
                    show_color(role, (0, 0, 255))
                    beep(role, [0.1])
            else:
                show_color(role, (255, 0, 0))
                beep(role, [1.0])

            if lcd_enabled:
                direction = "Disari ciktiniz" if not is_inside else "Iceri girdiniz"
                show_scan_result(direction, opened)
            time.sleep(1) 