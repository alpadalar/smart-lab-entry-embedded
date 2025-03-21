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
- I2C Kanal: 3

### Dış LED Şerit Bağlantıları
- VCC -> 5V
- GND -> GND
- DIN -> GPIO12 (Pin 32)
- I2C Kanal: 4

### İç Buzzer Bağlantıları
- VCC -> GPIO23 (Pin 16)
- GND -> GND
- I2C Kanal: 5

### Dış Buzzer Bağlantıları
- VCC -> GPIO24 (Pin 18)
- GND -> GND
- I2C Kanal: 6

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

1. Sanal ortamı aktifleştirin:
```bash
source venv/bin/activate
```

2. Programı çalıştırın:
```bash
python -m src.main
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