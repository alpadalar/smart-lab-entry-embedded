from RPLCD.i2c import CharLCD
from datetime import datetime
from readers.multiplexer import select_channel
import yaml
import time
import threading

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

days_tr = ['Pzt', 'Sal', 'Car', 'Per', 'Cum', 'Cmt', 'Paz']
custom_chars = {}  # boş, özel karakter gerekirse eklenebilir

lcd = None

def init_lcd():
    global lcd
    select_channel(config['lcd_channel'])
    lcd = CharLCD('PCF8574', config['lcd_address'], cols=20, rows=4)

def update_idle_screen():
    while True:
        now = datetime.now()
        select_channel(config['lcd_channel'])
        lcd.cursor_pos = (0, 0)
        lcd.write_string(f"[{days_tr[now.weekday()]} {now.strftime('%Y-%m-%d')}]".ljust(20))
        lcd.cursor_pos = (1, 0)
        lcd.write_string(now.strftime('%H:%M:%S').center(20))
        lcd.cursor_pos = (2, 0)
        lcd.write_string("AI LAB".center(20))
        lcd.cursor_pos = (3, 0)
        lcd.write_string("Kartinizi okutunuz".center(20))
        time.sleep(1)

def show_scan_result(direction, opened):
    select_channel(config['lcd_channel'])
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Kart okundu!".center(20))
    lcd.cursor_pos = (1, 0)
    lcd.write_string(direction.center(20))
    lcd.cursor_pos = (2, 0)
    lcd.write_string(("Kapi acildi" if opened else "Kapi acilmadi").center(20))
    time.sleep(2) 