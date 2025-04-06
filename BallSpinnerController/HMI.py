import tkinter as tk
import threading
from BallSpinnerController import BallSpinnerController
from BallSpinnerController.hmi_gui_utility.scroll_frame import ScrollbarFrame
import random
import queue
from BallSpinnerController.StepperMotor import StepperMotor
class HMI:
    def __init__(self, data):
        
        #This is our shared data dictionary that we check for changes in 
        self.data = data
        
        # How fast we check shared data dictionary to update values in the UI 
        self.ui_update_frequency = 200  
        
        #This try catch is for the automatic headless display when we fail to open HMI (most likely to occur on unsetup SSH see BWoodward Spring Journal 2025)
        try:
            self.root = tk.Tk()
        except Exception as e:
            print(e)
            pass

################################################### Function variables ###################################################\
        self.active_motor = None  # Track which motor's popup is active
        self.emergency_stop_clicks = 0
        self.is_emergency_stopped = False

        self.bsc = None

################################################### Initialize UI ###################################################\
        self.root.attributes('-fullscreen', True)  # Set the window size to 600x300 pixels
        # Remove window decorations (title bar, borders)
        self.root.overrideredirect(True)
        # Set window size to full screen

        # Keep window on top (optional)
        self.root.attributes("-topmost", True)
        # self.root.geometry("800x480")
        self.screen_width = 800
        self.screen_height = 480
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        
        self.root.title("Ball Spinner HMI")
        self.root.configure(bg=self.data["bg_color"])  # Set the background color of the window

        #Create root frame
        #Purpose of this frame is to create a widget that everything is in. This way we can lift(self.frame) or lower(self.frame) to hide or show widgets.
        #When making children widgets and placing them using place(), grid(), or pack() make sure to include (in_=self.frame)
        ## IF making elements inside another frame ELSEWHERE: new_frame.pack(in_=self.frame) and children use in_=new_frame 
        self.frame = tk.Frame(self.root, bg=self.data["bg_color"])
        self.frame.pack(side="top", fill="both", expand=True)

        self.title_label = self.build_title_label()
        self.e_frame, self.e_label = self.build_error_box()
        self.close_button = self.build_close_button()
        self.ip_label = self.build_ip_port_text()
        self.mode_label, self.message_label = self.build_mode_and_message_labels()
        self.motor_buttons = self.create_motor_buttons_grid()
        self.motor_popup = self.create_motor_popup()
        self.sd_window = self.create_SD_window()
        self.emergency_stop_button = self.create_emergency_stop_button()
        self.bsc_button = self.create_BSC_button()
        self.local_mode_button = self.create_local_mode_button()
        self.reset_button = self.create_reset_button()

        self.protocol_history_list = []
        self.protocol_history_circular_buffer_index = 0
        self.protocol_history_circular_buffer_size = 50
        self.protocol_history_window = self.create_protocol_history_window()
        self.show_protocol_button = self.create_protocol_history_button()
        
        #Local only elements
        self.motor_controller_window = self.create_motor_controller_window()
        self.motor = None
        #List of elements to initially hide

        #initialize stack for back button
        self.action_stack = [] #Filled with pairs of lists, lis[0] means it was just shown, list[1] means it was just hidden

        self.all_ui_elements = [
            self.title_label,
            self.e_frame, 
            self.e_label,
            self.close_button,
            self.ip_label, 
            self.mode_label, 
            self.message_label,
            self.motor_buttons, 
            self.motor_popup, 
            self.sd_window,
            self.emergency_stop_button, 
            self.bsc_button,
            self.local_mode_button, 
            self.reset_button,
            self.protocol_history_window,
            self.show_protocol_button,
        ]

        #self.is_protocol_visible = False
        
        #Initialize the lists for the BSC page
        self.hidden_ui_elements = [
            self.ip_label,
            self.mode_label,
            self.message_label,
            self.emergency_stop_button,
            self.sd_window,
            self.show_protocol_button,
            self.motor_buttons,
            self.reset_button,
            # self.protocol_history_window,
        ]
        #These are for the BSC page
        self.shown_ui_elements = [
            self.title_label,
            self.e_frame, 
            self.e_label,
            self.close_button,
            self.bsc_button,
            self.local_mode_button, 
            self.motor_popup
        ]

        #False means it is hidden, true means it is shown
        self.button_toggleable_elements = {
            self.protocol_history_window : False,
        }

        #self.shown_ui_elements = [element for element in self.all_ui_elements if element not in self.hidden_ui_elements]
       # print(f"SHOWN UI ELEMENTS: {self.shown_ui_elements}")
       # print(f"HIDDEN UI ELEMENTS: {self.hidden_ui_elements}")

    
        self.initial_ui_elements_to_hide = self.hidden_ui_elements
        self.initial_ui_elements_to_show = self.shown_ui_elements

        #Create initial start screen by hiding and showing the correct elements
        self.hide_ui_elements(self.initial_ui_elements_to_hide)
        self.hide_ui_elements(self.button_toggleable_elements)

        #Local mode list initialization
        self.local_ui_elements_to_show = [
            self.motor_buttons, 
            self.reset_button,
            self.motor_controller_window,
            self.emergency_stop_button,

        ]
        self.hide_ui_elements(self.local_ui_elements_to_show)



        

################################################### UI Utility Functions ################################################### 
   
   #CONSIDER TRY CATCHING EACH attempt
    def hide_ui_elements(self, ui_element_list):
        try:
            for e in ui_element_list:
                e.lower(self.frame)#pass in root frame
        except Exception as e:
            print(e)

    def show_ui_elements(self, ui_element_list):
        try:
            for e in ui_element_list:
                e.lift(self.frame)
        except Exception as e:
            print(e)

    def back_button_action_stack(self):
        lists = self.action_stack.pop()
        ui_elements_to_show = lists[1]
        ui_elements_to_hide = lists[0]

        for i in self.button_toggleable_elements:
            if i == True and i in ui_elements_to_hide:
                ui_elements_to_show = list[0]
                ui_elements_to_hide = list[1]
            
                print("accounting for the popup window")

        self.show_ui_elements(ui_elements_to_show)
        self.hide_ui_elements(ui_elements_to_hide)


    # Update Display
    def change_page(self, ui_elements_to_show, ui_elements_to_hide):
        print(f"PUSHED TO STACK: {ui_elements_to_hide}")
        print(f"JUST SHOWN: {ui_elements_to_show}")
        # if None in ui_elements_to_hide:
        self.action_stack.append([ui_elements_to_show, ui_elements_to_hide])
        if None not in ui_elements_to_hide:
            self.hide_ui_elements(ui_elements_to_hide)
        if None not in ui_elements_to_show:
            self.show_ui_elements(ui_elements_to_show)

################################################### Initialize Loops ###################################################\
    def run(self):
        self.root.mainloop()

    def check_for_updates(self):
        updates = {
            self.e_label: self.data["error_text"],
            self.ip_label: self.data["ip"],
            self.message_label: self.data["message_type"],
            self.sd_xl : self.data["sample_rates"][0],
            self.sd_gy : self.data["sample_rates"][1],
            self.sd_mg : self.data["sample_rates"][2],
            self.sd_lt : self.data["sample_rates"][3],
        }

        for label, new_text in updates.items():
            if label.cget("text") != new_text:
                label.config(text=new_text)
        
        #Update motor current value to keep updating while current changes based on active motor
        #Get the exact value from the label
        if self.popup_current.cget("text") != "" and self.active_motor is not None:
            current_value = self.popup_current.cget("text").split(' ')[1].split('A')[0]
            if current_value != self.data["motor_currents"][self.active_motor-1]:
                self.popup_current.config(text=f"Current: {self.data['motor_currents'][self.active_motor-1]}A")
       
        #Check the motor rpm to update the local mode text
        if self.motor is not None:
            self.update_motor_controller_text()
        #Iterate through the protocol queue and write the messages to the history.
        while not self.data["protocol_queue"].empty():
            self.update_protocol_list(self.data["protocol_queue"].get())

        self.root.after(self.ui_update_frequency, self.check_for_updates)

################################################### Basic Data Labels ###################################################
    def build_mode_and_message_labels(self):
        # First label
        label1 = tk.Label(self.root, text="Mode: ", bg="lightgray", padx=10, pady=5,borderwidth=1, relief="solid")
        label1.place(in_=self.frame, relx=.05, rely=.4)  # Place on the left side with a bit of padding

        # Second label
        label2 = tk.Label(self.root, text="", bg="lightgray", padx=10, pady=5, width=20, borderwidth=1, relief="solid")
        label2.place(in_=self.frame, relx=.05, rely=.5)  # Place it right below the first label with some vertical space

        return label1, label2

    def build_ip_port_text(self):
        label = tk.Label(self.root, text="Socket: 11.1.1.1.1:64920",  padx=10, pady=10)
        label.pack(in_=self.frame, side='bottom')
        return label
   
    # Create a title "Ball Spinner Controller"
    def build_title_label(self):
        title = tk.Label(self.root, text="Ball Spinner Controller", bg=self.data["bg_color"])
        title.pack(in_=self.frame,side='top', fill='both')
        return title

    # Create the error frame and label
    def build_error_box(self):
        e_frame = tk.Frame(self.root, bg='gray')
        e_frame.pack(in_=self.frame, side='top')
        e_text = tk.Label(e_frame, text=f"Error: ", fg='red', width=50)
        e_text.pack()
        return e_frame, e_text

        # sbf = ScrollbarFrame(self.root)
        # sbf.pack(in_=self.frame, anchor="center")
################################################### Protocol History popup ###################################################
    def create_protocol_history_window(self):
        sbf = ScrollbarFrame(self.root)
        sbf.pack(in_=self.frame,)
        sbf_frame = sbf.scrolled_frame
        count = 0
        self.protocol_labels = []
        for i in self.protocol_history_list:
            label = tk.Label(sbf_frame, text=f"{len(self.protocol_history_list)-count}: {self.protocol_history_list[len(self.protocol_history_list)-count - 1]}",
                    width = 50, anchor="w", borderwidth="1", relief="solid") 
            label.grid(row=count, column=0)
            count += 1
            self.protocol_labels.append(label)
        return sbf
    def update_protocol_list(self, new_text):
        self.protocol_history_list.append(new_text)
        #Remove labels
        for i in self.protocol_labels:
            new_row = i.grid_info()['row'] + 1
            i.grid(row=new_row)
        label = tk.Label(self.protocol_history_window.scrolled_frame, text=f"{len(self.protocol_history_list)}: {new_text}",
                    width = 50, anchor="w", borderwidth="1", relief="solid") 
        label.grid(row=0, column=0) 
        self.protocol_labels.append(label)

################################################### Local Motor Controller ###################################################
    def create_motor_controller_window(self):
        x = 200
        y = 333
        
        # Create a frame inside self.frame
        mc_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10, borderwidth=2, relief="ridge", width = 400, height = 100)
        mc_frame.place(x=x, y=y)
        mc_frame.grid_propagate(False) #Don't shrink frame to content


        # Configure columns for centering
        for i in range(8):  
            mc_frame.grid_columnconfigure(i, weight=1)  # Stretch columns equally

        
        # Create a label inside mc_frame
        self.selected_motor = tk.Label(mc_frame, bg="lightgray", text=f"Select a motor button", font=("Arial", 12,))
        self.selected_motor.grid(row=0, column=0, columnspan=3, pady=5)

        # Create buttons inside mc_frame using grid (instead of pack)
        self.motor_controller_buttons = []
        self.motor_button_text_list = ["-50", "-10", "-1", "+1", "+10", "+50"]
        for i in range(6):
            btn = tk.Button(mc_frame, text=self.motor_button_text_list[i], width = 2, font=("Arial", 14, "bold"), command=lambda i=i: self.change_motor_speed(i))
            btn.grid(row=1, column=i, padx=5, pady=5,)
            self.motor_controller_buttons.append(btn)
        return mc_frame

    def update_motor_controller_text(self):
        if self.motor:
            self.selected_motor.config(text=f"Controlling RPM of motor {self.active_motor}, RPM: {self.motor.rpm}")
            if self.popup_speed.cget("text") != "" and self.popup_speed.cget("text").split(" ")[1] != self.motor.rpm:
                self.popup_speed.config(text = f"Speed: {self.motor.rpm} RPM")

    def change_motor_speed(self, btn_idx):
        if self.motor.state == False:
            self.motor.turnOnMotor()
        increment = self.motor_button_text_list[btn_idx]
        if btn_idx > 2:
            increment = int(increment.split("+")[1])
        else:
            increment = int(increment)
        print(f"Button idx {btn_idx}")
        print(f"Changing motor speed by: {increment}")
        self.motor.changeSpeed(self.motor.rpm + increment)
        print(f"Motor speed should now be: {self.motor.rpm}")\

        self.update_motor_controller_text()

################################################### Motor Data popup ###################################################
    def create_motor_popup(self):
        """Creates an embedded popup frame that appears inside the UI."""
        popup_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10, borderwidth=2, relief="ridge")

        # Labels inside the popup
        self.popup_title = tk.Label(popup_frame, text="Motor Details", font=("Arial", 14, "bold"), bg="lightgray")
        self.popup_current = tk.Label(popup_frame, text="", bg="lightgray")
        self.popup_speed = tk.Label(popup_frame, text="", bg="lightgray")
        self.popup_temp = tk.Label(popup_frame, text="", bg="lightgray")
        self.popup_status = tk.Label(popup_frame, text="", bg="lightgray")

        # Close button (alternative way to close)
        self.close_button = tk.Button(popup_frame, text="Close", command=self.hide_popup)

        # Pack elements inside the popup frame
        self.popup_title.pack(in_=popup_frame,pady=5)
        self.popup_speed.pack(in_=popup_frame,)
        self.popup_temp.pack(in_=popup_frame,)
        self.popup_current.pack(in_=popup_frame,)
        self.popup_status.pack(in_=popup_frame,)
        self.close_button.pack(in_=popup_frame, pady=5)
        return popup_frame        

    def toggle_popup(self, motor_id):
        """Shows or hides the popup based on the button click."""
        if self.active_motor == motor_id:
            self.hide_popup()  # Hide if it's already open
        else:
            self.show_popup(motor_id)  # Show a new popup

    def show_popup(self, motor_id):
        """Updates and displays the popup with motor details."""
        self.popup_current.config(text=f"Current: {self.data['motor_currents'][motor_id-1]}A")
        self.popup_title.config(text=f"Motor {motor_id} Details")
        self.popup_speed.config(text=f"Speed: {100 + motor_id * 10} RPM")
        self.popup_temp.config(text=f"Temperature: {40 + motor_id}°C")
        self.popup_status.config(text=f"Status: Running")

        # Place the popup in the UI
        self.motor_popup.place(in_=self.frame, relx=0.5, rely=0.5, anchor="center")
        self.active_motor = motor_id  # Store active motor

        self.update_motor_controller_text()

    def hide_popup(self):
        """Hides the popup."""
        self.motor_popup.place_forget()
        self.active_motor = None  # Reset active motor
    

################################################### SD Data Display ###################################################
    #Create the SD window on the right side of the UI
    def create_SD_window(self):
        sd_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10, borderwidth=2, relief="ridge")

        # Add labels inside the SD window
        self.sd_title = tk.Label(sd_frame, text="SD Information", font=("Arial", 14, "bold"), bg="lightgray")
        self.sd_xl = tk.Label(sd_frame, text="XL: --", bg="lightgray")
        self.sd_gy = tk.Label(sd_frame, text="GY: --", bg="lightgray")
        self.sd_mg = tk.Label(sd_frame, text="MG: --", bg="lightgray")
        self.sd_lt = tk.Label(sd_frame, text="LT: --", bg="lightgray")

        # Pack elements inside the SD window
        self.sd_title.pack(pady=5)
        self.sd_xl.pack(pady=5)
        self.sd_gy.pack(pady=5)
        self.sd_mg.pack(pady=5)
        self.sd_lt.pack(pady=5)


        # Place the SD window on the right side
        sd_frame.place(relx=0.85, rely=0.5, anchor="center")
        return sd_frame

################################################### Create Buttons ###################################################
    def create_reset_button(self):
        reset_button = tk.Button(self.root, text="Back", command=self.back_button_action_stack)
        reset_button.place(in_=self.frame,relx=0.05,rely=0.05)
        return reset_button
    # Create a button to close the window
    def build_close_button(self):
        close_button = tk.Button(self.root, text="Close", command=self.close_window)
        close_button.pack(in_=self.frame, side='bottom', pady=5)
        return close_button

    #create button for starting local mode
    def create_local_mode_button(self):
        # Get the size of the button
        btn_width = 150
        btn_height = 100
        
        # Calculate position to center the button
        position_top = self.screen_height // 2 - btn_height // 2
        position_left = self.screen_width // 2 - btn_width // 2
        button = tk.Button(self.root, text="Start Local Mode", bg="white", command=self.launch_local_mode)
        button.place(in_=self.frame, x=position_left - 150, y=position_top, width=btn_width, height=btn_height)
        return button
    #create button for starting BSC server
    def create_BSC_button(self):
        # Get the size of the button
        btn_width = 150
        btn_height = 100
        
        # Calculate position to center the button
        position_top = self.screen_height // 2 - btn_height // 2
        position_left = self.screen_width // 2 - btn_width // 2
        button = tk.Button(self.root, text="Start BSC Server", bg="white", command=self.launch_BSC_thread_from_HMI)
        button.place(in_=self.frame, x=position_left + 150, y=position_top, width=btn_width, height=btn_height)
        return button

    ####### Button to open the protocol history #######
    def create_protocol_history_button(self):
        button = tk.Button(self.root, text="Open Protocol History", bg="white", command=self.show_protocol_history, width=20)
        button.place(in_=self.frame, relx=.05, rely=.6)  # Place it right below the first label with some vertical space
        return button

    ####### Grid of Motor Toggle Buttons #######
    def create_motor_buttons_grid(self): 
        #Create Grid in center to place motor name Buttons 
        grid_frame = tk.Frame(self.root, bg=self.data["bg_color"])
        grid_frame.pack(in_=self.frame, pady=20)

        # Configure grid inside the frame
        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1)

        grid_frame.grid_rowconfigure(0, weight=1)

        # Create buttons that toggle the popup
        for i in range(3):
            button = tk.Button(grid_frame, text=f"Motor {i+1}", bg="lightblue", width=10, height=2,
                               command=lambda m=i+1: self.toggle_popup(m))
            button.grid(in_=grid_frame, row=0, column=i, padx=10, pady=10)
        return grid_frame
           
    
       
    ####### Emergency Stop Button #######
    def create_emergency_stop_button(self):
        #Creates an emergency stop button in the bottom-left corner of the root window.
        bottom_left_button = tk.Button(self.root, text="EMERGENCY STOP MOTOR", bg="red", command=self.emergency_stop_click)
        bottom_left_button.place(in_=self.frame, relx=0.05, rely=0.95, anchor="sw", width=150, height=50)
        
        # Bind events to track the press and release
        bottom_left_button.bind("<ButtonPress-1>", self.start_emergency_stop_timer)
        bottom_left_button.bind("<ButtonRelease-1>", self.cancel_emergency_stop_timer)

        # Variable to store the timer ID
        self.timer_id = None
        return bottom_left_button
        

################################################### Timer Events ###################################################
    def start_emergency_stop_timer(self, event):
        """Starts the timer when the button is pressed and waits for 3 seconds."""
        # Start a 3-second timer (3000 milliseconds)
        self.timer_id = self.root.after(3000, self.emergency_stop_action)

    def cancel_emergency_stop_timer(self, event):
        """Cancels the timer if the button is released before 3 seconds."""
        if self.timer_id and self.is_emergency_stopped == False:
            self.root.after_cancel(self.timer_id)  # Cancel the action if released early
            self.timer_id = None

################################################### Button Functions ###################################################

    #Functionality of emergency stop
    def emergency_stop_click(self): ####TODO: Should add a timer to reset clicks to 0
        self.emergency_stop_clicks += 1
        self.data["error_text"] = f"Step {self.emergency_stop_clicks} emergency stop"
        if self.emergency_stop_clicks >= 3:
            self.emergency_stop_action()

    def emergency_stop_action(self):
        self.is_emergency_stopped = True
        self.data["error_text"] = f"Emergency Stopped motor"
        self.motor.turnOffMotor()
        print("Emergency Stopped Motor")

    def close_window(self):
        self.root.destroy()
        # Set the error text and update the error label

    #TODO: function for back button from main local or bsc screen    
    # Hide necessary UI elements. 
    # If back to Mode selection screen:     Close server connection if open     
    def reset_to_init_state(self):
        self.data["close_bsc"] = True
        self.full_reset_ui()
        
    def show_protocol_history(self):
        show = [None]
        hide = [None]
        if self.button_toggleable_elements[self.protocol_history_window] == False:
            show = [self.protocol_history_window]
        else:
            hide = [self.protocol_history_window]
        self.button_toggleable_elements[self.protocol_history_window] = not self.button_toggleable_elements[self.protocol_history_window]
        self.change_page(show, hide)          


################################################### Initialize BSC ###################################################
    
    def BSC(self):
        self.bsc = BallSpinnerController.BallSpinnerController(self.data)
    def launch_BSC_thread_from_HMI(self):
        if(self.data["can_launch_BSC"] == True):
            print("The HMI is starting the BSC")
            bsc_thread = threading.Thread(target=self.BSC)
            print("Starting the BSC server thread")
            bsc_thread.start()
            # print("BSC server thread joining main thread")
            # bsc_thread.join()
            print("Printing bsc ", self.bsc)
        else:
            print("Could not start BSC, must set data['can_launch_BSC'] to true")

        #Modify the current UI layout to fit the server mode.
        self.bsc_ui_elements_to_show = self.initial_ui_elements_to_hide
        # self.show_ui_elements(self.bsc_ui_elements_to_show)
        self.bsc_ui_elements_to_hide = {self.bsc_button, self.local_mode_button,}
        self.change_page(self.bsc_ui_elements_to_show, self.bsc_ui_elements_to_hide)
        # self.hide_ui_elements(self.bsc_ui_elements_to_hide)
        # #this is actually a toggle
        # self.show_protocol_history()
        self.motor = None

################################################### Initialize Local Mode ###################################################
    def launch_local_mode(self):
        # self.local_ui_elements_to_show = self.initial_ui_elements_to_hide
        self.local_ui_elements_to_hide = {self.local_mode_button, self.bsc_button}
        self.change_page(self.local_ui_elements_to_show, self.local_ui_elements_to_hide)
        self.motor =  StepperMotor(GPIOPin=12)




################################################### Run as Main Testing (Local Only) ################################################### 
def run_ui(shared_data):
    try:
        ui = UI(shared_data)
        ui.check_for_updates()
        ui.run()
    except:
        print("The HMI does not have a display connected, running in headless mode.")
        print("For information on how to open the HMI in SSH, view Brandon Woodward Spring25 Journal page 11")


#run HMI.py to test it without connecting it to the server
if __name__ == "__main__":
    shared_data = {
            "can_launch_BSC": False,
            "close_bsc":False,
            "ip": "",
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

    run_ui(shared_data)