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
        self.commsChannel : socket = self.commsPort.accept()
        
        
        #Start Threads
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(
            self.commsHandler()))       
        
    async def smartDotHandler(self):
        print("Handling SmartDot:")
        def accelDataSignal(dataBytes : bytearray):
            print("Acceleration: " + (dataBytes.__str__()))
        
        def magDataSignal(dataBytes : bytearray):
            print("Magnetometer: " + (dataBytes.__str__()))
        
        def gyroDataSignal(dataBytes : bytearray):
            print("Gyroscope: " + (dataBytes.__str__()))


        self.smartDot.setDataSignals(accelDataSignal, magDataSignal, gyroDataSignal)
        asyncio.run(asyncio.sleep(9999))

        

    async def commsHandler(self):
        
        #Read first message com
        data = self.commsChannel.recv(1024)
        print(type(data))
        print(data)
        #parse message
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
                    randomByte = data[2]
                    self.commsChannel.send(0x820001 + randomByte.hex())
                    self.mode = BSCModes.IDLE


            case(0x83):
                pass         
        
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