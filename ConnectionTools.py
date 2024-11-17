import asyncio
from mbientlab.warble import BleScanner
import six
from MetaMotion import MetaMotion
from SmartDotEmulator import SmartDotEmulator
from iSmartDot import iSmartDot
from Motor import Motor
import socket
import struct
from enum import Enum

# class syntax
class BSCModes(Enum):
    #Controller not Connected to Application
    WAITING_FOR_APP_INITILIZATION  = 1

    #Controller Connected to Application Waiting for Next Message Signal
    IDLE = 2
    
    #Searching For Bluetooth
    BLUETOOTH_SCANNING = 3

    #
    READYFORINSTRUCTIONS = 4

    TAKING_SHOT_DATA = 5
    
class BallSpinnerController():
    def setSmartDot(self, smartDot : MetaMotion):
        self.smartDot = smartDot

    def __init__(self):
        #determine global ip address
        self.iSmartDot = None
        self.mode : BSCModes = BSCModes.WAITING_FOR_APP_INITILIZATION

        ipAddr = None
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ipAddr = s.getsockname()[0]

        except Exception:
            # ERROR: Not Connected to Internet
            pass 

        #initiate Port to 8411
        self.commsPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ipAddr, 8411)  # Replace 'localhost' with the server's IP if needed
        print('Server listening on {}:{}'.format(*server_address))
        self.commsPort.bind(server_address)

        #wait for a device to attempt TCP connection to Port
        self.commsPort.listen(1)
        self.commsChannel, clientIp  = self.commsPort.accept()
        
        self.commsChannel.setblocking(True)
        asyncio.run(self.commsHandler())       
        
    async def smartDotHandler(self):
        print("Handling SmartDot:")
        def accelDataSignal(dataBytes : bytearray):
            bytesData = bytearray([0x8A, 0x00, 0x13, 0x41])
            bytesData.extend(dataBytes)
            #self.commsChannel.sendall(bytesData)

        def magDataSignal(dataBytes : bytearray):
            bytesData = bytearray([0x8A, 0x00, 0x13, 0x4D])
            bytesData.extend(dataBytes)
            #self.commsChannel.sendall(bytesData)
        
        def gyroDataSignal(dataBytes : bytearray):
            bytesData = bytearray([0x8A, 0x00, 0x13, 0x47])
            bytesData.extend(dataBytes)
            self.commsChannel.sendall(bytesData)
            #print("Gyroscope: " + (dataBytes.__str__()))


        self.smartDot.setDataSignals(accelDataSignal, magDataSignal, gyroDataSignal)
        #Instantly Setting the Start Configs for the 9DOF's to skip implementation
        self.smartDot.startMag(10, 10)
        self.smartDot.startAccel(100, 10)
        self.smartDot.startGyro(10, 10)       
        await self.wait_for_completion()
        print("Handler Done")

    async def wait_for_completion(self):
        await asyncio.sleep(9999)  # Or replace this with a condition/event loop

    async def commsHandler(self):
            loop = asyncio.get_event_loop()
            while True:
            #Read first message com
                data = await loop.run_in_executor(None, self.commsChannel.recv, 1024)
                #parse message
                if not data == b'':
                    print(type(data))
                    
                    print(data)
                    print(data.hex())
                    match data[0]: 
                        case(0x81):
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
                                #bytesData.
                                # append(data[2])
                                #print(bytes(bytesData))
                                self.commsChannel.send(bytesData)
                                self.mode = BSCModes.IDLE


                        case(0x83):
                            print("Looking For Pi")
                            name : str = "MyBallz"
                            bytesData =bytearray([0x84, 0x00, name.__len__()])
                            bytesData.extend(name.encode("utf-8"))
                            print(bytes(bytesData))
                            self.commsChannel.send(bytesData)
                            self.mode = BSCModes.IDLE
                            pass

                        case(0x85):
                            print("Connecting to \"SmartDot\"")
                            #Keep Trying to connect to Module in Presentation Ball
                            self.smartDot = None
                            while self.smartDot == None:
                                self.smartDot = MetaMotion()
                                if not self.smartDot.connect("C8:30:26:28:92:4A") :   
                                    self.smartDot = None
    
                            #NEED TO MAKE VARIABLE
                            bytesData = bytearray([0x86, 0x00, 0x06,  0xC8, 0x30, 0x26, 0x28, 0x92, 0x4A]) 
                            print(bytes(bytesData))
                            self.commsChannel.send(bytesData)
                            self.mode = BSCModes.READYFORINSTRUCTIONS

                        case(0x88):
                            print("Received Motor Instruction")
                            if self.mode == BSCModes.READYFORINSTRUCTIONS: 
                                print("Initializing Sensors")
                                # First Motor Instruction:                   
                                asyncio.create_task(self.smartDotHandler())    

                                #Turn On Motors
                                self.PrimMotor = Motor(7)
                                self.secMotor1 = Motor(11)
                                self.secMotor2 = Motor(12)                

                                self.PrimMotor.turnOnMotor(0)
                                self.secMotor1.turnOnMotor(0)
                                self.secMotor2.turnOnMotor(0)

                                self.mode = BSCModes.TAKING_SHOT_DATA

                            print("Motor1: %i" % data[3])
                            print("Motor2: %i" % data[4])
                            print("Motor3: %i" % data[5])

                            self.PrimMotor.changeSpeed(int(data[3]/30)) 
                            self.secMotor1.changeSpeed(int(data[4]/30)) 
                            self.secMotor2.changeSpeed(int(data[5]/30))

                            
                    
        
    '''
        availDevices = asyncio.run(scanAll())
        print("Select SmartDot to Connect to:")
        consInput = input()
        smartDot = MetaMotion()
        smartDotConnect = False
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        

        print('Server listening on {}:{}'.format(*server_address))

        # Accept a connection
        smartDotConnect = smartDot.connect(tuple(availDevices.keys())[int(consInput)], connection) # Create a socket object

        print('Connected to:', client_address)


        # Send a response to the client
        connection.sendall(b'Hello from the server!')
        # Receive data from the client
        data = connection.recv(1024)
        print('Received:', data.decode())

        '''
    
        
#Scans all modules to see which to connect to
async def scanAll() -> dict:
    
    availDevices = {}
    smartDot : iSmartDot = [MetaMotion(), SmartDotEmulator()]

    #self.mode = "Scanning"
    selection = -1
    #Continuously rescans for MetaWear Devices
    print("scanning for devices...")

    #Check if the Bluetooth device has ANY UUID's from any of the iSmartDot Modules
    def handler(result):
        for listedConnect in range(len(smartDot)):
            if result.has_service_uuid(smartDot[listedConnect].UUID()):
                availDevices[result.mac] = result.name

    BleScanner.set_handler(handler)
    BleScanner.start()
    
    try :
        i = 0
        while True: #self.mode == "Scanning":
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

'''
availDevices = asyncio.run(scanAll())
smartDot = MetaMotion()
smartDotConnect = smartDot.connect(tuple(availDevices.keys())[0])
myBallz = BallSpinnerController()
myBallz.smartDot = smartDot
myBallz.smartDot.startAccel(100,2)
myBallz.smartDot.startGyro(100, 100)
myBallz.smartDot.startMag(100, 10)
myBallz.smartDotHandler()
'''

BallSpinnerController()