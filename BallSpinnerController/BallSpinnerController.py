import asyncio
import random
import os
import threading
import subprocess
from mbientlab.warble import BleScanner
import six
from .MetaMotion import MetaMotion
from .SmartDotEmulator import SmartDotEmulator
from .iSmartDot import iSmartDot
from .Motor import Motor
import socket
import struct
import sys
from time import sleep
from enum import Enum
from.Protocol import *
from .HMI import HMI
# class syntax
class BSCModes(Enum):
    STARTUP = 0

    #Controller not Connected to Application
    WAITING_FOR_APP_INITILIZATION  = 1

    #Controller Connected to Application Waiting for Next Message Signal
    IDLE = 2
    
    #Currently Scannning For Bluetooth Modules
    BLUETOOTH_SCANNING = 3

    #Connected to SmartDot module  
    READY_FOR_INSTRUCTIONS = 4

    #Currently in process of Taking Data from all connected device
    TAKING_SHOT_DATA = 5
    
class BallSpinnerController():

    def __init__(self, shared_data, debug="0", name="Ball Spinner Controller"):
        #Before Anything, Check if user has raised permissions
        try:
            #Manually Raise Permissiosn, if Possible
            subprocess.check_call(['sudo', '-n', 'true'])
        
        except subprocess.CalledProcessError: #If not possible to run with admin permissions, 
            raise PermissionError("Application Must Be Ran with Raised Permissions")

        self.debug = (True if debug == "1" else False)
        
        #determine global ip address
        self.iSmartDot = None
        self.scanner = None

        #Create shared dictionary for HMI(GUI)
        self.shared_data = shared_data
    
        print("Debug Mode: ON") if self.debug else None 
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                self.server = s
                s.connect(("8.8.8.8", 80))
                ipAddr = s.getsockname()[0]
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



        except Exception:
            # ERROR: Not Connected to Internet
            pass 
        

        while(True):
            try:
                # self.launchHMI()
                self.socketHandler(ipAddr)
            except BrokenPipeError:
                pass

    #Intended to launch the HMI and add it to the asyncio execution as a simulated thread
    # def launchHMI(self):
    #     print("Attempting to laucnh HMI")
    #     if os.environ.get("DISPLAY") is None:
    #         print("No display detected. Running without GUI.")
    #     else:
    #         self.hmi = UI(self.shared_data)
    #         self.hmi.check_for_updates()
    #         self.hmi.run()
    def stop_server(self):
        print("########## Shutting down the BSC socket ##########")
        self.server.shutdown(socket.SHUT_RDWR)
        print("########## Closing the BSC server ##########")
        self.server.close()
    def check_shared_data(self, data):
        print("checking shared data ##########")
        if data["close_bsc"] is True:
            self.stop_server()
    def socketHandler(self, ipAddr):    
        while(True): #loop re-opening socket if crashes
           
            self.mode = BSCModes.WAITING_FOR_APP_INITILIZATION
            #initiate Port to 8411
            self.commsPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.commsPort.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_address = (ipAddr, 8411)  # Replace 'localhost' with the server's IP if needed
            self.shared_data["ip"] = f"Socket: {ipAddr}:{8411}"
            print('Server listening on {}:{}'.format(*server_address))
            self.commsPort.bind(server_address)

            #wait for a device to attempt TCP connection to Port
            self.commsPort.listen(1)
            self.commsChannel, clientIp  = self.commsPort.accept()
            self.commsChannel.setblocking(True)
            try:
                asyncio.run(self.commsHandler()) 

            except OSError: #Raised if Comms is forcibly closed while waiting for message
                print("Socket Closed, must restart")   
                self.commsChannel.close()
                self.commsPort.close()
            except KeyboardInterrupt:
                #When user presses cancel, attempt to close ports properly
                print("Crashed by User")
                self.commsChannel.close()
                self.commsPort.close()
                exit(0)
            except BrokenPipeError:
                print("Socket Closed Ubruptly, must restart")
                pass
    
    async def smartDotHandler(self):
        print("Handling SmartDot:")
        def accelDataSignal(dataBytes : bytearray):
            bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                                    0x00, 0x13, 0x41]) # Send Sensor Data for XL  
            bytesData.extend(dataBytes)
            try:
                self.commsChannel.sendall(bytesData)
            except Exception:  # Assumed Exception is caused from broken pipe, can look into another time
                self.smartDot.stopAccel()

        def magDataSignal(dataBytes : bytearray):
            bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                                    0x00, 0x13, 0x4D]) # Send B_A_SD_SENSOR_DATA for MG
            bytesData.extend(dataBytes)
            try:
                self.commsChannel.sendall(bytesData)
            except Exception:  # Assumed Exception is caused from broken pipe, can look into another time
                self.smartDot.stopMag()
        
        def gyroDataSignal(dataBytes : bytearray):
            bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                                    0x00, 0x13, 0x47]) # Send B_A_SD_SENSOR_DATA for XL
            bytesData.extend(dataBytes)
            try:
                self.commsChannel.sendall(bytesData)
            except Exception: # Assumed Exception is caused from broken pipe, can look into another time
               self.smartDot.stopGyro()

        def lightDataSignal(dataBytes : bytearray):
            bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                                    0x00, 0x13, 0x4C])
            bytesData.extend(dataBytes)
            #Add 0's to "Y and Z values"
            bytesData.extend(b'\x00\x00\x00\x00\x00\x00\x00\x00')
            try:
                self.commsChannel.sendall(bytesData)
            except Exception as e:  # Assumed Exception is caused from broken pipe, can look into another time
                print(f"Error Occured Somewhere in BSC: {e}")
                self.smartDot.stopLight()
            
        self.smartDot.setDataSignals(accelDataSig=accelDataSignal, magDataSig=magDataSignal, gyroDataSig=gyroDataSignal, lightDataSig=lightDataSignal)
        #Instantly Setting the Start Configs for the 9DOF's to skip implementation

        self.smartDot.startMag()
        self.smartDot.startAccel()
        self.smartDot.startGyro() 
        self.smartDot.startLight()      
        print("All started")
        try:
            await self.wait_for_completion()
        except Exception as e:
            print(e)
        print("Handler Done")

    async def wait_for_completion(self):
        print("Keeping SmartdotHandler up")
        try:
            await asyncio.sleep(9999)  
        except Exception as e:
            print(e)

    async def commsHandler(self):
            loop = asyncio.get_event_loop()
            while True:
                
            #Read first message com
                try:
                    data = await loop.run_in_executor(None, self.commsChannel.recv, 1024)
                    #parse message
                    if not data == b'':
                        print("Received: %s" % data.hex())  if self.debug else None
                        #Pass the last message to the HMI
                        # message_type = MsgType(data[0])
                        # if message_type is not None:
                        self.shared_data["message_type"] = MsgType.name_from_value(data[0])
                        
                        match data[0]: 
                            #shared_data["message_type"] =
                            #shared_data["message_type"] = message_enum.name
                            case(MsgType.A_B_INIT_HANDSHAKE): #A_B_INIT_HANDSHAKE 
                                #Message Received: | Msg Type: 0x01 | Msg Size: 0x0001 | RandomByte: XXXX 
                                print("Received: APP_INIT Message") if self.debug else None
                                if self.mode != BSCModes.WAITING_FOR_APP_INITILIZATION:
                                    #Send Error: Already Connected to Application

                                    #Reset
                                    pass
                                else:                   
                                    print("Sending: APP_INIT_ACK Message") if self.debug else None
                                    #Grab Random Byte from third and resend
                                    bytesData = bytearray([MsgType.B_A_INIT_HANDSHAKE_ACK, 0x00, 0x01, data[3]]) # Send B_A_INIT_HANDSHAKE_ACK
                                    self.commsChannel.send(bytesData)
                                    self.mode = BSCModes.IDLE

                            case(MsgType.A_B_NAME_REQ): #A_B_NAME_REQ Message
                                print("Looking For Pi")
                                name : str = "Ball Spinner Controller"
                                bytesData =bytearray([MsgType.B_A_NAME, 0x00, name.__len__()]) # Send B_A_NAME
                                bytesData.extend(name.encode("utf-8"))
                                print(bytes(bytesData))
                                self.commsChannel.send(bytesData)
                                self.mode = BSCModes.IDLE
                                pass
                            
                            case(MsgType.A_B_START_SCAN_FOR_SD): #A_B_START_SCAN_FOR_SD Message
                                #If the 
                                self.mode = BSCModes.BLUETOOTH_SCANNING
                                
                                #Confirm only one Scanner is open
                                if self.scanner == None:
                                    self.scanner = asyncio.create_task(self.tCPscanAll(self.debug))

                            case(MsgType.A_B_CHOSEN_SD): #A_B_CHOSEN_SD Message
                                try:
                                    print(self.scanner.cancel())
                                except Exception as e:
                                    print(e)

                                self.smartDot : iSmartDot = None
                                
                                #Save MAC Address as String
                                smartDotMACStr = "%s:%s:%s:%s:%s:%s" % (data[3:4].hex(), 
                                data[4:5].hex(), data[5:6].hex(), data[6:7].hex(), data[7:8].hex(), 
                                data[8:9].hex())  
                                smartDotMACStr= smartDotMACStr.upper()  
                                print(self.availDevicesType)
                                print(smartDotMACStr)
                                try: #if not in debug mode and application sends SMARTDOTEMULATOR String, 
                                    self.smartDot = self.availDevicesType[smartDotMACStr]
                                    #delete rest of SD instances
                                except KeyError:
                                    #The Application sent an unscanned MAC Address
                                    print("The Application Sent Device to Connect To Was Not a Valid MAC Address")
                                    break
                                    #This needs to be changed to have an error
                                print("Connecting to "+ smartDotMACStr)

                                #Check if connection was successful
                                if self.smartDot.connect(smartDotMACStr):   
                                    bytesData = bytearray([0x08, 0x00, 0x08]) #send B_A_RECEIVE_CONFIG_INFO
                                    print("sending bytesData")
                                    #bytesData.extend(data[3:9]) 
                                    #determine rate and ranges
                                    bytesData.extend(bitMappings.sendConfigSettings(self.smartDot.XL_availSampleRate, self.smartDot.XL_availRange,
                                                                                    self.smartDot.GY_availSampleRate, self.smartDot.GY_availRange,
                                                                                    self.smartDot.MG_availSampleRate, self.smartDot.MG_availRange,
                                                                                    self.smartDot.LT_availSampleRate, self.smartDot.LT_availRange))
                                    self.commsChannel.send(bytesData)
                                    self.mode = BSCModes.READY_FOR_INSTRUCTIONS
                                else:
                                    self.smartDot = None
                                    #NEED TO CHECK IF NOT TRUE, SEND ERROR
                            
                            case(MsgType.A_B_RECEIVE_CONFIG_INFO): #A_B_RECEIVE_CONFIG_INFO
                                print(data.hex())
                                XLConfigSampleRate = data[3] >> 4 # Parse XL Bytes
                                GYConfigSampleRate = data[4] >> 4 # Parse GY Bytes
                                MGConfigSampleRate = data[5] >> 4 # Parse MG Bytes
                                LTConfigSampleRate = data[6] >> 4 # Parse LT Bytes
                                
                                print(LTConfigSampleRate)
                                #create List of XL Rates to set
                                XLSampleRates = [12.5, 25, 50, 100, 200, 400, 800, 1600] 
                                GYSampleRates = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400]
                                MGSampleRates = [2, 6, 8, 10, 15, 20, 25, 30]
                                LTSampleRates = [.5, 1, 2, 5, 10, 20]

                                self.smartDot.setSampleRates(XL = XLSampleRates[XLConfigSampleRate],
                                                             GY = GYSampleRates[GYConfigSampleRate],
                                                             MG = MGSampleRates[MGConfigSampleRate],
                                                             LT = LTSampleRates[LTConfigSampleRate])
                                
                            case(MsgType.A_B_MOTOR_INSTRUCTIONS): #MOTOR_INSTRUCTIONS Message
                                #print("Received Motor Instruction")
                                if self.mode == BSCModes.READY_FOR_INSTRUCTIONS: 
                                    print("Initializing Sensors")
                                    print(data)
                                
                                    try:          
                                        self.smartDotHandlerThread = asyncio.create_task(self.smartDotHandler())    
                                    except BrokenPipeError:
                                        raise BrokenPipeError
                                    except Exception as e:
                                        print("Unable to start thread")
                                        print(e)
                                    
                                    # First Motor Instruction:         
                                    #Turn On Motors
                                    print("Turning on motors")
                                    self.PrimMotor = Motor(22)
                                    self.secMotor1 = Motor(38)
                                    self.secMotor2 = Motor(35)                

                                    self.PrimMotor.turnOnMotor(0)
                                    self.secMotor1.turnOnMotor(0)
                                    self.secMotor2.turnOnMotor(0)

                                    self.mode = BSCModes.TAKING_SHOT_DATA
                                
                                self.PrimMotor.changeSpeed(int(data[3])) 
                                self.secMotor1.changeSpeed(int(data[4])) 
                                self.secMotor2.changeSpeed(int(data[5]))

                            case(MsgType.A_B_STOP_MOTOR): #STOP_MOTOR_INSTRUCTIONS
                                
                                    print("Received Stop Function")
                                    #Stop Motors

                                    self.PrimMotor.turnOffMotor()
                                    self.secMotor1.turnOffMotor()
                                    self.secMotor2.turnOffMotor()
                                    
                                    del self.PrimMotor
                                    del self.secMotor1
                                    del self.secMotor2
   
                                    #Stop SmartDot Data Collection
                                    self.smartDot.stopAccel()
                                    self.smartDot.stopGyro()
                                    self.smartDot.stopMag()
                                    self.smartDot.stopLight()
                                    self.mode = BSCModes.READY_FOR_INSTRUCTIONS
                                    self.smartDotHandlerThread.cancel()

                            case(MsgType.A_B_DISCONNECT_FROM_BSC):
                                #Raise the BokenPipeError, as the Communication Line is disconnected
                                raise BrokenPipeError
                except BrokenPipeError:
                    print("Pipe Error Caught in CommsHandler")
                    raise BrokenPipeError
                except Exception as e:
                    print(f"Error Occured Somewhere in BSC: {e}")
                    print("Restarting Pipe")
                    raise BrokenPipeError
                #Try reading the dictionary here and acting on a change to maybe the stop_BSC value
                # print(self.shared_data["close_bsc"]) 
                # shared_data["close_bsc"] is True    

            


    async def tCPscanAll(self, debugMode):
        #Stores {MAC ADDRESS : NAME}
        self.availDevices = {}
        
        #Save the Class that each SmartDot is Associated with
        self.availDevicesType = {}
        smartDot : iSmartDot = [MetaMotion(), SmartDotEmulator()]

        #Continuously rescans for MetaWear Devices
        print("scanning for devices...")

        #Check if the Bluetooth device has ANY UUID's from any of the iSmartDot Modules
        def handler(result):
            for smartDotClass in range(len(smartDot)):
                if result.has_service_uuid(smartDot[smartDotClass].UUID()):
                    self.availDevices[result.mac] = result.name
                    self.availDevicesType[result.mac] = smartDot[smartDotClass]

        if(debugMode):
            #Debug is on, manually add SmartDotEmulator to scanned devices
            self.availDevices["11:11:11:11:11:11"] = "smartDotSimulator" 
            self.availDevicesType["11:11:11:11:11:11"] = smartDot[1]
        
        bleScannerRunning = True
        BleScanner.set_handler(handler)
        BleScanner.start(scan_type='active')
        
        try :
            i = 0
            while True: 
                #update list every 5s
                try:
                    await asyncio.sleep(1.0)  
                except asyncio.CancelledError:
                    break

                #print all BLE devices found and append to connectable list                
                count = 0
                for address, name in six.iteritems(self.availDevices):
                    name : str
                    address = address.replace(":", "")

                    #Pack Message So Lenght fits in 2 bytes
                    messLen = struct.pack(">I", (6 + name.__len__()))[2:4]
                    bytesData = bytearray([MsgType.B_A_SCANNED_SD])
                    bytesData.extend(messLen) 
                    bytesData.extend(bytearray([                    
                                        int(address[0:2],16),
                                        int(address[2:4],16),
                                        int(address[4:6],16),
                                        int(address[6:8],16),
                                        int(address[8:10],16),
                                        int(address[10:12],16)]))
                                        
                    bytesData.extend(name.encode("utf-8"))
                    self.commsChannel.send(bytesData)
                    
                

        except asyncio.CancelledError: #Called when BLE Thread is stopped
            pass

        except BrokenPipeError: #If Comms Crash while Scanning
            pass

        finally:
            if bleScannerRunning: 
                BleScanner.stop()
                bleScannerRunning = False

#Scans all modules to see which to connect to
async def scanAll() -> dict:
    
    availDevices = {}
    ismartDotSubClasses : iSmartDot = [MetaMotion(), SmartDotEmulator()]

    #self.mode = "Scanning"
    selection = -1
    #Continuously rescans for MetaWear Devices
    print("scanning for devices...")

    #Check if the Bluetooth device has ANY UUID's from any of the iSmartDot Modules
    def handler(result):
        for listedConnect in range(len(ismartDotSubClasses)):
            if result.has_service_uuid(ismartDotSubClasses[listedConnect].UUID()):
                availDevices[result.mac] = result.name

    BleScanner.set_handler(handler)
    BleScanner.start()
    
    try :
        i = 0
        while True: 
            #update list every 5s
            await asyncio.sleep(1.0)  

            #print all BLE devices found and append to connectable list                
            count = 0
            for address, name in six.iteritems(availDevices):
                if count >= i :
                    print("[%d] %s (%s)" % (i, address, name))
                    i += 1
                count += 1

    except : #Called when KeyInterrut ^C is called
        BleScanner.stop()
        return availDevices

#BallSpinnerController()
