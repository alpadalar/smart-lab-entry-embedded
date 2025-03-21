import requests
from config import API_URL, CONTROLLER_ID

class APIClient:
    def __init__(self):
        self.api_url = API_URL
        
    def check_access(self, card_uid, is_inside):
        """Kart erişim kontrolü yapar"""
        try:
            payload = {
                "cardUID": card_uid,
                "isInside": is_inside,
                "controllerId": CONTROLLER_ID
            }
            
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            return response.json().get("openDoor", False)
        except Exception as e:
            print(f"API hatası: {e}")
            return False 