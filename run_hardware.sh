#!/bin/bash

# Simülasyon modunu false olarak ayarla
export SIMULATION_MODE=false

# Sanal ortamı aktif et (varsa)
if [ -d "venv" ]; then
    echo "Sanal ortam aktif ediliyor..."
    source venv/bin/activate
fi

# Sudo ile çalıştır
echo "Program root yetkileriyle başlatılıyor..."
sudo SIMULATION_MODE=false python3 main.py 