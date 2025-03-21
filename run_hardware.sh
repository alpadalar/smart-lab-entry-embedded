#!/bin/bash

# GPIO factory olarak rpigpio kullan
export GPIOZERO_PIN_FACTORY=rpigpio

# Gerçek donanım modu
export SIMULATION_MODE=false

# Sanal ortamın mutlak yolunu belirt
VENV_PATH="$PWD/venv"

# Sanal ortamı aktif et (varsa)
if [ -d "$VENV_PATH" ]; then
    echo "Sanal ortam aktif ediliyor..."
    . "$VENV_PATH/bin/activate"
fi

# Root yetkisiyle çalıştır
echo "Program root yetkisiyle başlatılıyor..."
sudo PYTHONPATH="$PWD" GPIOZERO_PIN_FACTORY=rpigpio SIMULATION_MODE=false python3 main.py 