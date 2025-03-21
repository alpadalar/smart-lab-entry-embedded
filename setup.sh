#!/bin/bash

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hata kontrolü fonksiyonu
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}Hata: $1${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}Kurulum başlatılıyor...${NC}"

# Python kontrolü
echo -e "${YELLOW}Python kontrolü yapılıyor...${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}Python3 bulundu${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo -e "${GREEN}Python bulundu${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}Python bulunamadı. Kuruluyor...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv python3-full
    check_error "Python kurulumu başarısız"
    PYTHON_CMD="python3"
fi

# Gerekli build araçlarını yükle
echo -e "${YELLOW}Build araçları yükleniyor...${NC}"
sudo apt install -y python3-dev build-essential python3-wheel
check_error "Build araçları kurulumu başarısız"

# usbrelay kurulumu
echo -e "${YELLOW}usbrelay kurulumu yapılıyor...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USBRELAY_DIR="$SCRIPT_DIR/usbrelay"

if [ ! -d "$USBRELAY_DIR" ]; then
    echo -e "${RED}usbrelay dizini bulunamadı! ($USBRELAY_DIR)${NC}"
    echo -e "${YELLOW}Lütfen usbrelay dizininin doğru konumda olduğundan emin olun.${NC}"
    exit 1
fi

cd "$USBRELAY_DIR"
check_error "usbrelay dizinine geçilemedi"

make
check_error "usbrelay derleme hatası"

sudo make install
check_error "usbrelay kurulum hatası"

cd usbrelay_py
check_error "usbrelay_py dizinine geçilemedi"

$PYTHON_CMD setup.py bdist_wheel
check_error "usbrelay_py wheel oluşturma hatası"

# Sanal ortam oluştur
echo -e "${YELLOW}Sanal ortam oluşturuluyor...${NC}"
$PYTHON_CMD -m venv venv
check_error "Sanal ortam oluşturma hatası"

# Sanal ortamı aktifleştir ve paketleri yükle
echo -e "${YELLOW}Paketler yükleniyor...${NC}"
. venv/bin/activate
check_error "Sanal ortam aktifleştirme hatası"

pip install --upgrade pip
check_error "pip güncelleme hatası"

pip install -r requirements.txt
check_error "Paket kurulum hatası"

echo -e "${GREEN}Kurulum tamamlandı!${NC}"
echo -e "${YELLOW}Sistemi başlatmak için:${NC}"
echo -e "1. Sanal ortamı aktifleştirin: ${GREEN}. venv/bin/activate${NC}"
echo -e "2. Programı çalıştırın: ${GREEN}$PYTHON_CMD -m src.main${NC}" 