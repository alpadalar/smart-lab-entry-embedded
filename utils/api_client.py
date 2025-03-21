import requests
import yaml
import time
import random
import os

# Simülasyon modu kontrolü
SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'true').lower() in ('true', '1', 't', 'yes')

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

def send_card(uid, is_inside):
    """Kart ID'sini API'ye gönderir ve kapı durumunu alır"""
    payload = {
        "cardUID": uid,
        "isInside": is_inside,
        "controllerId": config['controller_id']
    }
    
    if SIMULATION_MODE:
        # Simülasyon modunda, gerçek API'ye bağlanmak yerine rastgele yanıt üret
        print(f"[API] Simülasyon gönderimi: {payload}")
        time.sleep(0.5)  # API yanıt gecikmesini simüle et
        
        # %70 olasılıkla kapıyı aç
        should_open = random.random() < 0.7
        response = {
            "openDoor": should_open,
            "userName": "Simüle Edilmiş Kullanıcı",
            "message": "Bu bir simülasyon yanıtıdır"
        }
        return 200, response
    else:
        # Gerçek API isteği
        try:
            res = requests.post(config['api_url'], json=payload)
            return res.status_code, res.json() if res.status_code == 200 else None
        except Exception as e:
            return 500, {"error": str(e)} 