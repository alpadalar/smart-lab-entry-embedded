import time
import usbrelay_py

def trigger_relays():
    """USB röleleri tetikler"""
    try:
        # Bağlı röle kartlarının sayısını al
        count = usbrelay_py.board_count()
        print("Tespit edilen kart sayısı:", count)

        # Kart detaylarını al
        boards = usbrelay_py.board_details()
        print("Kart detayları:", boards)

        # Her kart için işlemleri gerçekleştir
        for board in boards:
            board_id = board[0]
            num_relays = board[1]
            print(f"\nKart {board_id} üzerinde {num_relays} röle bulundu.")

            # Tüm röleleri aç
            for relay in range(1, num_relays + 1):
                print(f"Board {board_id} -> Röle {relay} açılıyor...")
                result = usbrelay_py.board_control(board_id, relay, 1)
                print("Sonuç:", result)
                time.sleep(0.5)  # Kısa gecikme

            # Röle açık kalması için 3 saniye bekle
            time.sleep(3)

            # Tüm röleleri kapat
            for relay in range(1, num_relays + 1):
                print(f"Board {board_id} -> Röle {relay} kapatılıyor...")
                result = usbrelay_py.board_control(board_id, relay, 0)
                print("Sonuç:", result)
                time.sleep(0.5)  # Kısa gecikme

    except Exception as e:
        print(f"Röle kontrol hatası: {str(e)}")
        raise 