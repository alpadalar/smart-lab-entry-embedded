#!/bin/bash

# Simülasyon modu varsayılan olarak açık
SIMULATION_MODE=${SIMULATION_MODE:-true}

# Sanal ortamı oluştur (eğer mevcut değilse)
if [ ! -d "venv" ]; then
    echo "Sanal ortam oluşturuluyor..."
    python3 -m venv venv
fi

# Sanal ortamı aktif et
echo "Sanal ortam aktif ediliyor..."
source venv/bin/activate

# Gereksinimleri kur
echo "Kütüphaneler yükleniyor..."
pip install -r requirements.txt

# Ana programı çalıştır
echo "Program başlatılıyor (Simülasyon modu: $SIMULATION_MODE)..."
SIMULATION_MODE=$SIMULATION_MODE python main.py 