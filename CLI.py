from BallSpinnerController.iSmartDot import iSmartDot
from BallSpinnerController.MetaMotion import MetaMotion
from BallSpinnerController.SmartDotEmulator import SmartDotEmulator
from BallSpinnerController.Motor import Motor
from mbientlab.warble import BleScanner
import six
import time
import asyncio

class CLI:
    async def scanAll(self) -> dict:
    
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

    def smartDotCLI(self):
        print("Starting Connection to SmartDot Module")
        print("Press ^C to Stop Scanning SmartDot Module")
        availDevices = asyncio.run(self.scanAll())
        print("Select SmartDot to Connect to:")
        consInput = input()
        smartDot = MetaMotion()
        smartDotConnect = smartDot.connect(tuple(availDevices.keys())[int(consInput)])
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

            if smartDot.commsChannel == None:
                print("[9] Connect to PC")


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
                odr = input()
                print("Select Range")
                range = input()
                print("Poll for How long?")
                timeForAccel = input()
                smartDot.startAccel(int(odr), int(range))
                time.sleep(int(timeForAccel))
                smartDot.stopAccel()

            elif consInput == "6":
                print("Select Rate")
                odr = input()
                print("Select Range")
                range = input()
                print("Poll for How long?")
                timeForGyro = input()
                smartDot.startGyro(int(odr), int(range))
                time.sleep(int(timeForGyro))
                smartDot.stopGyro()

            elif consInput == "7":
                print("Select Rate")
                print("[1] 10 Hz")
                print("[2] 20 Hz")

                dataRate = input()
                print("Poll for How long?")
                timeForMag = input()
                if dataRate == "1":
                    smartDot.startMag(10, None)
                elif dataRate == "2":
                    smartDot.startMag(20, None)
                else:
                    print("Too bad, polling at 10Hz")
                    smartDot.startMag(10, None)

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
                motors[int(motorNum)] = Motor.Motor(int(consInput))
            
            elif not motors.__getitem__(int(motorNum)).state:
                motors[int(motorNum)].turnOnMotor()

            
            elif motors.__getitem__(int(motorNum)).state:
                print("What are you changing the Duty Cycle?")
                consInput = input()
                motors[int(motorNum)].changeSpeed(int(consInput))

    def __init__(self):
        consInput = ""
        print("Ball Spinner Controller UI:")
        print("Which Part Are You Interacting With?")
        while(consInput != 'E'):
            print("----------------------")
            print("[1] SmartDot Module")
            print("[2] Motor")

            print("[E] Exit")
            consInput = input()

            if consInput == '1':
                self.smartDotCLI()
            elif consInput == '2':
                self.motorCLI()
            elif consInput == 'E':
                pass
            else:
                print("Invalid Input, Please Try Again\n")

CLI()
