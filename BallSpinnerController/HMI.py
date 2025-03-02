import tkinter as tk

class UI:
    def __init__(self, data):
        self.data = data
        self.ui_update_frequency = 200  # Update the UI every 200 milliseconds
        self.root = tk.Tk()
        self.root.geometry("600x300")  # Set the window size to 600x300 pixels
        self.root.title("Ball Spinner Controller GUI")
        self.root.configure(bg=data["bg_color"])  # Set the background color of the window

        # Build the UI components
        self.title_label = self.build_title_label()
        self.e_frame, self.e_label = self.build_error_box()
        self.close_button = self.build_close_button()


    def run(self):
        self.root.mainloop()

    def check_for_updates(self):
        if self.data["error_text"] != self.e_label.cget("text"):
            self.set_error_text(self.data["error_text"])#f"Error message here {self.error_text}")
        # if self.data["xy"] != self.xy_label.cget("text"):
        #     self.set_xy_text()

        self.root.after(self.ui_update_frequency, self.check_for_updates)  # Check every 1000 milliseconds (1 second)

    def close_window(self):
        self.root.destroy()
        # Set the error text and update the error label

    def set_error_text(self,txt):
        self.e_label.config(text=f"Error: {txt}")

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

def run_ui(shared_data):
    
    ui = UI(shared_data)
    ui.check_for_updates()
    ui.run()

if __name__ == "__main__":
    self.shared_data = {
            "ip": "",
            "port": "",
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
            "error_text": "aaa",
            "i": 0
        }

    run_ui(shared_data)