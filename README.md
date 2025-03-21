# Akıllı Laboratuvar Giriş Sistemi

Bu proje, Raspberry Pi 5 üzerinde çalışan bir laboratuvar giriş kontrol sistemidir. Sistem, NFC kartları kullanarak giriş-çıkış kontrolü yapar ve tüm olayları loglar.

## Özellikler

- İki adet PN532 NFC okuyucu (iç ve dış)
- PCA9548A I²C multiplexer ile donanım yönetimi
- 20x4 I²C LCD ekran
- İki adet WS2812B LED şerit (8'er LED)
- İki adet pasif buzzer
- USB röle kartı ile kapı kontrolü
- API entegrasyonu
- Detaylı loglama sistemi

## Gereksinimler

- Python 3.7+
- Raspberry Pi 5
- Gerekli donanımlar (NFC okuyucular, LCD, LED şeritler, vb.)
- Gerekli Python paketleri (requirements.txt içinde listelenmiştir)

## Kurulum

1. Gerekli sistem paketlerini yükleyin:
```bash
sudo apt update
sudo apt install python3-venv python3-full python3-dev build-essential python3-wheel
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. usbrelay paketini kurun:
```bash
# usbrelay kaynak kodunu indir
git clone https://github.com/darrylb123/usbrelay.git
cd usbrelay

# usbrelay'i derle ve kur
make
sudo make install

# Python modülünü wheel olarak derle ve kur
cd usbrelay_py
python setup.py bdist_wheel
pip install -e .
cd ../..
```

4. Diğer Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

5. Donanımları bağlayın:
   - İç NFC okuyucu -> Multiplexer Kanal 0
   - Dış NFC okuyucu -> Multiplexer Kanal 1
   - LCD Ekran -> Multiplexer Kanal 2
   - LED şeritler -> GPIO18 (iç) ve GPIO23 (dış)
   - Buzzerlar -> GPIO17 (iç) ve GPIO27 (dış)
   - USB röle kartı -> USB port

6. `config.py` dosyasını düzenleyin:
   - API URL'sini güncelleyin
   - Gerekirse pin numaralarını değiştirin
   - Diğer yapılandırma ayarlarını yapın

## Kullanım

1. Sanal ortamı aktifleştirin:
```bash
source venv/bin/activate
```

2. Programı başlatın:
```bash
python src/main.py
```

3. Program çalıştığında:
   - LED şeritler beyaz nefes alma efekti ile yanar
   - LCD ekranda karşılama mesajı görüntülenir
   - NFC okuyucular kart beklemeye başlar
   - Tüm olaylar `access_log.txt` dosyasına kaydedilir

4. Programı sonlandırmak için:
```bash
deactivate
```

## LED Efektleri

- Bekleme: Beyaz nefes alma efekti
- Başarılı geçiş: Yeşil (2 saniye)
- Başarısız geçiş: Mavi (2 saniye)
- Hata: Kırmızı (2 saniye)

## Buzzer Tepkileri

- Başarılı geçiş: İki kısa bip
- Başarısız geçiş: Bir kısa bip
- Hata: Bir uzun bip

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 