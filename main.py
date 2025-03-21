import threading
from readers.nfc_reader import handle_reader
from controllers.lcd_controller import init_lcd, update_idle_screen
import yaml

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# LCD başlat
init_lcd()

# NFC okuyucu thread'leri başlat
threading.Thread(target=handle_reader, args=("inside", config['nfc_channels']['inside'], True), daemon=True).start()
threading.Thread(target=handle_reader, args=("outside", config['nfc_channels']['outside'], False, True), daemon=True).start()

# LCD ekranı sürekli güncelle
threading.Thread(target=update_idle_screen, daemon=True).start()

# Sonsuz döngü
try:
    while True:
        threading.Event().wait(1)
except KeyboardInterrupt:
    print("Program sonlandirildi.") 