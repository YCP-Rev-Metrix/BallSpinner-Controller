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

        # Build the UI components
        self.title_label = self.build_title_label()
        self.e_frame, self.e_label = self.build_error_box()
        self.close_button = self.build_close_button()
        self.ip_label = self.build_ip_port_text()



    def run(self):
        self.root.mainloop()

    #This is our loop for updating data within the HMI. It checks for changes in the shared dictionary that both the BSC and HMI have.
    def check_for_updates(self):
        if self.data["error_text"] != self.e_label.cget("text"):
            self.e_label.config(text=self.data["error_text"])
        if self.data["ip"] != self.ip_label.cget("text"):
            self.ip_label.config(text=self.data["ip"])

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
        close_button.pack(side='bottom')
        return close_button

    def build_mode_text_box(self):
        label = tk.Label(self.root, text="")
    
    def build_ip_port_text(self):
        label = tk.Label(self.root, text="11.1.1.1.1:612941")
        label.pack(side='bottom')
        return label


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
            "last_message": "",
            "bg_color": 'dodgerblue2',
            "geometry": "600x300",  # Set the window size to 600x300 pixels
            "title": "Ball Spinner Controller GUI",
            "configure": 'dodgerblue2',  # Set the background color of the window
            "error_text": "",
            "i": 0
        }

    run_ui(shared_data)