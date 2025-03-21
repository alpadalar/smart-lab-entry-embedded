#!/bin/bash

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Kurulum başlatılıyor...${NC}"

# Python3 ve pip kurulumu
echo -e "${YELLOW}Python3 ve pip kontrol ediliyor...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 bulunamadı. Kuruluyor...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Gerekli build araçlarını yükle
echo -e "${YELLOW}Build araçları yükleniyor...${NC}"
sudo apt install -y python3-dev build-essential python3-wheel

# usbrelay kurulumu
echo -e "${YELLOW}usbrelay kurulumu yapılıyor...${NC}"
cd ~/usbrelay
make
sudo make install
cd usbrelay_py
python3 setup.py bdist_wheel
pip3 install -e .
cd ../..

# Sanal ortam oluştur
echo -e "${YELLOW}Sanal ortam oluşturuluyor...${NC}"
python3 -m venv venv

# Sanal ortamı aktifleştir ve paketleri yükle
echo -e "${YELLOW}Paketler yükleniyor...${NC}"
source venv/bin/activate
pip install -r requirements.txt

echo -e "${GREEN}Kurulum tamamlandı!${NC}"
echo -e "${YELLOW}Sistemi başlatmak için:${NC}"
echo -e "1. Sanal ortamı aktifleştirin: ${GREEN}source venv/bin/activate${NC}"
echo -e "2. Programı çalıştırın: ${GREEN}python -m src.main${NC}" 