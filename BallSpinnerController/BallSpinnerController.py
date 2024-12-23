import asyncio
import threading
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

    def __init__(self):
    
        #determine global ip address
        self.iSmartDot = None
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ipAddr = s.getsockname()[0]

        except Exception:
            # ERROR: Not Connected to Internet
            pass 
        self.socketHandler(ipAddr)

    def socketHandler(self, ipAddr):    
        while(True): #loop re-opening socket if crashes
            self.mode = BSCModes.WAITING_FOR_APP_INITILIZATION
            #initiate Port to 8411
            self.commsPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (ipAddr, 8411)  # Replace 'localhost' with the server's IP if needed
            print('Server listening on {}:{}'.format(*server_address))
            self.commsPort.bind(server_address)

            #wait for a device to attempt TCP connection to Port
            self.commsPort.listen(1)
            self.commsChannel, clientIp  = self.commsPort.accept()
            self.commsChannel.setblocking(True)
            try:
                    asyncio.run(self.commsHandler()) 
            except OSError: #Raised if Comms is forcibly closed by resetCommsPort while waiting for message
                print("Socket Closed, must restart")   

            except KeyboardInterrupt:
                print("Crashed by User")
                exit(0)

    def resetCommsPort(self):
        self.smartDot.stopGyro()
        self.smartDot.stopAccel()
        self.smartDot.stopMag()
        self.commsChannel.close()
        self.commsPort.close()
    
    async def smartDotHandler(self):
        print("Handling SmartDot:")
        def accelDataSignal(dataBytes : bytearray):
            bytesData = bytearray([0x8A, 0x00, 0x13, 0x41])
            bytesData.extend(dataBytes)
            try:
                self.commsChannel.sendall(bytesData)
            except Exception as e:
                raise self.resetCommsPort()

                def brokenPipeErrorThrower():
                    print(f"Exception caught in the event loop: {exception}")
                # Schedule the exception-handling coroutine on the main event loop
                asyncio.run_coroutine_threadsafe(brokenPipeErrorThrower, asyncio.get_event_loop())
                raise BrokenPipeError

        def magDataSignal(dataBytes : bytearray):
            bytesData = bytearray([0x8A, 0x00, 0x13, 0x4D])
            bytesData.extend(dataBytes)
            try:
                self.commsChannel.sendall(bytesData)
            except BrokenPipeError:
                raise 
                
                def brokenPipeErrorThrower():
                    print(f"Exception caught in the event loop: {exception}")
                # Schedule the exception-handling coroutine on the main event loop
                asyncio.run_coroutine_threadsafe(brokenPipeErrorThrower, asyncio.get_event_loop())
        
        def gyroDataSignal(dataBytes : bytearray):
            bytesData = bytearray([0x8A, 0x00, 0x13, 0x47])
            bytesData.extend(dataBytes)
            try:
                self.commsChannel.sendall(bytesData)
            except Exception as e:
                self.resetCommsPort()
                raise BrokenPipeError
                

                def brokenPipeErrorThrower():
                    print(f"Exception caught in the event loop: {exception}")
                # Schedule the exception-handling coroutine on the main event loop
                asyncio.run_coroutine_threadsafe(brokenPipeErrorThrower, asyncio.get_event_loop())
                raise BrokenPipeError

        self.smartDot.setDataSignals(accelDataSig= accelDataSignal, magDataSig= magDataSignal, gyroDataSig=gyroDataSignal)
        #Instantly Setting the Start Configs for the 9DOF's to skip implementation

        self.smartDot.startMag(10, 10)
        self.smartDot.startAccel(100, 10)
        self.smartDot.startGyro(100, 10)       
        
        await self.wait_for_completion()
        print("Handler Done")

    async def wait_for_completion(self):
        await asyncio.sleep(9999)  # Or replace this with a condition/event loop

    async def commsHandler(self):
            print("Comms Handler entered")
            loop = asyncio.get_event_loop()
            while True:
            #Read first message com
                try:
                    data = await loop.run_in_executor(None, self.commsChannel.recv, 1024)
                    #parse message
                    if not data == b'':
                        print(data)
                        match data[0]: 
                            case(0x81): #APP_INIT Message
                                #Message Received: | Mess Type: 0x81 | Mess Size: 0x0001 | RandomByte: XXXX 
                                print("Message Type: App Sending Start Message")
                                if self.mode != BSCModes.WAITING_FOR_APP_INITILIZATION:
                                    #Send Error: Already Connected to Application

                                    #Reset
                                    pass
                                else:
                                    # Confirm Communications are established and send confirmation signal
                                    #| Mess Type: 0x82 | Mess Size: 0x0001 | RandomByte: XXXX 
                                    
                                    #Grab Random Byte from third and resend
                                    bytesData = bytearray([0x82, 0x00, 0x01, data[3]]) 
                                    #bytesData.append(data[2])
                                    #print(bytes(bytesData))
                                    self.commsChannel.send(bytesData)
                                    self.mode = BSCModes.IDLE

                            case(0x83): #BSC_NAME_REQ Message
                                print("Looking For Pi")
                                name : str = "Ball Spinner Controller"
                                bytesData =bytearray([0x84, 0x00, name.__len__()])
                                bytesData.extend(name.encode("utf-8"))
                                print(bytes(bytesData))
                                self.commsChannel.send(bytesData)
                                self.mode = BSCModes.IDLE
                                pass
                            
                            case(0x85): #BSC_NAME Message
                                print(data[3:9].hex())
                                #If the 
                                if data[3:9].hex() == "000000000000":
                                    print("TRUEEEEE")
                                    self.mode = BSCModes.BLUETOOTH_SCANNING
                                    self.scanner = asyncio.create_task(self.tCPscanAll(0))
                                    print("Connecting to \"SmartDot\"")
                                #Keep Trying to connect to Module in Presentation Ball
                                else:
                                    self.scanner.cancel()
                                    self.smartDot : iSmartDot = None
                                    
                                    smartDotMACStr = "%s:%s:%s:%s:%s:%s" % (data[3:4].hex(), 
                                    data[4:5].hex(), data[5:6].hex(), data[6:7].hex(), data[7:8].hex(), 
                                    data[8:9].hex())  
                                    try: #if not in debug mode and application sends SMARTDOTEMULATOR String, 
                                        if self.availDevicesType[smartDotMACStr] == SmartDotEmulator:
                                            print("Simulator Selected")
                                            self.smartDot = SmartDotEmulator()
                                        else:
                                            pass
                                    except KeyError:
                                        print("Application Sent Device Not Scanned")

                                        print("Womp Womp") 
                                        self.smartDot = MetaMotion()
                                    print("Connecting to "+ smartDotMACStr)
                                    print(smartDotMACStr)
                                    if not self.smartDot.connect(smartDotMACStr):   
                                        self.smartDot = None
                                    
                                    #NEED TO CHECK IF NOT TRUE, SEND ERROR
                                    bytesData = bytearray([0x86, 0x00, 0x06])
                                    bytesData.extend(data[4:9]) 
                                    print(bytes(bytesData))
                                    self.commsChannel.send(bytesData)
                                    self.mode = BSCModes.READY_FOR_INSTRUCTIONS
    
                            case(0x88): #ABBREVIATED_MOTOR_INSTRUCTIONS Message
                                #print("Received Motor Instruction")
                                if self.mode == BSCModes.READY_FOR_INSTRUCTIONS: 
                                    print("Initializing Sensors")
                                    # First Motor Instruction:         
                                    try:          
                                        asyncio.create_task(self.smartDotHandler())    
                                    except BrokenPipeError:
                                        raise BrokenPipeError
                                    #Turn On Motors
                                    self.PrimMotor = Motor(40)
                                    self.secMotor1 = Motor(38)
                                    self.secMotor2 = Motor(35)                

                                    self.PrimMotor.turnOnMotor(0)
                                    self.secMotor1.turnOnMotor(0)
                                    self.secMotor2.turnOnMotor(0)

                                    self.mode = BSCModes.TAKING_SHOT_DATA
                                
                                self.PrimMotor.changeSpeed(int(data[3]/30*100)) 
                                self.secMotor1.changeSpeed(int(data[4]/12*100)) 
                                self.secMotor2.changeSpeed(int(data[5]/12*100))

                            case(0x8B): #STOP_MOTOR_INSTRUCTIONS
                                if self.mode == BSCModes.TAKING_SHOT_DATA:
                                    #Stop Motors

                                    self.PrimMotor.turnOffMotor()
                                    self.secMotor1.turnOffMotor()
                                    self.secMotor2.turnOffMotor()

                                    #Stop SmartDot Data Collection
                                    self.smartDot.stopAccel()
                                    self.smartDot.stopGyro()
                                    self.smartDot.stopMag()
                except BrokenPipeError:
                    print("Pipe Error Caught in CommsHandler")
                    sys.exit(1)
                    raise
            


    async def tCPscanAll(self, debugMode):
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
                    self.availDevicesType[result.mac] = smartDotClass

        if(debugMode):
            print("Software Added")
            self.availDevices["11:11:11:11:11:11"] = "smartDotSimulator" 
            self.availDevicesType["11:11:11:11:11:11"] = SmartDotEmulator

        BleScanner.set_handler(handler)
        BleScanner.start()
        
        try :
            i = 0
            while True: 
                #update list every 5s
                await asyncio.sleep(1.0)  

                #print all BLE devices found and append to connectable list                
                count = 0
                for address, name in six.iteritems(self.availDevices):
                    address = address.replace(":", "")
                    bytesData = bytearray([0x86, 0x00, 0x06, 
                                        int(address[0:2],16),
                                        int(address[2:4],16),
                                        int(address[4:6],16),
                                        int(address[6:8],16),
                                        int(address[8:10],16),
                                        int(address[10:12],16)])
                    name : str
                    bytesData.extend(name.encode("utf-8"))
                    print(self.commsChannel.send(bytesData))
                    
                

        except asyncio.CancelledError: #Called when KeyInterrut ^C is called
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