import requests
import yaml

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

def send_card(uid, is_inside):
    payload = {
        "cardUID": uid,
        "isInside": is_inside,
        "controllerId": config['controller_id']
    }
    try:
        res = requests.post(config['api_url'], json=payload)
        return res.status_code, res.json() if res.status_code == 200 else None
    except Exception as e:
        return 500, {"error": str(e)} 