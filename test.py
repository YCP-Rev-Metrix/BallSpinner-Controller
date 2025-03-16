from mbientlab.metawear import MetaWear, libmetawear
from BallSpinnerController import *
from time import sleep
import asyncio
import socket
import RPi.GPIO as GPIO
import multiprocessing 
import struct
'''
#Set PWM Pin Motor is Connected to 
GPIOPin = 35
#Configure GPIO Pin
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIOPin, GPIO.OUT)


PWM = GPIO.PWM(GPIOPin, 1000)
print("start")
PWM.start(100)
sleep(500)
PWM.stop()

availDevices = ConnectionTools.asyncio.run(ConnectionTools.scanAll())
print("Select SmartDot to Connect to:")
consInput = input()
smartDot = MetaMotion.MetaMotion()
smartDotConnect = False
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to an IP address and port
server_address = ("10.127.7.20", 8411)  # Replace 'localhost' with the server's IP if needed
server_socket.bind(server_address)
#192.

# Listen for incoming connections
server_socket.listen(1)

print('Server listening on {}:{}'.format(*server_address))

# Accept a connection
connection, client_address = server_socket.accept()
smartDotConnect = smartDot.connect(tuple(availDevices.keys())[int(consInput)], connection)# Create a socket object

print('Connected to:', client_address)


# Send a response to the client
connection.sendall(b'Hello from the server!')
# Receive data from the client
data = connection.recv(1024)
print('Received:', data.decode())

print("Select Rate")
odr = input()
print("Select Range")
range = input()
print("Poll for How long?")
timeForAccel = input()
smartDot.configAccel(int(odr), int(range))
smartDot.startAccel()
sleep(int(timeForAccel))
smartDot.stopAccel()
# Close the connection
try:
    while 1:
        pass
except:
    connection.close()
    server_socket.close()
'''

def startLightTest():
    # When scan cancelled, connect to first SmartDot in Dict
    smartDot = MetaMotion()
    findDotMacAddress = asyncio.run(scanAll())

    #connects to first SmartDot module found 
    smartDot.connect(findDotMacAddress.popitem()[0])   

    #Samples for 99 seconds, cancel to stop
    smartDot.startLight()
    sleep(99)
    print("DidNotWork")

class restartTest:
    @classmethod
    def setUpClass(cls):
        pass          
            

    def crashSystemRestart(self):
        
        def _test_socket_Established(self):
            try:
                    # Create a client socket and connect to the server
                        
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                server_ip = self.ipAddr  # Replace with the actual IP address
                server_port = 8411  # Replace with the actual port
            
                print("Test: Connecting to BSC")
                client_socket.connect((server_ip, server_port))

                print("Test: Connected to BSC")

                self.commsPort = client_socket
                
            except socket.error as e:
                self.fail(e)

        def _test_APP_INIT_ACK(self):
            # Send APP_INIT
            print("Test: Sending APP_INIT")
            self.commsPort.sendall(bytearray([0x01, 0x00, 0x01, 0x00]))
                
            #Receive APP_INIT_ACK
            response = self.commsPort.recv(4)

            #Confirm APP_INIT_ACK in Protocol
            if(response == b'\x02\x00\x01\x00'):
                print("Test: Received APP_INIT_ACK")

        def _test_BSC_NAME(self):
            pass

        def _test_SMARTDOT_SCAN(self):
            #Send SMARTDOT_SCAN
            print("Test: Sending SMARTDOT_SCAN_INIT")
            self.commsPort.sendall(bytearray([0x05, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

            #Receive ABBREVIATED_SMARTDOT_CONNECTED (ASSUMING THE FIRST RETRIEVED IS THE SMARTDOT_EMULATOR)
            #Confirm SMARTDOT_SCAN in Protocol

            #1) Parse Header
            data = self.commsPort.recv(1024)
            #Determine Size of Message
            
            print("Test: Received SMARTDOT_SCAN")      

        def _test_ABBREVIATED_SMARTDOT_CONNECTED(self):
            print("Test: Sending SMART_SCAN_CONNECT")
            self.commsPort.sendall(bytearray([0x05, 0x00, 0x06, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11]))
            response = self.commsPort.recv(9)
            print("Test: Received ABBREVIATED_SMARTDOT_CONNECTED")

         # Start the BallSpinnerController in a separate process
        bsc_process = multiprocessing.Process(target=BallSpinnerController, args="1") 
        bsc_process.start()

        # Give time for BallSpinnerController to Connect to Socket
        sleep(.5)

        #determine global ip address
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                self.ipAddr = s.getsockname()[0]

        except Exception:
            # ERROR: Not Connected to Internet
            pass 
        _test_socket_Established(self)
        _test_APP_INIT_ACK(self)
        _test_BSC_NAME(self)
        _test_SMARTDOT_SCAN(self)
        _test_ABBREVIATED_SMARTDOT_CONNECTED(self)
        self.commsPort.sendall(bytearray([0x05, 0x00, 0x06, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11]))
        self.commsPort.sendall(bytearray([0x0B]))
        print("Test: SED ]")

        sleep(4)
        self.commsPort.sendall(bytearray([0x08, 0x00, 0x03, 0x0A, 0x0A, 0x0A]))
        print("Test: SED ABBREVIATED_SMARTDOT_CONNECTED")

        sleep(4)
        self.commsPort.sendall(bytearray([0x0B]))
        print("Test: SED STO")

        sleep(4)
        self.commsPort.sendall(bytearray([0x08, 0x00, 0x03, 0x0A, 0x0A, 0x0A]))

MMS = MetaMotion()
print(MMS.sendConfigSettings())
#smartDot = SmartDotEmulator()
#smartDot.sendConfigSettings()