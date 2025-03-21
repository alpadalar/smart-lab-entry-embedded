"""
LCD simülasyon modülü - gerçek LCD ekran olmayan ortamlarda kullanmak için
"""

class CharLCD:
    def __init__(self, i2c_expander, address, cols=20, rows=4, **kwargs):
        self.i2c_expander = i2c_expander
        self.address = address
        self.cols = cols
        self.rows = rows
        self.cursor_pos = (0, 0)
        self.display = [' ' * cols for _ in range(rows)]
        print(f"[DummyLCD] LCD ekran başlatıldı: {rows}x{cols}, {i2c_expander} @ 0x{address:02x}")
    
    def write_string(self, text):
        row, col = self.cursor_pos
        
        # Mevcut satırı güncelle
        current_row = self.display[row]
        
        # Yazmaya başlanacak noktadan itibaren metni yerleştir
        new_row = current_row[:col]
        for i, char in enumerate(text):
            if col + i < self.cols:
                new_row += char
        
        # Kalan kısmı doldur
        if len(new_row) < self.cols:
            new_row += current_row[len(new_row):]
        
        # Satırı güncelle
        self.display[row] = new_row
        
        # Ekranı yazdır
        self._print_display()
        
        # İmleç konumunu güncelle
        self.cursor_pos = (row, min(col + len(text), self.cols - 1))
    
    def clear(self):
        self.display = [' ' * self.cols for _ in range(self.rows)]
        self.cursor_pos = (0, 0)
        print("[DummyLCD] Ekran temizlendi")
        self._print_display()
    
    def _print_display(self):
        print("[DummyLCD] Ekran içeriği:")
        print("+" + "-" * self.cols + "+")
        for row in self.display:
            print("|" + row + "|")
        print("+" + "-" * self.cols + "+") 