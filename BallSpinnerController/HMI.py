import tkinter as tk

class UI:
    def __init__(self, data):
        self.data = data
        self.ui_update_frequency = 200  # Update the UI every 200 milliseconds
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)  # Set the window size to 600x300 pixels
        self.root.geometry("800x480")
        self.root.title("Ball Spinner HMI")
        self.root.configure(bg=data["bg_color"])  # Set the background color of the window
        self.active_motor = None  # Track which motor's popup is active
        self.emergency_stop_clicks = 0
        self.is_emergency_stopped = False
        # Build the UI components
        self.title_label = self.build_title_label()
        self.e_frame, self.e_label = self.build_error_box()
        self.close_button = self.build_close_button()
        self.ip_label = self.build_ip_port_text()
        self.mode_label, self.message_label = self.build_mode_and_message_labels()
        self.create_grid()
        self.create_motor_popup()
        self.create_SD_window()
        self.create_emergency_stop_button()



    def run(self):
        self.root.mainloop()

    #This is our loop for updating data within the HMI. It checks for changes in the shared dictionary that both the BSC and HMI have.
    def check_for_updates(self):
        if self.data["error_text"] != self.e_label.cget("text"):
            self.e_label.config(text=self.data["error_text"])
        if self.data["ip"] != self.ip_label.cget("text"):
            self.ip_label.config(text=self.data["ip"])
        if self.data["message_type"] != self.message_label.cget("text"):
            self.message_label.config(text=self.data["message_type"])

        #Cause this function to call itself, recurring with ui_update_frequency in ms.
        self.root.after(self.ui_update_frequency, self.check_for_updates)  # Check every 1000 milliseconds (1 second)

    def close_window(self):
        self.root.destroy()
        # Set the error text and update the error label

    # Create a title "Ball Spinner Controller"
    def build_title_label(self):
        title = tk.Label(self.root, text="Ball Spinner Controller", bg=self.data["bg_color"])
        title.pack(side='top', fill='both')
        return title

    # Create the error frame and label
    def build_error_box(self):
        e_frame = tk.Frame(self.root, bg='gray')
        e_frame.pack(side='top')
        e_text = tk.Label(e_frame, text=f"Error: ", fg='red', width=50)
        e_text.pack()
        return e_frame, e_text

    # Create a button to close the window
    def build_close_button(self):
        close_button = tk.Button(self.root, text="Close", command=self.close_window)
        close_button.pack(side='bottom', pady=5)
        return close_button

    def build_mode_and_message_labels(self):
        # # Create a frame to hold the labels on the left
        # left_frame = tk.Frame(self.root, bg=self.data["bg_color"])  # Optional background color for visibility
        # left_frame.pack(side='left', padx=0, pady=20, anchor="nw")

        # First label
        label1 = tk.Label(self.root, text="Mode: ", bg="lightgray", padx=10, pady=5)
        label1.place(relx=.05, rely=.4)  # Place on the left side with a bit of padding

        # Second label
        label2 = tk.Label(self.root, text="Last Message Received: ", bg="lightgray", padx=10, pady=5)
        label2.place(relx=.05, rely=.5)  # Place it right below the first label with some vertical space

        return label1, label2

    def build_ip_port_text(self):
        label = tk.Label(self.root, text="Socket: 11.1.1.1.1:612941",  padx=10, pady=10)
        label.pack(side='bottom')
        return label

    def create_motor_popup(self):
        """Creates an embedded popup frame that appears inside the UI."""
        self.popup_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10, borderwidth=2, relief="ridge")

        # Labels inside the popup
        self.popup_title = tk.Label(self.popup_frame, text="Motor Details", font=("Arial", 14, "bold"), bg="lightgray")
        self.popup_speed = tk.Label(self.popup_frame, text="", bg="lightgray")
        self.popup_temp = tk.Label(self.popup_frame, text="", bg="lightgray")
        self.popup_status = tk.Label(self.popup_frame, text="", bg="lightgray")

        # Close button (alternative way to close)
        self.close_button = tk.Button(self.popup_frame, text="Close", command=self.hide_popup)

        # Pack elements inside the popup frame
        self.popup_title.pack(pady=5)
        self.popup_speed.pack()
        self.popup_temp.pack()
        self.popup_status.pack()
        self.close_button.pack(pady=5)

    def toggle_popup(self, motor_id):
        """Shows or hides the popup based on the button click."""
        if self.active_motor == motor_id:
            self.hide_popup()  # Hide if it's already open
        else:
            self.show_popup(motor_id)  # Show a new popup

    def show_popup(self, motor_id):
        """Updates and displays the popup with motor details."""
        self.popup_title.config(text=f"Motor {motor_id} Details")
        self.popup_speed.config(text=f"Speed: {100 + motor_id * 10} RPM")
        self.popup_temp.config(text=f"Temperature: {40 + motor_id}°C")
        self.popup_status.config(text=f"Status: Running")

        # Place the popup in the UI
        self.popup_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.active_motor = motor_id  # Store active motor

    def hide_popup(self):
        """Hides the popup."""
        self.popup_frame.place_forget()
        self.active_motor = None  # Reset active motor

    def create_grid(self): 
        """Creates a frame with buttons to open/hide the popup."""
        grid_frame = tk.Frame(self.root, bg=self.data["bg_color"])
        grid_frame.pack(pady=20)

        # Configure grid inside the frame
        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1)

        grid_frame.grid_rowconfigure(0, weight=1)

        # Create buttons that toggle the popup
        for i in range(3):
            button = tk.Button(grid_frame, text=f"Motor {i+1}", bg="lightblue", width=10, height=2,
                               command=lambda m=i+1: self.toggle_popup(m))
            button.grid(row=0, column=i, padx=10, pady=10)

    #Create the SD window on the right side of the UI
    def create_SD_window(self):
        self.sd_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10, borderwidth=2, relief="ridge")

        # Add labels inside the SD window
        self.sd_title = tk.Label(self.sd_frame, text="SD Information", font=("Arial", 14, "bold"), bg="lightgray")
        self.sd_xl = tk.Label(self.sd_frame, text="XL: --", bg="lightgray")
        self.sd_gy = tk.Label(self.sd_frame, text="GY: --", bg="lightgray")
        self.sd_mg = tk.Label(self.sd_frame, text="MG: --", bg="lightgray")
        self.sd_lt = tk.Label(self.sd_frame, text="LT: --", bg="lightgray")

        # Pack elements inside the SD window
        self.sd_title.pack(pady=5)
        self.sd_xl.pack(pady=5)
        self.sd_gy.pack(pady=5)
        self.sd_mg.pack(pady=5)
        self.sd_lt.pack(pady=5)


        # Place the SD window on the right side
        self.sd_frame.place(relx=0.85, rely=0.5, anchor="center")

    #Creates an emergency stop button in the bottom-left corner of the root window.
    def create_emergency_stop_button(self):
        bottom_left_button = tk.Button(self.root, text="EMERGENCY STOP MOTOR", bg="red", command=self.emergency_stop_click)
        bottom_left_button.place(relx=0.05, rely=0.95, anchor="sw", width=200, height=50)
        
        # Bind events to track the press and release
        bottom_left_button.bind("<ButtonPress-1>", self.start_emergency_stop_timer)
        bottom_left_button.bind("<ButtonRelease-1>", self.cancel_emergency_stop_timer)

        # Variable to store the timer ID
        self.timer_id = None

    def start_emergency_stop_timer(self, event):
        """Starts the timer when the button is pressed and waits for 3 seconds."""
        # Start a 3-second timer (3000 milliseconds)
        self.timer_id = self.root.after(3000, self.emergency_stop_action)

    def cancel_emergency_stop_timer(self, event):
        """Cancels the timer if the button is released before 3 seconds."""
        if self.timer_id and self.is_emergency_stopped == False:
            self.root.after_cancel(self.timer_id)  # Cancel the action if released early
            self.timer_id = None

    #Functionality of emergency stop
    def emergency_stop_click(self): ####TODO: Should add a timer to reset clicks to 0
        self.emergency_stop_clicks += 1
        self.data["error_text"] = f"Step {self.emergency_stop_clicks} emergency stop"
        if self.emergency_stop_clicks >= 3:
            self.emergency_stop_action()

    def emergency_stop_action(self):
        self.is_emergency_stopped = True
        self.data["error_text"] = f"IMPLEMENT STOP OF MOTOR"



def run_ui(shared_data):
    ui = UI(shared_data)
    ui.check_for_updates()
    ui.run()


#run HMI.py to test it without connecting it to the server
if __name__ == "__main__":
    shared_data = {
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