"""
Simülasyon modu kontrolü için yardımcı fonksiyonlar.
"""

import os
import logging

# Varsayılan simülasyon modu ayarı
_SIMULATION_MODE = True

def set_simulation_mode(mode):
    """
    Simülasyon modunu ayarla.
    
    Args:
        mode (bool): Simülasyon modunu etkinleştir veya devre dışı bırak
    """
    global _SIMULATION_MODE
    _SIMULATION_MODE = bool(mode)
    logging.info(f"Simülasyon modu {'etkinleştirildi' if _SIMULATION_MODE else 'devre dışı bırakıldı'}")

def is_simulation_mode():
    """
    Mevcut simülasyon modunu döndür.
    
    Returns:
        bool: Simülasyon modu etkin ise True, değilse False
    """
    # Çevre değişkenini kontrol et (komut dosyalarından ayarlanabilir)
    env_sim_mode = os.environ.get('SIMULATION_MODE', '').lower()
    
    if env_sim_mode in ('true', '1', 't', 'y', 'yes', 'evet'):
        return True
    elif env_sim_mode in ('false', '0', 'f', 'n', 'no', 'hayır'):
        return False
    
    # Çevre değişkeni ayarlanmadıysa varsayılan değeri kullan
    return _SIMULATION_MODE

def is_hardware_mode():
    """
    Donanım modunda çalışıp çalışmadığını kontrol et.
    
    Returns:
        bool: Donanım modunda ise True, değilse False (simülasyon modu)
    """
    return not is_simulation_mode()

def detect_platform():
    """
    Platformu otomatik olarak algılar (Raspberry Pi mi değil mi?).
    
    Returns:
        str: 'raspberry_pi', 'raspberry_pi_5', veya 'other'
    """
    try:
        # Raspberry Pi modelini kontrol et
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            if 'Raspberry Pi' in model:
                if '5 Model' in model:
                    return 'raspberry_pi_5'
                return 'raspberry_pi'
    except (IOError, FileNotFoundError):
        pass  # Raspberry Pi değil
    
    return 'other'

def auto_detect_simulation_mode():
    """
    Platformu algılayarak simülasyon modunu otomatik olarak ayarla.
    
    Returns:
        bool: Simülasyon modu etkin ise True, değilse False
    """
    platform = detect_platform()
    
    # Raspberry Pi'de donanım modu, diğer platformlarda simülasyon modu
    simulation_mode = platform == 'other'
    
    set_simulation_mode(simulation_mode)
    logging.info(f"Platform: {platform}, Simülasyon modu: {simulation_mode}")
    
    return simulation_mode 