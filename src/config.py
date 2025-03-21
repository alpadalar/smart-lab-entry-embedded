# I2C ve Multiplexer Ayarları
MULTIPLEXER_ADDR = 0x70
I2C_BUS = 1

# NFC Okuyucu Kanalları
INSIDE_NFC_CHANNEL = 0
OUTSIDE_NFC_CHANNEL = 1
LCD_CHANNEL = 2

# LCD Ekran Ayarları
LCD_WIDTH = 20
LCD_HEIGHT = 4
LCD_ADDR = 0x27  # Varsayılan I2C adresi

# LED Şerit Ayarları
LED_COUNT = 8
INSIDE_LED_PIN = 18  # GPIO18
OUTSIDE_LED_PIN = 23  # GPIO23

# Buzzer Pinleri
INSIDE_BUZZER_PIN = 17  # GPIO17
OUTSIDE_BUZZER_PIN = 27  # GPIO27

# API Ayarları
API_URL = "http://localhost:8080/api/access-portals/door-status"
CONTROLLER_ID = "585285"

# Log Dosyası
LOG_FILE = "access_log.txt"

# LED Renkleri
COLORS = {
    "WHITE": (255, 255, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "RED": (255, 0, 0),
    "OFF": (0, 0, 0)
}

# Buzzer Süreleri (saniye)
BUZZER_DURATIONS = {
    "SUCCESS": 0.1,
    "FAIL": 0.1,
    "ERROR": 0.5
}

# LED Efekt Süreleri (saniye)
LED_DURATIONS = {
    "SUCCESS": 2,
    "FAIL": 2,
    "ERROR": 2
} 