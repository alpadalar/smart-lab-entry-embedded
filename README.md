# Smart Lab Entry System

Raspberry Pi 5 tabanlı akıllı laboratuvar giriş sistemi. NFC kart okuyucular, LED şeritler, LCD ekran ve USB röle kullanarak güvenli giriş kontrolü sağlar.

## Donanım Gereksinimleri

- Raspberry Pi 5
- 2x PN532 NFC Okuyucu
- 1x PCA9548A I2C Multiplexer
- 1x 20x4 I2C LCD Ekran
- 2x WS2812B LED Şerit (30 LED)
- 2x Pasif Buzzer
- 1x USB Röle Kartı
- 1x 5V Güç Kaynağı
- Jumper Kablolar
- Breadboard (opsiyonel)

## Donanım Bağlantıları

### I2C Multiplexer (PCA9548A) Bağlantıları
- VCC -> 3.3V
- GND -> GND
- SDA -> GPIO2 (Pin 3)
- SCL -> GPIO3 (Pin 5)
- A0, A1, A2 -> GND (Adres: 0x70)

### İç NFC Okuyucu (PN532) Bağlantıları
- VCC -> 3.3V
- GND -> GND
- SDA -> I2C Multiplexer Kanal 0
- SCL -> I2C Multiplexer Kanal 0
- IRQ -> GPIO17 (Pin 11)
- RST -> GPIO27 (Pin 13)

### Dış NFC Okuyucu (PN532) Bağlantıları
- VCC -> 3.3V
- GND -> GND
- SDA -> I2C Multiplexer Kanal 1
- SCL -> I2C Multiplexer Kanal 1
- IRQ -> GPIO22 (Pin 15)
- RST -> GPIO23 (Pin 16)

### LCD Ekran (20x4 I2C) Bağlantıları
- VCC -> 5V
- GND -> GND
- SDA -> I2C Multiplexer Kanal 2
- SCL -> I2C Multiplexer Kanal 2
- Adres: 0x27 (varsayılan)

### İç LED Şerit Bağlantıları
- VCC -> 5V
- GND -> GND
- DIN -> GPIO18 (Pin 12)

### Dış LED Şerit Bağlantıları
- VCC -> 5V
- GND -> GND
- DIN -> GPIO12 (Pin 32)

### İç Buzzer Bağlantıları
- VCC -> GPIO23 (Pin 16)
- GND -> GND

### Dış Buzzer Bağlantıları
- VCC -> GPIO24 (Pin 18)
- GND -> GND

### USB Röle Kartı
- USB port üzerinden bağlanır
- Röle 1 kullanılır

## Kurulum

1. Gerekli sistem paketlerini yükleyin:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git build-essential python3-dev
```

2. I2C'yi etkinleştirin:
```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
```

3. Projeyi klonlayın:
```bash
git clone https://github.com/yourusername/smart-lab-entry-embedded.git
cd smart-lab-entry-embedded
```

4. Sanal ortam oluşturun ve aktifleştirin:
```bash
python3 -m venv venv
source venv/bin/activate
```

5. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

6. usbrelay kurulumu:
```bash
# Gerekli build araçlarını yükle
sudo apt install python3-dev build-essential python3-wheel

# usbrelay kaynak kodunu indir ve derle
git clone https://github.com/darrylb123/usbrelay.git
cd usbrelay
make
sudo make install

# Python modülünü wheel olarak derle ve kur
cd usbrelay_py
python setup.py bdist_wheel
pip install -e .
cd ../..
```

## Kullanım

### Simülasyon Modunda Çalıştırma

Donanım bağlantısı olmadan, bilgisayar üzerinde test amaçlı çalıştırmak için:

```bash
bash run.sh
```

veya

```bash
export SIMULATION_MODE=true
python main.py
```

### Gerçek Donanım Modunda Çalıştırma

Raspberry Pi 5 üzerinde gerçek donanımla:

```bash
bash run_hardware.sh
```

veya

```bash
sudo GPIOZERO_PIN_FACTORY=lgpio SIMULATION_MODE=false python main.py
```

## Özellikler

- İç ve dış NFC kart okuma
- LED şerit ile görsel geri bildirim
- Buzzer ile sesli geri bildirim
- LCD ekranda durum gösterimi
- USB röle ile kapı kontrolü
- Detaylı loglama
- Hata yönetimi ve kurtarma

## Güvenlik

- NFC kartlar şifrelidir
- API ile merkezi erişim kontrolü
- Hata durumunda güvenli kapanma
- Detaylı loglama

## Hata Ayıklama

1. I2C cihazlarını kontrol edin:
```bash
i2cdetect -y 1
```

2. GPIO pinlerini kontrol edin:
```bash
gpio readall
```

3. USB röle durumunu kontrol edin:
```bash
lsusb
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Raspberry Pi 5 Uyumluluğu ve Sorun Giderme

Raspberry Pi 5, farklı GPIO kontrolör mimarisi nedeniyle önceki Raspberry Pi modellerinden bazı farklılıklar gösterir. Aşağıdaki bilgiler, Raspberry Pi 5 ile çalışırken karşılaşabileceğiniz sorunları çömenize yardımcı olacaktır.

### Pin Factory Seçimi

Raspberry Pi 5 ile çalışırken, uygun pin factory seçimi önemlidir:

1. **lgpio (Önerilen)**: Raspberry Pi 5 için özel olarak tasarlanmış, yerel GPIO kütüphanesi.
   ```bash
   export GPIOZERO_PIN_FACTORY=lgpio
   ```

2. **pigpio**: Tüm Raspberry Pi modellerinde çalışan, düşük gecikme süreli bir GPIO kütüphanesi.
   ```bash
   export GPIOZERO_PIN_FACTORY=pigpio
   sudo pigpiod  # pigpio daemon'u başlat
   ```

3. **rpigpio**: Eski Raspberry Pi modelleri için, Raspberry Pi 5 üzerinde tam uyumlu değil.
   ```bash
   export GPIOZERO_PIN_FACTORY=rpigpio  # Raspberry Pi 5'te bazı sorunlar yaratabilir
   ```

4. **native**: GPIOZero'nun otomatik olarak en uygun pin factory'i seçmesini sağlar.
   ```bash
   export GPIOZERO_PIN_FACTORY=native
   ```

### I2C Sorunları ve Çözümleri

Raspberry Pi 5 üzerinde I2C iletişim sorunları yaşıyorsanız:

1. **I2C Baudrate Hızını Düşürme**: Clock stretching sorunlarını çözmek için I2C hızını düşürün.
   ```bash
   # /boot/config.txt dosyasına ekle veya düzenle
   dtparam=i2c_arm=on,i2c_arm_baudrate=50000
   ```

2. **NFC Okuyucu Bağlantı Sorunları**: PN532 okuyucular için bağlantıyı doğrulayın.
   ```bash
   i2cdetect -y 1  # I2C cihazlarını listele
   sudo i2cdump -y 1 0x24  # PN532 için
   ```

3. **Alternatif I2C Yazılım Veri Yolu**: Donanım I2C ile sorun yaşıyorsanız, yazılım tabanlı I2C kullanın.
   ```bash
   # /boot/config.txt dosyasına ekle
   dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=17,i2c_gpio_scl=27
   ```

### GPIO Erişim İzinleri

Raspberry Pi 5 üzerinde GPIO erişim sorunları:

1. **Kullanıcı İzinleri**: Kullanıcınızın gerekli gruplara üye olduğundan emin olun.
   ```bash
   sudo usermod -a -G gpio,i2c,spi,dialout $USER
   # Değişikliklerin geçerli olması için oturumu kapatıp açın
   ```

2. **GPIO Erişim Haklarını Ayarlama**: Doğrudan GPIO dosya sistemine erişim için.
   ```bash
   sudo chmod -R a+rw /sys/class/gpio/
   sudo chmod a+rw /dev/gpiomem
   ```

3. **Root ile Çalıştırma**: Son çare olarak, programı root olarak çalıştırın.
   ```bash
   sudo ./run_hardware.sh
   ```

### "Cannot determine SOC peripheral base address" Hatası

Bu hata, genellikle Raspberry Pi 5 üzerinde RPi.GPIO kütüphanesi kullanıldığında görülür:

1. **lgpio Kullanma**: rpigpio yerine lgpio pin factory'i kullanın.
   ```bash
   export GPIOZERO_PIN_FACTORY=lgpio
   ```

2. **Sistemin Güncellenmesi**: İşletim sistemini güncelleyin.
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Kernel Başlangıç Parametreleri**: `/boot/cmdline.txt` dosyasına `iomem=relaxed` ekleyin.
   ```
   console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 iomem=relaxed ...
   ```

### NFC Okuyucu Optimizasyonu

PN532 NFC okuyucularla daha iyi performans için:

1. **Güvenilir I2C İletişimi**: Düşük baudrate ile I2C sorunlarını azaltın.
   ```bash
   # /boot/config.txt dosyasına ekle veya düzenle
   dtparam=i2c_arm=on,i2c_arm_baudrate=50000
   ```

2. **RF Seviyesi Ayarı**: Okuma mesafesini artırmak için kod içerisindeki RF seviyesi ayarını aktifleştirin.

3. **NFC Testi**: Standart NFC araçları ile okuyucuyu test edin.
   ```bash
   sudo apt install -y libnfc-bin libnfc-dev
   sudo nfc-list
   sudo nfc-poll
   ```

### Otomatik Kurulum

Raspberry Pi 5 ile çalışmak üzere en uygun yapılandırma için otomatik kurulum betiğini kullanın:

```bash
chmod +x setup_pi5.sh
./setup_pi5.sh
sudo reboot
```

Bu betik gerekli tüm ayarları yaparak Raspberry Pi 5'in GPIOZero, I2C ve NFC cihazları ile en iyi şekilde çalışmasını sağlar.

## Debug Loglama

Debug loglarını etkinleştirmek için:

```bash
# config/config.yaml dosyasında
logging:
  level: "DEBUG"  # INFO, WARNING, ERROR, DEBUG, CRITICAL
  file: "logs/lab_entry.log"
  console: true
```

Bu ayar ile bütün cihazların başlangıç ve çalışma zamanı loglarına erişebilirsiniz. 