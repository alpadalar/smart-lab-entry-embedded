#!/bin/bash

echo "Raspberry Pi 5 için GPIO ve I2C konfigürasyonu yapılıyor..."

# I2C modüllerini etkinleştir ve sistemi başlangıçta otomatik yükle
if ! grep -q "i2c-dev" /etc/modules; then
    echo "I2C modüllerini /etc/modules'e ekliyorum..."
    sudo bash -c 'echo "i2c-dev" >> /etc/modules'
    sudo bash -c 'echo "i2c-bcm2835" >> /etc/modules'
fi

# I2C, SPI ve GPIO'yu raspi-config ile etkinleştir
echo "I2C, SPI ve GPIO'yu etkinleştirme..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial 2  # UART erişimi (konsol olmadan)

# GPIO Zero için gereken kütüphaneleri kur
echo "GPIO Zero için gereken kütüphaneleri kuruyorum..."
sudo apt update
sudo apt install -y python3-gpiozero python3-lgpio python3-rpi.gpio python3-pigpio pigpio

# Eğer pigpio daemon kuruluysa başlat
if command -v pigpiod &> /dev/null; then
    echo "pigpio daemon'u başlatıyorum..."
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod
fi

# I2C araçlarını kur
echo "I2C araçlarını kuruyorum..."
sudo apt install -y i2c-tools python-is-python3

# Python bağlayıcılarını yükle
echo "Python paketlerini kuruyorum..."
pip install lgpio gpiozero pigpio adafruit-blinka adafruit-circuitpython-busdevice

# Kullanıcıyı gerekli gruplara ekle (GPIO ve I2C erişimi için)
echo "Kullanıcıyı gerekli gruplara ekliyorum..."
sudo usermod -a -G gpio,i2c,spi $USER

# udev kuralları ayarla (GPIO erişimi için)
if [ ! -f "/etc/udev/rules.d/99-gpio.rules" ]; then
    echo "GPIO için udev kuralları oluşturuyorum..."
    sudo bash -c 'cat > /etc/udev/rules.d/99-gpio.rules << EOF
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c '\''chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'\''
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c '\''chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'\''
EOF'
fi

echo "Yapılandırma tamamlandı. Lütfen sistemi yeniden başlatın."
echo "Yeniden başlatmak için: sudo reboot"
echo ""
echo "Kullanabileceğiniz pin factory'ler:"
echo "- LGPIOFactory: Raspberry Pi 5 için (export GPIOZERO_PIN_FACTORY=lgpio)"
echo "- RPiGPIOFactory: Raspberry Pi 4 ve öncesi için (export GPIOZERO_PIN_FACTORY=rpigpio)"
echo "- PiGPIOFactory: Düşük gecikme süresi için (export GPIOZERO_PIN_FACTORY=pigpio)"
echo "- NativeFactory: Otomatik pin factory seçimi (export GPIOZERO_PIN_FACTORY=native)" 