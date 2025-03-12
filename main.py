from BallSpinnerController.BallSpinnerController import BallSpinnerController
from BallSpinnerController.HMI import * 
import sys
import threading

if __name__ == "__main__":
    shared_data = {
            "ip": "",
            "port": "",
            "name": "",
            "xl": "",
            "gy": "",
            "mg": "",
            "lt": "",
            "mode": "",
            "message_type": "",
            "bg_color": 'dodgerblue2',
            "geometry": "600x300",  # Set the window size to 600x300 pixels
            "title": "Ball Spinner Controller GUI",
            "configure": 'dodgerblue2',  # Set the background color of the window
            "error_text": "",
            "i": 0
    }


def BSC_thread():
    if len(sys.argv) > 1:
        if sys.argv[1] == "1":
            BallSpinnerController(shared_data, debug="1")
    else:
        BallSpinnerController(shared_data)

# Create threads for the UI and the other loop
ui_thread = threading.Thread(target=run_ui, args=(shared_data,))
bsc_thread = threading.Thread(target=BSC_thread)

# Start the threads
print("Starting the HMI thread")
ui_thread.start()
print("Starting the BSC server thread")
bsc_thread.start()

# Join the threads to the main thread
print("HMI thread joining main thread")
ui_thread.join()
print("BSC server thread joining main thread")
bsc_thread.join()

