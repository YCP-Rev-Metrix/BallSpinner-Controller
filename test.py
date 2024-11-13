from mbientlab.metawear import MetaWear, libmetawear
import ConnectionTools
import MetaMotion
import SmartDotEmulator
from time import sleep
import socket
import RPi.GPIO as GPIO

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

def startMagTest():
    # When scan cancelled, connect to first SmartDot in Dict
    smartDot = ConnectionTools.MetaMotion()
    findDotMacAddress = ConnectionTools.asyncio.run(ConnectionTools.scanAll())

    #connects to first SmartDot module found 
    smartDot.connect(findDotMacAddress.popitem()[0])   

    #Samples for 99 seconds, cancel to stop
    smartDot.startMag()
    sleep(99)
    print("DidNotWork")

startMagTest()
