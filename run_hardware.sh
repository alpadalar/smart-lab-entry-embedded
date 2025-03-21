#!/bin/bash

echo "===== SMART LAB ACCESS SYSTEM BAŞLIYOR ====="

# GPIOZero için pin factory seçimi
# Raspberry Pi 5 için lgpio kullan
# RPiGPIOFactory genellikle Raspberry Pi 4 ve öncesinde çalışır
# LGPIOFactory Raspberry Pi 5 ve diğerlerinde çalışabilir
# PiGPIOFactory ise performans gerektiren durumlarda kullanılabilir
export GPIOZERO_PIN_FACTORY=lgpio

# Gerçek donanım modu
export SIMULATION_MODE=false

# Debug modunu aktifleştir
export DEBUG_MODE=true

# I2C ve GPIO modüllerini kontrol et ve yükle
echo "I2C ve GPIO modüllerini kontrol ediyorum..."
if ! lsmod | grep -q "^i2c_dev "; then
    echo "I2C modülü aktif değil, aktifleştiriliyor..."
    sudo modprobe i2c-dev
fi

if ! lsmod | grep -q "^i2c_bcm2835 "; then
    echo "BCM2835 I2C modülü aktif değil, aktifleştiriliyor..."
    sudo modprobe i2c-bcm2835
fi

# PN532 NFC okuyucuları için gerekli izinleri ver
# GPIO pinlerinin erişim iznini ayarla
echo "GPIO izinleri ayarlanıyor..."
if [ -d "/sys/class/gpio" ]; then
    sudo chmod -R a+rw /sys/class/gpio
    echo "GPIO izinleri ayarlandı"
else
    echo "UYARI: /sys/class/gpio dizini bulunamadı, izinler ayarlanamadı"
fi

# UART izinleri ayarla (PN532 için)
if [ -e "/dev/ttyAMA0" ]; then
    sudo chmod a+rw /dev/ttyAMA0
    echo "UART izinleri ayarlandı"
fi

# Sanal ortamın mutlak yolunu belirt
VENV_PATH="$PWD/venv"

# Sanal ortamı aktif et (varsa)
if [ -d "$VENV_PATH" ]; then
    echo "Sanal ortam aktif ediliyor..."
    . "$VENV_PATH/bin/activate"
fi

# I2C aygıtlarını listele
echo "I2C aygıtları kontrol ediliyor..."
sudo i2cdetect -y 1

# Multiplexer adresini kontrol et (varsayılan: 0x70)
if ! i2cget -y 1 0x70 > /dev/null 2>&1; then
    echo "UYARI: I2C multiplexer (0x70) bulunamadı veya erişilemiyor!"
    echo "  - I2C bağlantılarını kontrol edin"
    echo "  - Multiplexer adresini config.yaml dosyasında doğrulayın"
    echo "  - 'sudo setup_pi5.sh' çalıştırarak kurulumu yeniden yapın"
    read -p "Devam etmek istiyor musunuz? (e/h) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ee]$ ]]; then
        echo "İşlem iptal edildi."
        exit 1
    fi
fi

# GPIO izinleri için kullanıcı grupları kontrolü
if ! groups | grep -q -e gpio -e i2c; then
    echo "UYARI: Kullanıcınız gpio/i2c gruplarına üye değil. Bazı erişim sorunları yaşanabilir."
    echo "Bu sorunu çözmek için setup_pi5.sh dosyasını çalıştırın."
fi

# Daha fazla detaylı loglama
if [ "$DEBUG_MODE" = "true" ]; then
    echo "Debug modu aktif, detaylı loglama yapılacak"
    export PYTHONVERBOSE=1
fi

echo "GPIO Pin Factory: $GPIOZERO_PIN_FACTORY"
echo "Simulation Mode: $SIMULATION_MODE"

# Root yetkisiyle çalıştır
echo "Program root yetkisiyle başlatılıyor..."
sudo \
    PYTHONPATH="$PWD" \
    GPIOZERO_PIN_FACTORY="$GPIOZERO_PIN_FACTORY" \
    PYTHONDONTWRITEBYTECODE=1 \
    SIMULATION_MODE="$SIMULATION_MODE" \
    DEBUG_MODE="$DEBUG_MODE" \
    PYTHONIOENCODING=utf-8 \
    python3 main.py

echo "===== SMART LAB ACCESS SYSTEM DURDU =====" 