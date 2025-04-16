from BallSpinnerController import BallSpinnerController
from BallSpinnerController.hmi_gui_utility.scroll_frame import ScrollbarFrame
from BallSpinnerController.hmi_gui_utility.animated_graph import *
from BallSpinnerController.Motors.StepperMotor import StepperMotor
from BallSpinnerController.SmartDots.iSmartDot import iSmartDot
from BallSpinnerController.SmartDots.MetaMotion import MetaMotion
from BallSpinnerController.SmartDots.SmartDotEmulator import SmartDotEmulator
from .AuxSensors.MotorEncoder import MotorEncoder
from mbientlab.warble import BleScanner
import tkinter as tk
from tkinter import ttk
import six
import threading
import random
import queue
import asyncio
import threading
import time
import math

class HMI:
    def __init__(self, data, fullscreen=True):
        
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
        self.smartDot = None
        self.bsc = None
        self.graph_xl = None
        self.data_graphs = []
        self.motorEncodersOn = False
        self.motorEncoder1 = None

################################################### Initialize UI ###################################################\
        if fullscreen:
            self.root.attributes('-fullscreen', True)  # Set the window size to 600x300 pixels
            # Remove window decorations (title bar, borders)
            self.root.overrideredirect(True)
            # Set window size to full screen
            # Keep window on top (optional)
            self.root.attributes("-topmost", True)
            self.root.tk.call('tk', 'scaling', .91)  # 1.0 is 100% scaling


        # self.root.geometry("800x480")
        self.screen_width = 800
        self.screen_height = 480
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        #For handling the closing of the application, calls self.on_close()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after_id = 0
        
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
        self.sd_connect_window = self.create_SD_connect_window()
        self.sd_connect_toggle_button = self.toggle_SD_connect_window_button()

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
            self.sd_connect_toggle_button,
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
            self.sd_connect_window : False
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
            self.sd_connect_toggle_button,
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

    def on_close(self):
        if hasattr(self, 'after_id'):
            print("Destructor Kaboom")
            self.root.after_cancel(self.after_id)
        self.root.destroy()

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

        #Update SmartDot Data Queues
        if self.smartDot is not None: #and (self.smartDot is MetaMotion or self.smartDot is SmartDotEmulator):
            if isinstance(self.smartDot, MetaMotion):
                for i in range(len(self.data_graphs)):
                    #print(f"Gyro data {self.smartDot.data_arr[2]}")
                    self.data_graphs[i].queue.put(self.smartDot.data_arr[i])
               
            
        if self.popup_speed.cget("text") != "" and self.active_motor is not None:
            print(type(self.motorEncoder1))
            if self.motorEncodersOn and self.motorEncoder1 is not None:
                me1cData = self.motorEncoder1.readData()
                #print("Motor 1 RPM %.2f" % me1cData)
                #Send data to HMI
                self.data['motor_encoder_rpms'][0] = "%.2f " % me1cData
            rpm = float(self.popup_speed.cget("text").split(" ")[1])# != self.data['motor_encoder_rpms'][0]:
            # print(f"{type(rpm)} rpm : {rpm}")
            if rpm != self.data["motor_encoder_rpms"][0]:
                print("overwrote the rpm")
                self.popup_speed.config(text = f"Speed: {self.data['motor_encoder_rpms'][0]} RPM")
                
        self.after_id = self.root.after(self.ui_update_frequency, self.check_for_updates)

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

################################################### Local SD Connect ###################################################
    def toggle_SD_connect_window_button(self):
        btn = tk.Button(self.root, text="Local SmartDot", command = self.toggle_SD_connect_window)
        btn.place(x=650, y=230)
        return btn
    def toggle_SD_connect_window(self):
        if self.button_toggleable_elements[self.sd_connect_window] == False:
            self.sd_connect_window = self.create_SD_connect_window()
            self.button_toggleable_elements[self.sd_connect_window] = True

        else:
            self.fully_close_SD_connection()
            
    def create_SD_connect_window(self):
        x = 375
        y = 50
        
        # Create a frame inside self.frame
        frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10, borderwidth=2, relief="ridge", width = 400, height = 305)
        frame.place(x=x, y=y)
        frame.pack_propagate(False) #Don't shrink frame to content

        self.connect_sd = tk.Button(frame,text="Scan SD", command = self.handle_smart_dot_btn)
        self.connect_sd.pack(in_=frame)

        self.connect_sd_buttons = [self.connect_sd]
      
        #used to track which stage of connection we are in
        #0 means we have just clicked scan, it will get incremented to 1. if we click button again it becomes 2 
        #and the scan will see and stop
        self.sd_cmd_idx = 0
        self.sd_thread = None
        self.sd_thread2 = None
        close_btn = tk.Button(frame, text="Close SD Connection", command=self.fully_close_SD_connection)
        close_btn.pack(side="bottom", pady = 2)
        return frame
    def fully_close_SD_connection(self):
        if len(self.data_graphs) > 0:
            self.close_sd_graphs()
            print("closing graphs")
        print("closing SD window")
        self.sd_connect_window.place_forget()
        if isinstance(self.smartDot, MetaMotion) or isinstance(self.smartDot, SmartDotEmulator):
            self.smartDot.disconnect()
            print("closing SD bluetooth connection")
            self.smartDot = None
            print("emptying smartdot object")
        self.button_toggleable_elements[self.sd_connect_window] = False
    def unpack_connect_elements(self):
        for i in self.connect_sd_buttons:
            i.pack_forget()
        self.pack_connected_elements()

    def pack_connected_elements(self):
        self.sd_connected_label = tk.Label(self.sd_connect_window, text=f"Connected to {self.smartDot._MAC_ADDRESS}", font =("Arial",10))
        self.sd_connected_label.pack(in_=self.sd_connect_window)

        self.local_SD_config = self.create_local_SD_window()

    def handle_smart_dot_btn(self):
        if self.sd_thread is None:
            self.sd_thread = threading.Thread(target=self.scanAll)
            self.sd_thread.start()
        # availDevices = self.scanAll()
        self.sd_cmd_idx += 1

    def handle_SD_connect_btn(self, i):
        if self.sd_thread2 is None:
            self.sd_thread2 = threading.Thread(target=self.connect_to_chosen_SD, args=(i,))
            self.sd_thread2.start()

    def connect_to_chosen_SD(self, btn_idx):
        try:
            #self.sd_thread.join() #Complete the scanAll Thread
            print("Active threads:")
            for thread in threading.enumerate():
                print(f"  {thread.name}")
            #Jank way to grab Correct MAC Address: Creates Keys and gra
            print(f"Button index {btn_idx}")
            smartDotMAC = tuple(self.availDevicesType.keys())[btn_idx]
            smartDot = self.availDevicesType[smartDotMAC]()
            self.smartDot = MetaMotion(tuple(self.availDevices.keys())[btn_idx], is_local=True)
            smartDotConnect = self.smartDot.connect(smartDotMAC)
            self.sd_cmd_idx += 1

            self.unpack_connect_elements()
        except Exception as e:
            self.data["error_text"] = f"{e}"

    def scanAll(self):
        self.availDevices = {}
        self.availDevicesType = {}

        self.smartDot : iSmartDot = [MetaMotion(), SmartDotEmulator()]

        self.availDevices["11:11:11:11:11:11"] = "smartDotSimulator" 
        self.availDevicesType["11:11:11:11:11:11"] = SmartDotEmulator

        #self.mode = "Scanning"
        selection = -1
        #Continuously rescans for MetaWear Devices
        print("scanning for devices...")

        #Check if the Bluetooth device has ANY UUID's from any of the iSmartDot Modules
        def handler(result):
            for listedConnect in range(len(self.smartDot)):
                if result.has_service_uuid(self.smartDot[listedConnect].UUID()):
                    self.availDevices[result.mac] = result.name
                    if(isinstance(self.smartDot[listedConnect],MetaMotion)):
                            self.availDevicesType[result.mac] = MetaMotion

        BleScanner.set_handler(handler)
        BleScanner.start()
        
        try :
            i = 0
            while True: 
                #print(f"cmd idx: {self.sd_cmd_idx}")
                # #update list every 1s
                time.sleep(1.0)  
                #print all BLE devices found and append to connectable list                
                count = 0
                for address, name in six.iteritems(self.availDevices):
                    if count >= i :
                        btn = tk.Button(self.sd_connect_window, text=f"{address}",  font=("Arial", 10,), command=lambda i=i: self.handle_SD_connect_btn(i))
                        btn.pack(in_=self.sd_connect_window)
                        self.connect_sd_buttons.append(btn)
                        i += 1
                    count += 1
                if self.sd_cmd_idx > 1:
                    BleScanner.stop()
                    print("exiting the scan")
                    break# self.availDevices
        except Exception as e: #Called when KeyInterrut ^C is called
            BleScanner.stop()
            self.data["error_text"] = f"Error in scanAll {e}"
            return

    ############### Local mode SD config window ###############
    def create_local_SD_window(self):
        sd_frame = tk.Frame(self.root, bg="lightgray", padx=5, pady=5, borderwidth=2, relief="ridge")

        # Add labels inside the SD window
        self.local_sd_title = tk.Label(sd_frame, text="SD Information", font=("Arial", 14, "bold"), bg="lightgray")
        self.local_sd_xl = tk.Label(sd_frame, text="XL: --", bg="lightgray")
        self.local_sd_gy = tk.Label(sd_frame, text="GY: --", bg="lightgray")
        self.local_sd_mg = tk.Label(sd_frame, text="MG: --", bg="lightgray")
        self.local_sd_lt = tk.Label(sd_frame, text="LT: --", bg="lightgray")

        #create List of XL Rates to set
        XLSampleRates = [12.5, 25, 50, 100, 200, 400, 800, 1600] 
        GYSampleRates = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400]
        MGSampleRates = [2, 6, 8, 10, 15, 20, 25, 30]
        LTSampleRates = [.5, 1, 2, 5, 10, 20]

        #create lists of ranges
        XLRanges = [2, 4, 8, 16,]
        GYRanges = [125, 250, 500, 1000, 2000,]
        MGRanges = [2500, 4, 8, 16, 8, 16, 32, 64]
        LTRanges = [600, 1300, 8000, 16000, 32000, 64000,]
        
        lists = [XLSampleRates, XLRanges, GYSampleRates, GYRanges, MGSampleRates, MGRanges, LTSampleRates, LTRanges]
        labels = [
            "XL Sample Rates", "XL Ranges",
            "GY Sample Rates", "GY Ranges",
            "MG Sample Rates", "MG Ranges",
            "LT Sample Rates", "LT Ranges"
        ]

        self.SD_dropdowns = []
        def on_select(event):
            selected_value = event.widget.get()
            print("Selected:", selected_value)
        for i, (label_text, values) in enumerate(zip(labels, lists)):
            row = i // 2
            col = i % 2

            label = tk.Label(sd_frame, text=label_text, bg="lightgray")
            label.grid(row=row * 2, column=col, padx=10, pady=(5, 0), sticky="w")

            combo = ttk.Combobox(sd_frame, values=values, state="readonly")
            combo.current(0)
            combo.bind("<<ComboboxSelected>>", on_select)
            combo.grid(row=row * 2 + 1, column=col, padx=10, pady=(0, 10), sticky="we")

            self.SD_dropdowns.append(combo)

        sd_frame.columnconfigure(0, weight=1)
        sd_frame.columnconfigure(1, weight=1)

        submit_btn = tk.Button(sd_frame, text="Submit", command=self.submit_sd_settings)
        submit_btn.grid(row=8, column=0, columnspan=2,)

        sd_frame.pack(in_=self.sd_connect_window)
        
        return sd_frame
    def submit_sd_settings(self):
        self.SD_config_values = [combo.get() for combo in self.SD_dropdowns]
        for i in range(len(self.SD_config_values)):
            self.SD_config_values[i] = float(self.SD_config_values[i])
            self.SD_config_values[i] = math.trunc(self.SD_config_values[i])
            #print(f"type: {type(self.SD_config_values[i])}, Value: {self.SD_config_values[i]}")
        print("Submitted SD Settings:", self.SD_config_values)
        self.smartDot.setSampleRates(XL=int(self.SD_config_values[0]))
        self.smartDot.setRanges(XL=int(self.SD_config_values[1]))
        self.smartDot.setSampleRates(GY=int(self.SD_config_values[2]))
        self.smartDot.setRanges(GY=int(self.SD_config_values[3]))
        self.smartDot.setSampleRates(MG=int(self.SD_config_values[4]))
        self.smartDot.setRanges(MG=int(self.SD_config_values[5]))
        self.smartDot.setSampleRates(LT=int(self.SD_config_values[6]))
        self.smartDot.setRanges(LT=int(self.SD_config_values[7]))

        self.unpack_SD_local_config_window()
        self.SD_data_graphs = self.build_SD_data_graphs()
    def unpack_SD_local_config_window(self):
        self.local_SD_config.pack_forget()
    def pack_local_SD_labels(self, sd_frame):
         # Pack elements inside the SD window
        self.local_sd_title.pack(in_=sd_frame, pady=5)
        self.local_sd_xl.pack(in_=sd_frame, pady=5)
        self.local_sd_gy.pack(in_=sd_frame, pady=5)
        self.local_sd_mg.pack(in_=sd_frame, pady=5)
        self.local_sd_lt.pack(in_=sd_frame, pady=5)
    ############### Local mode SD GRAPHS!! ###############
    def build_SD_data_graphs(self):
        graph_frame = tk.Frame(self.root, padx=7, pady=7)
        graph_frame.pack(in_=self.sd_connect_window)

        labels = [
            ("XL", 0, 0),
            ("MG", 0, 1),
            ("GY", 1, 0),
            ("LT", 1, 1),
        ]
        data_queues = [
            Queue(),
            Queue(),
            Queue(),
            Queue()
        ]

        graph_update_speed = 45
        self.smartDot.startAccel()
        self.smartDot.startMag()
        self.smartDot.startGyro()
        self.smartDot.startLight()
        simulate_data_feed(data_queues[2])
        for i, (text, row, col) in enumerate(labels):
            # Create subframe for label + graph
            subframe = tk.Frame(graph_frame)
            subframe.grid(row=row, column=col, padx=10, pady=0)

            # Add label at top of subframe
            label = tk.Label(subframe, text=text, borderwidth=2, relief="groove", width=10)
            label.grid(row=0, column=0, pady=1)

            # Add graph below the label
            bIsForBool = True
            if i == 2 or i == 0:
                bIsForBool=False
            graph = RealTimeGraph(subframe, data_queues[i], graph_update_speed,changey=bIsForBool) 
            graph.canvas_widget.grid(row=1, column=0)
            self.data_graphs.append(graph)
        # self.graph_xl = RealTimeGraph(subframe, data_queues[0], graph_update_speed) 
        # self.graph_xl.canvas_widget.grid(row=1, column=0)
        # self.data_graphs.append(self.graph_xl)
        # self.sd_graph_close_btn = tk.Button(graph_frame, text="Close Graphs", command = self.close_sd_graphs)
        # self.sd_graph_close_btn.grid(row=2, column=0, columnspan=2,)
        return graph_frame
    def close_sd_graphs(self):
        self.smartDot.stopAccel()
        self.smartDot.stopMag()
        self.smartDot.stopGyro()
        self.smartDot.stopLight()
        self.SD_data_graphs.pack_forget()

        for i in self.data_graphs:
            i.canvas_widget.destroy()
            
        self.data_graphs.clear()

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
        self.selected_motor = tk.Label(mc_frame, bg="lightgray", text=f"Hit Motor 1 Btn", font=("Arial", 12,))
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
            #Make motor encoder object when we activate our motor
            try:
                self.motorEncoder1 = MotorEncoder()
                self.motorEncodersOn = True
            except Exception as e:  # Assumed Exception is caused from broken pipe, can look into another time
                    print(f"Error When attempting to set up Motor Encoder: {e}")      

        increment = self.motor_button_text_list[btn_idx]
        if btn_idx > 2:
            increment = int(increment.split("+")[1])
        else:
            increment = int(increment)
        if self.motor.rpm + increment > 0:
            self.motor.changeSpeed(self.motor.rpm + increment)
            print(f"Changing motor speed by: {increment}")
            print(f"Motor speed should now be: {self.motor.rpm}")

        else:
            print("cant set motor rpm below 0")
        self.update_motor_controller_text()

################################################### Motor Data popup ###################################################
    def create_motor_popup(self):
        """Creates an embedded popup frame that appears inside the UI."""
        popup_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10, borderwidth=2, relief="ridge")

        # Labels inside the popup
        self.popup_title = tk.Label(popup_frame, text="Motor Details", font=("Arial", 14, "bold"), bg="lightgray")
        self.popup_current = tk.Label(popup_frame, text="", bg="lightgray")
        self.popup_speed = tk.Label(popup_frame, text="", bg="lightgray")
        self.popup_status = tk.Label(popup_frame, text="", bg="lightgray")

        # Close button (alternative way to close)
        self.close_button = tk.Button(popup_frame, text="Close", command=self.hide_popup)

        # Pack elements inside the popup frame
        self.popup_title.pack(in_=popup_frame,pady=5)
        self.popup_speed.pack(in_=popup_frame,)
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
            button = tk.Button(grid_frame, text=f"Motor {i+1}", bg="gray60", width=10, height=2,
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
        self.data["estop"] = True
        self.motor.turnOffMotor()
        del self.motor
        self.motor = StepperMotor(GPIOPin=12)
        self.motor.turnOnMotor(0)
        print("Emergency Stopped Motor")

    def close_window(self):
        self.on_close()

        # Set the error text and update the error label

    #TODO: function for back button from main local or bsc screen    
    # Hide necessary UI elements. 
    # If back to Mode selection screen:     Close server connection if open     
    def stop_bsc(self):
        self.data["close_bsc"] = True
        
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
        self.local_ui_elements_to_hide = {self.local_mode_button, self.bsc_button, }
        self.change_page(self.local_ui_elements_to_show, self.local_ui_elements_to_hide)
        self.motor =  StepperMotor(GPIOPin=12)
        self.stop_bsc()





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
            "bg_color": 'red',
            "geometry": "600x300",  # Set the window size to 600x300 pixels
            "title": "Ball Spinner Controller GUI",
            "error_text": "",
            "i": 0
        }

    run_ui(shared_data)