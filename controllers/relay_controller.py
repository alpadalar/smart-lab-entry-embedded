import usbrelay_py
import time

def trigger_relay():
    boards = usbrelay_py.board_details()
    for board_id, num_relays in boards:
        for relay in range(1, num_relays + 1):
            usbrelay_py.board_control(board_id, relay, 1)
        time.sleep(3)
        for relay in range(1, num_relays + 1):
            usbrelay_py.board_control(board_id, relay, 0) 