#!/bin/bash

echo "Raspberry Pi 5 için GPIO ve I2C konfigürasyonu yapılıyor..."

# Yükleme başlangıç zamanı
START_TIME=$(date +%s)

# Sistem güncellemesi
echo "Sistem paketleri güncelleniyor..."
sudo apt update && sudo apt upgrade -y

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
sudo apt install -y python3-gpiozero python3-lgpio python3-rpi.gpio python3-pigpio pigpio

# Eğer pigpio daemon kuruluysa başlat
if command -v pigpiod &> /dev/null; then
    echo "pigpio daemon'u başlatıyorum..."
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod
fi

# I2C araçlarını kur
echo "I2C araçlarını kuruyorum..."
sudo apt install -y i2c-tools python-is-python3 libi2c-dev

# Python bağlayıcılarını yükle
echo "Python paketlerini kuruyorum..."
pip install lgpio gpiozero pigpio adafruit-blinka adafruit-circuitpython-busdevice adafruit-circuitpython-pn532 smbus2

# Kullanıcıyı gerekli gruplara ekle (GPIO ve I2C erişimi için)
echo "Kullanıcıyı gerekli gruplara ekliyorum..."
sudo usermod -a -G gpio,i2c,spi,dialout $USER

# udev kuralları ayarla (GPIO erişimi için)
if [ ! -f "/etc/udev/rules.d/99-gpio.rules" ]; then
    echo "GPIO için udev kuralları oluşturuyorum..."
    sudo bash -c 'cat > /etc/udev/rules.d/99-gpio.rules << EOF
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c '\''chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'\''
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c '\''chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'\''
EOF'
fi

# PN532 NFC okuyucular için I2C ayarları
echo "PN532 NFC okuyucular için I2C ayarlarını yapıyorum..."

# I2C baudrate'i (hızını) düşür
if [ ! -f "/boot/config.txt.bak" ]; then
    sudo cp /boot/config.txt /boot/config.txt.bak
fi

# Zaten dtparam=i2c_arm=on,i2c_arm_baudrate=XXX eklenmişse güncelle, yoksa ekle
if grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
    # Var olan i2c_arm ayarını güncelle, baudrate ekle
    sudo sed -i 's/dtparam=i2c_arm=on.*/dtparam=i2c_arm=on,i2c_arm_baudrate=50000/' /boot/config.txt
    echo "I2C baudrate 50000 olarak güncellendi"
else
    # Yeni ayar ekle
    echo "dtparam=i2c_arm=on,i2c_arm_baudrate=50000" | sudo tee -a /boot/config.txt
    echo "I2C baudrate 50000 olarak eklendi"
fi

# PN532 için UART ve üçüncü I2C veri yolu etkinleştirme
if ! grep -q "dtoverlay=i2c-gpio,bus=3" /boot/config.txt; then
    echo "Üçüncü I2C veri yolu (yazılım tabanlı) etkinleştiriliyor..."
    echo "dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=17,i2c_gpio_scl=27" | sudo tee -a /boot/config.txt
fi

# NFC okuyucular için erişim izinlerini ayarla
echo "NFC okuyucular için erişim izinlerini ayarlıyorum..."
if [ ! -f "/etc/udev/rules.d/90-nfc.rules" ]; then
    sudo bash -c 'cat > /etc/udev/rules.d/90-nfc.rules << EOF
# PN532 NFC Controller için udev kuralları
SUBSYSTEM=="usb", ATTRS{idVendor}=="04e6", ATTRS{idProduct}=="5591", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04cc", ATTRS{idProduct}=="2533", MODE="0666"
# I2C-GPIO için erişim izni
KERNEL=="i2c-[0-9]*", GROUP="i2c", MODE="0666"
EOF'
    echo "NFC udev kuralları oluşturuldu"
fi

# USB röle kartı için erişim izinleri
echo "USB röle kartı için erişim izinlerini ayarlıyorum..."
if [ ! -f "/etc/udev/rules.d/50-usbrelay.rules" ]; then
    sudo bash -c 'cat > /etc/udev/rules.d/50-usbrelay.rules << EOF
# HID USB Relay için udev kuralları
SUBSYSTEM=="usb", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="05df", MODE="0666"
EOF'
    echo "USB röle udev kuralları oluşturuldu"
fi

# I2C hata ayıklama araçları
echo "I2C hata ayıklama araçlarını kuruyorum..."
sudo apt install -y i2c-tools python3-smbus python3-dev

# Git deposundan usbrelay kur (en son sürüm)
echo "USB röle kütüphanesini kuruyorum..."
if [ ! -d "usbrelay" ]; then
    git clone https://github.com/darrylb123/usbrelay.git
    cd usbrelay
    make
    sudo make install
    cd ..
fi

# usbrelay Python modülünü kur
if [ -d "usbrelay/usbrelay_py" ]; then
    cd usbrelay/usbrelay_py
    pip install -e .
    cd ../..
    echo "usbrelay_py Python modülü kuruldu"
fi

# PN532 NFC okuyucuyu test etmek için araç
echo "PN532 test aracını kuruyorum..."
sudo apt install -y libnfc-bin libnfc-dev libnfc-examples

# libnfc konfigürasyonu
if [ ! -d "/etc/nfc" ]; then
    sudo mkdir -p /etc/nfc
fi

if [ ! -f "/etc/nfc/libnfc.conf" ]; then
    sudo bash -c 'cat > /etc/nfc/libnfc.conf << EOF
# PN532 over I2C ayarları
device.name = "PN532 over I2C"
device.connstring = "pn532_i2c:/dev/i2c-1"
EOF'
    echo "libnfc yapılandırması oluşturuldu"
fi

# I2C clock stretching sorunu için dtparam=i2c_arm_baudrate azalt
if grep -q "dtparam=i2c_arm_baudrate" /boot/config.txt; then
    # Var olan baudrate ayarını güncelle
    sudo sed -i 's/dtparam=i2c_arm_baudrate=.*/dtparam=i2c_arm_baudrate=50000/' /boot/config.txt
    echo "I2C clock stretching için baudrate düşürüldü"
fi

# GPIO satır durumunu düzelt
if [ ! -f "/etc/modprobe.d/gpio.conf" ]; then
    sudo bash -c 'echo "options gpio_grp_gpio grp_gpio_bpwm=0" > /etc/modprobe.d/gpio.conf'
    echo "GPIO modül parametreleri yapılandırıldı"
fi

# GPIO izinlerini system.d servisi ile ayarla
if [ ! -f "/etc/systemd/system/gpio-permissions.service" ]; then
    sudo bash -c 'cat > /etc/systemd/system/gpio-permissions.service << EOF
[Unit]
Description=GPIO Permissions
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c "chmod -R a+rw /sys/class/gpio || true"
ExecStart=/bin/bash -c "chmod -R a+rw /dev/gpiomem || true"
ExecStart=/bin/bash -c "chmod -R a+rw /dev/i2c* || true"
ExecStart=/bin/bash -c "chmod -R a+rw /dev/spi* || true"

[Install]
WantedBy=multi-user.target
EOF'
    sudo systemctl enable gpio-permissions.service
    echo "GPIO izinleri servisi oluşturuldu ve etkinleştirildi"
fi

# Yapılandırma süresi
END_TIME=$(date +%s)
SETUP_TIME=$((END_TIME - START_TIME))
echo ""
echo "Yapılandırma tamamlandı. Süre: $SETUP_TIME saniye"
echo "Lütfen sistemi yeniden başlatın."
echo "Yeniden başlatmak için: sudo reboot"
echo ""
echo "Kullanabileceğiniz pin factory'ler:"
echo "- LGPIOFactory: Raspberry Pi 5 için (export GPIOZERO_PIN_FACTORY=lgpio)"
echo "- RPiGPIOFactory: Raspberry Pi 4 ve öncesi için (export GPIOZERO_PIN_FACTORY=rpigpio)"
echo "- PiGPIOFactory: Düşük gecikme süresi için (export GPIOZERO_PIN_FACTORY=pigpio)"
echo "- NativeFactory: Otomatik pin factory seçimi (export GPIOZERO_PIN_FACTORY=native)"
echo ""
echo "NFC okuyucunun doğru çalışması için düşük I2C hızı (50kHz) ayarlandı"
echo "Kurulum sonrası I2C test etmek için: sudo i2cdetect -y 1" 