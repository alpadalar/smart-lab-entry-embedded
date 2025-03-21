"""
SMBus simülasyon modülü - gerçek I2C erişimi olmayan ortamlarda kullanmak için
"""

class SMBus:
    def __init__(self, bus_number):
        self.bus_number = bus_number
        self.registers = {}
        self.last_addr = None
        print(f"[DummySMBus] SMBus({bus_number}) başlatıldı")
    
    def write_byte(self, addr, value):
        self.last_addr = addr
        print(f"[DummySMBus] 0x{addr:02x} adresine 0x{value:02x} yazılıyor")
    
    def write_byte_data(self, addr, reg, value):
        self.last_addr = addr
        if addr not in self.registers:
            self.registers[addr] = {}
        self.registers[addr][reg] = value
        print(f"[DummySMBus] 0x{addr:02x} adresinin 0x{reg:02x} kaydına 0x{value:02x} yazılıyor")
    
    def read_byte(self, addr):
        self.last_addr = addr
        print(f"[DummySMBus] 0x{addr:02x} adresinden okuma: 0x00")
        return 0x00
    
    def read_byte_data(self, addr, reg):
        self.last_addr = addr
        if addr in self.registers and reg in self.registers[addr]:
            value = self.registers[addr][reg]
            print(f"[DummySMBus] 0x{addr:02x} adresinin 0x{reg:02x} kaydından okuma: 0x{value:02x}")
            return value
        print(f"[DummySMBus] 0x{addr:02x} adresinin 0x{reg:02x} kaydından okuma: 0x00 (varsayılan)")
        return 0x00 