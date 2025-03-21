#!/bin/bash

# GPIOZero için pin factory seçimi
# Raspberry Pi 5 için lgpio kullan
# RPiGPIOFactory genellikle Raspberry Pi 4 ve öncesinde çalışır
# LGPIOFactory Raspberry Pi 5 ve diğerlerinde çalışabilir
# PiGPIOFactory ise performans gerektiren durumlarda kullanılabilir
export GPIOZERO_PIN_FACTORY=lgpio

# Gerçek donanım modu
export SIMULATION_MODE=false

# Sanal ortamın mutlak yolunu belirt
VENV_PATH="$PWD/venv"

# Sanal ortamı aktif et (varsa)
if [ -d "$VENV_PATH" ]; then
    echo "Sanal ortam aktif ediliyor..."
    . "$VENV_PATH/bin/activate"
fi

# I2C modülü kontrolü ve yükleme
if ! lsmod | grep -q "^i2c_dev "; then
    echo "I2C modülü aktif değil, aktifleştiriliyor..."
    sudo modprobe i2c-dev
fi

# I2C aygıtlarını listele
echo "I2C aygıtları kontrol ediliyor..."
sudo i2cdetect -y 1

# GPIO izinleri için kullanıcı grupları kontrolü
if ! groups | grep -q -e gpio -e i2c; then
    echo "UYARI: Kullanıcınız gpio/i2c gruplarına üye değil. Bazı erişim sorunları yaşanabilir."
    echo "Bu sorunu çözmek için setup_pi5.sh dosyasını çalıştırın."
fi

# Root yetkisiyle çalıştır
echo "Program root yetkisiyle başlatılıyor..."
sudo \
    PYTHONPATH="$PWD" \
    GPIOZERO_PIN_FACTORY=lgpio \
    PYTHONDONTWRITEBYTECODE=1 \
    SIMULATION_MODE=false \
    python3 main.py 