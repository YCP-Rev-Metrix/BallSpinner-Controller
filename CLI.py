from BallSpinnerController.SmartDots.iSmartDot import iSmartDot
from BallSpinnerController.SmartDots.MetaMotion import MetaMotion
from BallSpinnerController.SmartDots.SmartDotEmulator import SmartDotEmulator
#from BallSpinnerController.Motor import Motor
from BallSpinnerController.Motors.iMotor import iMotor
from BallSpinnerController.Motors.StepperMotor import StepperMotor as Motor
from mbientlab.warble import BleScanner
import six
import time
import asyncio
import socket

class CLI:
    async def scanAll(self) -> dict:
    
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
                #update list every 5s
                await asyncio.sleep(1.0)  

                #print all BLE devices found and append to connectable list                
                count = 0
                for address, name in six.iteritems(self.availDevices):
                    if count >= i :
                        print("[%d] %s (%s)" % (i, address, name))
                        i += 1
                    count += 1

        except : #Called when KeyInterrut ^C is called
            BleScanner.stop()
            return self.availDevices

    def smartDotCLI(self):
        print("Starting Connection to SmartDot Module")
        print("Press ^C to Stop Scanning SmartDot Module")
        availDevices = asyncio.run(self.scanAll())
        print("Select SmartDot to Connect to:")
        consInput = input()

        #Jank way to grab Correct MAC Address: Creates Keys and gra
        smartDotMAC = tuple(self.availDevicesType.keys())[int(consInput)]
        smartDot = self.availDevicesType[smartDotMAC]()
        print()
        smartDotConnect = smartDot.connect(smartDotMAC)
        # Connect to Selected SmartDot Module
        while not smartDotConnect:
            print("Unable to Connect to ")
            print("Press ^C to Stop Scanning SmartDot Module")
            availDevices = asyncio.run(self.scanAll())
            print("Select SmartDot to Connect to:")
            consInput = input()
            smartDot = MetaMotion(tuple(availDevices.keys())[int(consInput)])

        while(consInput != 'E'):
            print("----------------------")
            print("Choose your function:")
            print("[1] Turn on Red LED")
            print("[2] Turn on Blue LED")
            print("[3] Turn on Green LED")
            print("[4] Turn off LED")
            print("[5] Start Accel Sensing")
            print("[6] Start Gyro Sensing")
            print("[7] Start Mag Sensing")
            print("[8] Start All Sensing")

            print("[E] Exit")
            consInput = input()

            if   consInput == "1":
                smartDot.turnOnRedLED()
                
            elif consInput == "2":
                smartDot.turnOnBlueLED()

            elif consInput == "3":
                smartDot.turnOnGreenLED()
                
            elif consInput == "4":
                smartDot.turnOffLED()
                
            elif consInput == "5":
                print("Select Rate")
                smartDot.setSampleRates(XL=int(input()))
                print("Select Range")
                smartDot.setRanges(XL=int(input()))
                print("Poll for How long?")
                timeForAccel = input()
                smartDot.startAccel()
                time.sleep(int(timeForAccel))
                smartDot.stopAccel()

            elif consInput == "6":
                print("Select Rate")
                smartDot.setSampleRates(GY=int(input()))
                print("Select Range")
                smartDot.setRanges(GY=int(input()))
                print("Poll for How long?")
                timeForGyro = input()
                smartDot.startGyro()
                time.sleep(int(timeForGyro))
                smartDot.stopGyro()

            elif consInput == "7":
                print("Select Rate")
                smartDot.setSampleRates(MG=int(input()))
                print("Select Range")
                smartDot.setRanges(MG=int(input()))
                print("Poll for How long?")
                timeForMag = input()
                smartDot.startMag()

                time.sleep(int(timeForMag))
                smartDot.stopMag()
            
            elif consInput == "8":
                print("Poll for How long?")
                timeForMag = input()
            
                smartDot.startMag(10, 10)
                smartDot.startAccel(100, 10)
                smartDot.startGyro(10, 10)
            
                time.sleep(int(timeForMag))
                smartDot.stopMag()
                smartDot.stopAccel()
                smartDot.stopGyro()
            elif consInput == "E":
                pass

            else:
                print("Invalid Input, Please Try Again\n")
            
        smartDot.disconnect()

    def motorCLI(self):
        print("----------------------")
        print("What Are you doing with the motors (Motors will turn of on Exit)")
        consInput = ""
        motors :list = [None, None, None, None]    
        while(consInput != 'E'):
            for i in range(1, motors.__len__()):
                if(motors.__getitem__(i) == None):
                    print("[%i] Connect to Motor" % i)
                
                elif not motors.__getitem__(i).state:
                    print("[%i] Turn On "% i)
                
                elif motors.__getitem__(i).state:
                    print("[%i] Change Speed"%i)
                
            print("[E] Exit")

            motorNum = input()
            if(motorNum == 'E'):
                consInput = "E"

            elif motors.__getitem__(int(motorNum)) == None:
                print("Which Pin is the Motor Connected To?")
                consInput = input()
                motors[int(motorNum)] = Motor(int(consInput))
            
            elif not motors.__getitem__(int(motorNum)).state:
                motors[int(motorNum)].turnOnMotor()

            
            elif motors.__getitem__(int(motorNum)).state:
                print("What is the RPM?")
                consInput = input()
                motors[int(motorNum)].changeSpeed(int(consInput))

    async def tcpCLI(self):
        #Start Up TCP Socket
        consInput = ''
        ipAddr = ''
        print("Starting Up Connection to Application, press ^C to stop")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ipAddr = s.getsockname()[0]
            commsPort = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (ipAddr, 8411)  
            print('Server listening on {}:{}'.format(*server_address))
            commsPort.bind(server_address)

            #wait for a device to attempt TCP connection to Port
            commsPort.listen(1)
            commsChannel, clientIp  = commsPort.accept()
            commsChannel.setblocking(True)
        except KeyboardInterrupt:
            print("\nUser Stopped While Listening, Exiting")
            commsPort.close()
            raise KeyboardInterrupt
        except OSError as e:
            if e.errno == 98:
                print("Port was not de-allocated properly, Exiting")
                raise KeyboardInterrupt
        except Exception as e:
            print(e)
            print("Unable to connect to the internet to obtain a Global Ip address, please try again later")
            consInput = 'E'
        print("Connection Established, verifying application")
        
        #Grab Random Byte from third and resend
        data = commsChannel.recv(1024)
        bytesData = bytearray([0x02, 0x00, 0x01, data[3]]) 
        commsChannel.send(bytesData)
        print("Software Connected")
        async def tcpListener(): #Continuosly Print received messages, even when sending
            print("Listening To Socket")
            run = True
            while run == True:
                try:
                    data = await asyncio.get_event_loop().run_in_executor(None, commsChannel.recv, 1024)
                    print(f"Received {data}")
                except Exception: #If commsChannel is closed, end loop
                    run = False

        #Start up tcpListener()        
        listening = asyncio.create_task(tcpListener())

        async def sendMessages(): #
            message = ""
            while(message != 'E'):
                #Call input() without blocking main thread
                message = await asyncio.get_event_loop().run_in_executor(None, input, "What Hex Message do you want to send?"+
                "\nStart with 0x:\n"
                "or press E to exit\n")
                if(message == "E"):
                    pass
                elif message.__len__() % 2 !=0 :
                    print("Unable to Parse Bytes with uneven amount of Hex")
                else:
                    #whatever fucking works - Zach Cox
                    
                    bytesMessage = []
                    message=message[2:]
                    size= 0
                    
                    while(size + 1 < message.__len__()):
                        bytesMessage.append(int(message[size:size+2], 16))
                        size = size+2
                   
                    bytesarrayMessage : bytearray = bytearray(bytesMessage)
                    print(bytesarrayMessage)
                    commsChannel.send(bytesarrayMessage)
                    #Give a chance for any immediate messages to come in
                
                time.sleep(.5)

        #Allow time for tcpListener to start up before starting sendMessages()
        #this way the tcpListener printout comes before the sendMessages printout
        time.sleep(.1)
        await sendMessages()
        listening.cancel()
        try:
            await listening
        except asyncio.CancelledError:
            print("Extra Thread Closed")

        commsChannel.shutdown(socket.SHUT_RDWR)
        commsPort.shutdown(socket.SHUT_RDWR)
        commsChannel.close()
        commsPort.close()
        print("Ports Closed")
        time.sleep(1)

    def __init__(self):
        consInput = ""
        print("Ball Spinner Controller UI:")
        while(consInput != 'E'):
            print("----------------------")
            print("Which Part Are You Interacting With?")
            print("[1] SmartDot Module")
            print("[2] Motor")
            print("[3] TCP")
            print("[E] Exit")
            consInput = input()

            if consInput == '1':
                self.smartDotCLI()
            elif consInput == '2':
                self.motorCLI()
            elif consInput == '3':
                try:
                    asyncio.run(self.tcpCLI())
                except KeyboardInterrupt: #If stopped by user, keep CLI running
                    pass
            elif consInput == 'E':
                pass
            else:
                print("Invalid Input, Please Try Again\n")

CLI()

