#!/bin/bash

# Simülasyon modunu false olarak ayarla
export SIMULATION_MODE=false

# Sanal ortamın mutlak yolunu belirt
VENV_PATH="$PWD/venv"

# Sanal ortamı aktif et (varsa)
if [ -d "$VENV_PATH" ]; then
    echo "Sanal ortam aktif ediliyor..."
    . "$VENV_PATH/bin/activate"
fi

# Sudo ile çalıştır ve Python yolunu belirt
echo "Program root yetkileriyle başlatılıyor..."
sudo PYTHONPATH="$PWD" SIMULATION_MODE=false python3 main.py 