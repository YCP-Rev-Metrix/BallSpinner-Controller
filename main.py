from BallSpinnerController.BallSpinnerController import BallSpinnerController
from BallSpinnerController.HMI import * 
import sys
import threading
import queue

def BSC_thread():
    if len(sys.argv) > 1:
        if sys.argv[1] == "1":
            BallSpinnerController.BallSpinnerController(shared_data, debug="1")
    else:
        BallSpinnerController.BallSpinnerController(shared_data)

#In order to know whether or not the HMI can successfully run, we create an HMI thread class that stores an exception.
class HMIThread(threading.Thread):
    def __init__(self, shared_data, fullscreen=True):
        super().__init__()
        self.shared_data = shared_data
        self.exception = False  # This will track if an exception occurs
        self._stop_event = threading.Event()  # Event to stop the thread


    def run(self):
        try:
            # UI initialization and method calls
            ui = HMI(self.shared_data, fullscreen)
            ui.check_for_updates()
            ui.run()
        except Exception as e:
            print(e)
            print("The HMI does not have a display connected, running in headless mode.")
            print("For information on how to open the HMI in SSH, view Brandon Woodward Spring25 Journal page 11")
            self.exception = True
            self._stop_event.set()  # Set the stop event to end the thread gracefully

if __name__ == "__main__":
    shared_data = {
            "protocol_queue": queue.Queue(),
            "motor_currents": [0,0,0],
            "can_launch_BSC": True,
            "close_bsc":False,
            "ip": "",
            "port": "",
            "name": "",
            "sample_rates":["--:--","--:--","--:--","--:--"],
            "mode": "",
            "message_type": "",
            "bg_color": 'dodgerblue2',
            "geometry": "600x300",  # Set the window size to 600x300 pixels
            "title": "Ball Spinner Controller GUI",
            "configure": 'dodgerblue2',  # Set the background color of the window
            "error_text": "",
            "i": 0,
            "estop": False,
    }
        
    # Create threads for the UI and the other loop
    fullscreen = True
    if len(sys.argv) > 1:
        if sys.argv[1] == "1":
            fullscreen = False
    hmi_thread = HMIThread(shared_data, fullscreen)

    # Start the HMI thread first
    print("Starting the HMI thread")
    hmi_thread.start()
    print("HMI thread joining main thread")
    #Calling join here allows us to get back to the main execution.
    hmi_thread.join()

    if hmi_thread.exception == True: #If unsuccessful, launch in headless mode
        #Run in headless mode because the hmi_thread did not launch successfully. 
        shared_data["can_launch_BSC"] = False
        bsc_thread = threading.Thread(target=BSC_thread)
        print("Starting the BSC server thread")
        bsc_thread.start()
        print("BSC server thread joining main thread")
        bsc_thread.join()
