#!/bin/bash

# Bu script, yapılandırma olmadan simülasyon modunda çalıştırır
echo "Fallback ile program başlatılıyor (Simülasyon modu: true)..."

# Çalışma dizinini script dosyasının bulunduğu yer olarak ayarla
cd "$(dirname "$0")"

# Simülasyon modunda direkt başlat
SIMULATION_MODE=true python3 main.py 