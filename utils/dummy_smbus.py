"""
Simülasyon modunda I2C SMBus işlevselliğini taklit etmek için kullanılan dummy modül.
"""

import random


class SMBus:
    """
    Simülasyon için SMBus sınıfı. Gerçek I2C cihazları olmadan geliştirmeyi kolaylaştırır.
    """

    def __init__(self, bus_number):
        """
        I2C veri yolunu başlat.
        
        Args:
            bus_number: I2C veri yolu numarası (genellikle 1)
        """
        self.bus_number = bus_number
        self.is_open = True
        
        # Simüle edilmiş cihazlar
        self.devices = {
            0x24: {  # PN532 NFC okuyucu
                "name": "PN532 NFC Reader",
                "firmware_version": [0x32, 0x01, 0x06, 0x07],
                "registers": {
                    0x00: 0x32,  # Cihaz kimliği
                    0x01: 0x01,  # Firmware sürümü - ana sürüm
                    0x02: 0x06,  # Firmware sürümü - alt sürüm
                    0x03: 0x07,  # Destek baytı
                    0x04: random.randint(0, 255),  # Rastgele veri
                }
            },
            0x70: {  # I2C çoklayıcı
                "name": "TCA9548A I2C Multiplexer",
                "registers": {
                    0x00: 0x01  # Varsayılan olarak kanal 0 seçili
                }
            },
            0x27: {  # LCD ekran
                "name": "LCD Display Controller",
                "registers": {
                    0x00: 0x00,  # LCD komut kaydı
                    0x01: 0x00   # LCD veri kaydı
                }
            }
        }
        
        print(f"Dummy SMBus {bus_number} başlatıldı (Simülasyon)")

    def close(self):
        """
        I2C veri yolunu kapat.
        """
        self.is_open = False
        print(f"Dummy SMBus {self.bus_number} kapatıldı")

    def read_byte(self, addr):
        """
        Belirtilen adresten bir bayt oku.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            
        Returns:
            int: 0-255 arasında bir bayt
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        if addr not in self.devices:
            if random.random() < 0.8:  # %80 olasılıkla hata döndür
                raise IOError(f"I2C cihazı bulunamadı: 0x{addr:02x}")
            # %20 olasılıkla rastgele bir değer döndür
            return random.randint(0, 255)
            
        # Cihaz varsa rastgele bir değer döndür (veya cihaz kimliğini)
        device = self.devices[addr]
        if 0x00 in device["registers"]:
            value = device["registers"][0x00]
        else:
            value = random.randint(0, 255)
            
        print(f"Dummy SMBus read_byte: [0x{addr:02x}] -> 0x{value:02x}")
        return value

    def write_byte(self, addr, value):
        """
        Belirtilen adrese bir bayt yaz.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            value: 0-255 arasında bir bayt
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        if addr not in self.devices:
            if random.random() < 0.8:  # %80 olasılıkla hata döndür
                raise IOError(f"I2C cihazı bulunamadı: 0x{addr:02x}")
            return  # Sessizce başarısız ol
            
        # Cihaz varsa, 0x00 kaydına yaz
        device = self.devices[addr]
        if "registers" in device:
            device["registers"][0x00] = value & 0xFF
            
        print(f"Dummy SMBus write_byte: [0x{addr:02x}] <- 0x{value:02x}")

    def read_byte_data(self, addr, cmd):
        """
        Belirtilen adres ve komut kaydından bir bayt oku.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            
        Returns:
            int: 0-255 arasında bir bayt
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        if addr not in self.devices:
            if random.random() < 0.8:
                raise IOError(f"I2C cihazı bulunamadı: 0x{addr:02x}")
            return random.randint(0, 255)
            
        # Cihaz varsa, belirtilen kaydı oku
        device = self.devices[addr]
        if "registers" in device and cmd in device["registers"]:
            value = device["registers"][cmd]
        else:
            # Kayıt yoksa rastgele bir değer döndür
            value = random.randint(0, 255)
            if "registers" in device:
                device["registers"][cmd] = value  # Yeni kayıt oluştur
            
        print(f"Dummy SMBus read_byte_data: [0x{addr:02x}, 0x{cmd:02x}] -> 0x{value:02x}")
        return value

    def write_byte_data(self, addr, cmd, value):
        """
        Belirtilen adres ve komut kaydına bir bayt yaz.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            value: 0-255 arasında bir bayt
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        if addr not in self.devices:
            if random.random() < 0.8:
                raise IOError(f"I2C cihazı bulunamadı: 0x{addr:02x}")
            return
            
        # Cihaz varsa, belirtilen kaydı yaz
        device = self.devices[addr]
        if "registers" in device:
            device["registers"][cmd] = value & 0xFF
            
        print(f"Dummy SMBus write_byte_data: [0x{addr:02x}, 0x{cmd:02x}] <- 0x{value:02x}")

    def read_word_data(self, addr, cmd):
        """
        Belirtilen adres ve komut kaydından bir word (2 bayt) oku.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            
        Returns:
            int: 0-65535 arasında bir word
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        # İki bayt oku ve birleştir (little endian)
        low = self.read_byte_data(addr, cmd) & 0xFF
        high = self.read_byte_data(addr, cmd + 1) & 0xFF
        value = (high << 8) | low
            
        print(f"Dummy SMBus read_word_data: [0x{addr:02x}, 0x{cmd:02x}] -> 0x{value:04x}")
        return value

    def write_word_data(self, addr, cmd, value):
        """
        Belirtilen adres ve komut kaydına bir word (2 bayt) yaz.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            value: 0-65535 arasında bir word
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        # Word'ü iki bayta ayır ve yaz (little endian)
        low = value & 0xFF
        high = (value >> 8) & 0xFF
        self.write_byte_data(addr, cmd, low)
        self.write_byte_data(addr, cmd + 1, high)
            
        print(f"Dummy SMBus write_word_data: [0x{addr:02x}, 0x{cmd:02x}] <- 0x{value:04x}")

    def read_block_data(self, addr, cmd):
        """
        Belirtilen adres ve komut kaydından bir veri bloğu oku.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            
        Returns:
            list: Bayt değerlerinden oluşan bir liste
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        if addr not in self.devices:
            if random.random() < 0.8:
                raise IOError(f"I2C cihazı bulunamadı: 0x{addr:02x}")
            
            # Rastgele bir blok döndür
            block_length = random.randint(1, 32)
            return [random.randint(0, 255) for _ in range(block_length)]
            
        # NFC okuyucu için özel simülasyon
        if addr == 0x24:
            # PN532'den UID simülasyonu
            uid = [0x04, 0xE1, 0x5F, 0xAA, 0x75, 0xBD, 0x1E]
            print(f"Dummy SMBus read_block_data (NFC UID): [0x{addr:02x}, 0x{cmd:02x}] -> {uid}")
            return uid
            
        # Rastgele bir blok döndür
        block_length = random.randint(1, 32)
        block_data = [random.randint(0, 255) for _ in range(block_length)]
        
        print(f"Dummy SMBus read_block_data: [0x{addr:02x}, 0x{cmd:02x}] -> {block_data}")
        return block_data

    def write_block_data(self, addr, cmd, data):
        """
        Belirtilen adres ve komut kaydına bir veri bloğu yaz.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            data: Baytlardan oluşan bir liste
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        if addr not in self.devices and random.random() < 0.8:
            raise IOError(f"I2C cihazı bulunamadı: 0x{addr:02x}")
            
        print(f"Dummy SMBus write_block_data: [0x{addr:02x}, 0x{cmd:02x}] <- {data}")

    def write_i2c_block_data(self, addr, cmd, data):
        """
        Belirtilen adres ve komut kaydına bir I2C veri bloğu yaz.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            data: Baytlardan oluşan bir liste
        """
        self.write_block_data(addr, cmd, data)

    def read_i2c_block_data(self, addr, cmd, length=32):
        """
        Belirtilen adres ve komut kaydından belirli uzunlukta bir I2C veri bloğu oku.
        
        Args:
            addr: 7-bit I2C cihaz adresi
            cmd: Komut/register adresi
            length: Okunacak bayt sayısı
            
        Returns:
            list: Bayt değerlerinden oluşan bir liste
        """
        if not self.is_open:
            raise IOError("Veri yolu kapalı")
            
        if addr not in self.devices:
            if random.random() < 0.8:
                raise IOError(f"I2C cihazı bulunamadı: 0x{addr:02x}")
            
            # Rastgele bir blok döndür
            return [random.randint(0, 255) for _ in range(length)]
            
        # NFC okuyucu için özel simülasyon
        if addr == 0x24:
            # PN532'den UID simülasyonu
            uid = [0x04, 0xE1, 0x5F, 0xAA, 0x75, 0xBD, 0x1E]
            # İstenen uzunluğa göre kırp veya uzat
            if len(uid) > length:
                uid = uid[:length]
            elif len(uid) < length:
                uid = uid + [0] * (length - len(uid))
            print(f"Dummy SMBus read_i2c_block_data (NFC UID): [0x{addr:02x}, 0x{cmd:02x}, {length}] -> {uid}")
            return uid
            
        # Rastgele bir blok döndür
        block_data = [random.randint(0, 255) for _ in range(length)]
        
        print(f"Dummy SMBus read_i2c_block_data: [0x{addr:02x}, 0x{cmd:02x}, {length}] -> {block_data}")
        return block_data 