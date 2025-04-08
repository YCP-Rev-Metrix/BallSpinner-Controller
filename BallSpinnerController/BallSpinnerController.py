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
from .StepperMotor import StepperMotor
from .AuxSensors import iAuxSensor
from .AuxSensors.CurrentSensors import CurrentSensor
import socket
import struct
import sys
from time import sleep
from enum import Enum
from.Protocol import *
from .HMI import HMI
import queue

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
        self.data = shared_data
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
        asyncio.run(self.socketHandler(ipAddr))
        ''''
        while(True):
            try:
                # self.launchHMI()
                self.socketHandler(ipAddr)
            except BrokenPipeError:
                pass
        '''
    #async def launchTasks(self): #figure out a better name later, I hate the idea of it being called main tho
        pass
    
    def stop_server(self):
        print("########## Shutting down the BSC socket ##########")
        self.server.shutdown(socket.SHUT_RDWR)
        print("########## Closing the BSC server ##########")
        self.server.close()
        #TODO Correctly shut down server, send an error message to BSA too.
        #B_A_BSC_SHUTDOWN_BY_HMI
        
    async def check_shared_data(self, data):
        while True:
            #print("########## HMI Communication Occurring ##########")
            if data["close_bsc"] is True:
                self.stop_server()
            if data["estop"] is True:
                if self.PrimMotor is not None:# and self.secMotor1 and self.secMotor2:
                    self.PrimMotor.turnOffMotor()
                    self.secMotor1.turnOffMotor()
                    self.secMotor2.turnOffMotor()   
                data["estop"] = False
            await asyncio.sleep(1)
    
    async def socketHandler(self, ipAddr):    
        while(True): #loop re-opening socket if crashes

        
            #turn on Sensors
            try:
                self.motorCurrentSensor1 = CurrentSensor(ADC_IN=0)
                self.motorCurrentSensor2 = CurrentSensor(ADC_IN=1)
                self.motorCurrentSensor3 = CurrentSensor(ADC_IN=2)
                self.currentSenorsOn = True
                print("Sensors Turned on")
            except ValueError:
                self.data['error_text'] = "I2C Not Detected, please Check Wifi"
                currentSenorsOn = False

            self.mode = BSCModes.WAITING_FOR_APP_INITILIZATION
            #initiate Port to 8411
            self.commsPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.commsPort.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_address = (ipAddr, 8411)  # Replace 'localhost' with the server's IP if needed

            #Set the socket information in the HMI
            self.data["ip"] = f"Socket: {ipAddr}:{8411}"

            print('Server listening on {}:{}'.format(*server_address))
            self.commsPort.bind(server_address)
          
            #wait for a device to attempt TCP connection to Port
            self.commsPort.listen(1)
            self.commsChannel, clientIp  = self.commsPort.accept()
            self.commsChannel.setblocking(True)
            try:
                #Start up all Tasks PROPERLY (Your welcome Brandon)
                self.startScanner = asyncio.Event()
                self.startSmartDotHandler = asyncio.Event() 

                await asyncio.gather(
                    self.tCPscanAll(self.debug),
                    self.commsHandler(),
                    self.smartDotHandler(),
                    self.check_shared_data(self.data),
                    self.sensorHandler()
                )
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
        while True: # Allow for thread to loop when repeated Start

            #Wait until Motor Instructions are first sent

            await self.startSmartDotHandler.wait()
            print("Handling SmartDot:")
            def accelDataSignal(dataBytes : bytearray):
                bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                                        0x00, 0x13, 0x41]) # Send Sensor Data for XL  
                bytesData.extend(dataBytes)
                try:
                    self.commsChannel.sendall(bytesData)
                    #TODO:  This will likely flood. Create some sort of timer or limit on printing this to protocol history
                    #p_msg = MsgType.name_from_value(bytesData[0])
                    #self.data["message_type"] = p_msg
                    #self.data["protocol_queue"].put(p_msg)
             
                except Exception:  # Assumed Exception is caused from broken pipe, can look into another time
                    self.smartDot.stopAccel()

            def magDataSignal(dataBytes : bytearray):
                bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                                        0x00, 0x13, 0x4D]) # Send B_A_SD_SENSOR_DATA for MG
                bytesData.extend(dataBytes)
                try:
                    self.commsChannel.sendall(bytesData)
                    print("Sending Mag")
                    #TODO:  This will likely flood. Create some sort of timer or limit on printing this to protocol history
                    #p_msg = MsgType.name_from_value(bytesData[0])
                    #self.data["message_type"] = p_msg
                    #self.data["protocol_queue"].put(p_msg)
             
                except Exception:  # Assumed Exception is caused from broken pipe, can look into another time
                    self.smartDot.stopMag()
            
            def gyroDataSignal(dataBytes : bytearray):
                bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                                        0x00, 0x13, 0x47]) # Send B_A_SD_SENSOR_DATA for XL
                bytesData.extend(dataBytes)
                try:
                    self.commsChannel.sendall(bytesData)
                    #TODO:  This will likely flood. Create some sort of timer or limit on printing this to protocol history
                    #p_msg = MsgType.name_from_value(bytesData[0])
                    #self.data["message_type"] = p_msg
                    #self.data["protocol_queue"].put(p_msg)
             
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
                    #TODO:  This will likely flood. Create some sort of timer or limit on printing this to protocol history
                    #p_msg = MsgType.name_from_value(bytesData[0])
                    #self.data["message_type"] = p_msg
                    #self.data["protocol_queue"].put(p_msg)
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
            while self.startSmartDotHandler.is_set():
                #Continuously check if SmartDotHandler should be open
                await asyncio.sleep(1)
        
    async def commsHandler(self):
            loop = asyncio.get_event_loop()

            while True:
                
            #Read first message com
                try:
                    data = await loop.run_in_executor(None, self.commsChannel.recv, 1024)
                    #parse message
        
                    print("Received: %s" % data.hex())  if self.debug else None
                    #Pass the last message to the HMI
                    p_msg = MsgType.name_from_value(data[0])
                    self.data["message_type"] = p_msg
                    self.data["protocol_queue"].put(p_msg)
                    
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
                                p_msg = MsgType.name_from_value(bytesData[0])
                                self.data["message_type"] = p_msg
                                self.data["protocol_queue"].put(p_msg)
                                self.commsChannel.send(bytesData)
                                self.mode = BSCModes.IDLE

                        case(MsgType.A_B_NAME_REQ): #A_B_NAME_REQ Message
                            print("Looking For Pi")
                            name : str = "Ball Spinner Controller"
                            bytesData =bytearray([MsgType.B_A_NAME, 0x00, name.__len__()]) # Send B_A_NAME
                            bytesData.extend(name.encode("utf-8"))
                            print(bytes(bytesData))
                            p_msg = MsgType.name_from_value(bytesData[0])
                            self.data["message_type"] = p_msg
                            self.data["protocol_queue"].put(p_msg)
                            self.commsChannel.send(bytesData)
                            self.mode = BSCModes.IDLE
                            pass
                        
                        case(MsgType.A_B_START_SCAN_FOR_SD): #A_B_START_SCAN_FOR_SD Message
                            #There is a bug on the Application that on connection 2 Start Scans are being sent
                            #Confirm only one Scanner is open
                            if self.mode != BSCModes.BLUETOOTH_SCANNING:
                                #Unlock tcpScanAll()
                                self.startScanner.set()
                                #self.scanner = asyncio.create_task(self.tCPscanAll(self.debug))
                                self.mode = BSCModes.BLUETOOTH_SCANNING

                        case(MsgType.A_B_CHOSEN_SD): #A_B_CHOSEN_SD Message
                            try:
                                #Stops Scanner
                                print("Stopping Scaner")
                                self.startScanner.clear()
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
                                #Set Sample Rates and Ranges on HMI
                                #TODO: Rename dictionary list 
                                #set default Sample Rates and Ranges
                                
                                defaultXLSampleRate = 100
                                defaultGYSampleRate = 100
                                defaultMGSampleRate = 10
                                defaultLTSampleRate = .5

                                self.smartDot.setSampleRates(XL=100, GY=100, MG=10, LT=.5)
                                
                                self.data["sample_rates"][0] = f"{defaultXLSampleRate}Hz, 2g" #Hardcoded unitl the Pass Ranges values work
                                self.data["sample_rates"][1] = f"{defaultGYSampleRate}Hz, 125dps"
                                self.data["sample_rates"][2] = f"{defaultMGSampleRate}Hz, 1000/2000 μT"
                                self.data["sample_rates"][3] = f"{defaultLTSampleRate}Hz, 600 Lux"

                                #determine rate and ranges
                                bytesData.extend(bitMappings.sendConfigSettings(self.smartDot.XL_availSampleRate, self.smartDot.XL_availRange,
                                                                                self.smartDot.GY_availSampleRate, self.smartDot.GY_availRange,
                                                                                self.smartDot.MG_availSampleRate, self.smartDot.MG_availRange,
                                                                                self.smartDot.LT_availSampleRate, self.smartDot.LT_availRange))
                                self.commsChannel.send(bytesData)
                                p_msg = MsgType.name_from_value(bytesData[0])
                                self.data["message_type"] = p_msg
                                self.data["protocol_queue"].put(p_msg)
                                self.mode = BSCModes.READY_FOR_INSTRUCTIONS
                            else:
                                self.smartDot = None
                                self.data['error_text'] = "Unable To Connect To SmartDot, Please Restart"
                                #NEED TO CHECK IF NOT TRUE, SEND ERROR
                        
                        case(MsgType.A_B_RECEIVE_CONFIG_INFO): #A_B_RECEIVE_CONFIG_INFO
                            XLConfigSampleRate = data[3] >> 4 # Parse XL Bytes
                            XLConfigRange = data[3] & 0x0F #Bitwise AND with (00001111)
                            GYConfigSampleRate = data[4] >> 4 # Parse GY Bytes
                            GYConfigRange = data[4] & 0x0F
                            MGConfigSampleRate = data[5] >> 4 # Parse MG Bytes
                            MGConfigRange = data[5] & 0x0F
                            LTConfigSampleRate = data[6] >> 4 # Parse LT Bytes
                            LTConfigRange = data[6] & 0x0F

                            #create List of XL Rates to set
                            XLSampleRates = [12.5, 25, 50, 100, 200, 400, 800, 1600] 
                            GYSampleRates = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400]
                            MGSampleRates = [2, 6, 8, 10, 15, 20, 25, 30]
                            LTSampleRates = [.5, 1, 2, 5, 10, 20]

                            #create lists of ranges
                            XLRanges = [2, 4, 8, 16, -1, -1, -1, -1]
                            GYRanges = [125, 250, 500, 1000, 2000, -1, -1, -1]
                            MGRanges = [2500, 4, 8, 16, 8, 16, 32, 64]
                            LTRanges = [600, 1300, 8000, 16000, 32000, 64000, -1, -1]

                            self.smartDot.setSampleRates(XL = XLSampleRates[XLConfigSampleRate],
                                                            GY = GYSampleRates[GYConfigSampleRate],
                                                            MG = MGSampleRates[MGConfigSampleRate],
                                                            LT = LTSampleRates[LTConfigSampleRate])

                            self.smartDot.setRanges(XL = XLRanges[XLConfigRange],
                                                        GY = GYRanges[GYConfigRange],
                                                        MG = MGRanges[MGConfigRange],
                                                        LT = LTRanges[LTConfigRange])

                            #This is actually rate and ranges
                            #TODO: Rename dictionary list 
                            self.data["sample_rates"][0] = f"{XLSampleRates[XLConfigSampleRate]}Hz, {XLRanges[XLConfigRange]}g"
                            self.data["sample_rates"][1] = f"{GYSampleRates[GYConfigSampleRate]}Hz, {GYRanges[GYConfigRange]}dps"
                            self.data["sample_rates"][2] = f"{MGSampleRates[MGConfigSampleRate]}Hz, {MGRanges[MGConfigRange]}μT"
                            self.data["sample_rates"][3] = f"{LTSampleRates[LTConfigSampleRate]}Hz, {LTRanges[LTConfigRange]}Lux"
                            
                            
                        case(MsgType.A_B_MOTOR_INSTRUCTIONS): #MOTOR_INSTRUCTIONS Message
                            #print("Received Motor Instruction")
                            if self.mode == BSCModes.READY_FOR_INSTRUCTIONS: 
                                print("Initializing Sensors")
                                print(data)
                            
                                self.startSmartDotHandler.set()
                                 

                                # First Motor Instruction:         
                                #Turn On Motors
                                print("Turning on motors")
                                #I asked for a number between 1 and 20
                                self.PrimMotor = StepperMotor(12) 
                                print("PrimMotor Turned On")
                                self.secMotor1 = StepperMotor(23)
                                self.secMotor2 = StepperMotor(24)                

                                self.PrimMotor.turnOnMotor()
                                self.secMotor1.turnOnMotor()
                                self.secMotor2.turnOnMotor()

                                
                                self.mode = BSCModes.TAKING_SHOT_DATA

                                
   
                            
                            #primMotorSpeed = int(data[3])
                            primMotorSpeed = struct.unpack('<f', data[3:7])[0]
                            self.PrimMotor.changeSpeed(primMotorSpeed) 
                            print("Prim Motor Instruction: %f" % primMotorSpeed)
                            
              
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
                                

                                print("Stopping Auxillary Sensors")
                                
                                del self.motorCurrentSensor1
                                del self.motorCurrentSensor2
                                del self.motorCurrentSensor3

                                #Stop SmartDot Data Collection
                                self.smartDot.stopAccel()
                                self.smartDot.stopGyro()
                                self.smartDot.stopMag()
                                self.smartDot.stopLight()
                                self.mode = BSCModes.READY_FOR_INSTRUCTIONS
                                self.startSmartDotHandler.clear()
                                self.currentSenorsOn = False

                        case(MsgType.A_B_DISCONNECT_FROM_BSC):
                            print("Server Disconnected")
                            #Raise the BokenPipeError, as the Communication Line is disconnected
                            raise BrokenPipeError
                        case():
                            print("Unknown Data: %s" % data[0])
                                
                except BrokenPipeError:
                    print("Pipe Error Caught in CommsHandler")
                    self.data['error_text'] = "Disconnected From Application Side"

                    #If smartDot is connected, Disconnect
                    if self.smartDot != None:
                        print("Disconnecting from SmartDot")
                        self.smartDot.disconnect()
                    raise BrokenPipeError
                except Exception as e:
                    print(f"Error Occured Somewhere in BSC: {e}")
                    self.data['error_text'] = e
                    #If smartDot is connected, Disconnect
                    if self.smartDot != None:
                        print("Disconnecting from SmartDot")
                        self.smartDot.disconnect()
                    print("Restarting Pipe")
                    raise BrokenPipeError
                #Try reading the dictionary here and acting on a change to maybe the stop_BSC value
                # print(self.data["close_bsc"]) 
                # shared_data["close_bsc"] is True    
           
    async def sensorHandler(self):
        while True: # Allow for thread to loop when repeated Start

            #motorEncoder = AuxSensorSimulator(None)
            while(self.currentSenorsOn): #runs until Sensors are
                # bytesData = bytearray([MsgType.B_A_SD_SENSOR_DATA,
                #                    0x00, 0x13, 0x41]) # Send Sensor Data for XL  
                
                # bytesData.extend(motorEncoder.readData()) 
                m1cData = self.motorCurrentSensor1.readData()
                self.data['motor_currents'][0] = "%.2f " % m1cData
                print("CurrentSensor 1: %f" % m1cData) 
                #This will Be to Send Current Sensor Data to BSA

                m2cData = self.motorCurrentSensor2.readData()
                self.data['motor_currents'][1] ="%.2f " % m2cData
                print("CurrentSensor 2: %f" % m2cData) 
                #This will Be to Send Current Sensor Data to BSA

                m3cData = self.motorCurrentSensor3.readData()
                self.data['motor_currents'][2] = "%.2f " % m3cData
                print("CurrentSensor 3: %f" % m3cData) 
                #This will Be to Send Current Sensor Data to BSA

                await asyncio.sleep(1)

    async def tCPscanAll(self, debugMode):
        #Wait until Application receives Start Scanner Message
        await self.startScanner.wait()
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
        
        BleScanner.set_handler(handler)
        BleScanner.start(scan_type='active')
        
        try :
            i = 0
            while self.startScanner.is_set(): 
                #update list every 5s
                #try:
                await asyncio.sleep(1.0)  
                #except asyncio.CancelledError:
                 #   break

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
                    p_msg = MsgType.name_from_value(bytesData[0])
                    self.data["message_type"] = p_msg
                    self.data["protocol_queue"].put(p_msg)
                    self.commsChannel.send(bytesData)
                    print("Sending")

        except BrokenPipeError: #If Comms Crash while Scanning
            pass

        finally:
            if not self.startScanner.is_set: 
                BleScanner.stop()

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
