# I2C Multiplexer (PCA9548A) ayarları
MULTIPLEXER_ADDR = 0x70
I2C_BUS = 1

# NFC Okuyucu (PN532) ayarları
NFC_ADDR = 0x24
INSIDE_NFC_CHANNEL = 0
OUTSIDE_NFC_CHANNEL = 1

# LCD Ekran ayarları
LCD_CHANNEL = 2
LCD_WIDTH = 20
LCD_HEIGHT = 4
LCD_ADDR = 0x27

# LED Şerit ayarları
LED_COUNT = 30
INSIDE_LED_PIN = 18  # GPIO18
OUTSIDE_LED_PIN = 12  # GPIO12

# Buzzer ayarları
INSIDE_BUZZER_PIN = 23  # GPIO23
OUTSIDE_BUZZER_PIN = 24  # GPIO24

# Relay ayarları
RELAY_DURATION = 3  # saniye

# API ayarları
API_URL = "http://localhost:8000/api/access"
CONTROLLER_ID = "RASPI_001"

# Log ayarları
LOG_FILE = "access_log"

# Renk tanımlamaları
COLORS = {
    "OFF": (0, 0, 0),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "WHITE": (255, 255, 255),
    "YELLOW": (255, 255, 0),
    "PURPLE": (255, 0, 255),
    "CYAN": (0, 255, 255)
}

# LED süreleri (saniye)
LED_DURATIONS = {
    "SUCCESS": 1.0,
    "FAIL": 0.5,
    "ERROR": 0.3
}

# Buzzer süreleri (saniye)
BUZZER_DURATIONS = {
    "SUCCESS": 0.5,
    "FAIL": 0.2,
    "ERROR": 0.1
} 