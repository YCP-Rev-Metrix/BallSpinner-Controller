import ConnectionTools
import MetaMotion
import time

consInput = ""
print("Ball Spinner Controller UI:")
print("Press ^C to Stop Scanning SmartDot Module")
availDevices = ConnectionTools.asyncio.run(ConnectionTools.scanAll())
print("Select SmartDot to Connect to:")
consInput = input()
smartDot = MetaMotion.MetaMotion()
smartDotConnect = False
try: 
    smartDotConnect = smartDot.connect(tuple(availDevices.keys())[int(consInput)])
except:
    # Connect to Selected SmartDot Module
    while not smartDotConnect:
        print("Unable to Connect to ")
        print("Press ^C to Stop Scanning SmartDot Module")
        availDevices = ConnectionTools.asyncio.run(ConnectionTools.scanAll())
        print("Select SmartDot to Connect to:")
        consInput = input()
        smartDot = MetaMotion.MetaMotion(tuple(availDevices.keys())[int(consInput)])

while(consInput != 'E'):
    print("----------------------")
    print("Choose your function:")
    print("[1] Turn on Red LED")
    print("[2] Turn on Blue LED")
    print("[3] Turn on Green LED")
    print("[4] Turn off LED")
    print("[5] Start Accel Sensing")
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
        smartDot.configAccel(int(odr), int(range))
        smartDot.startAccel()
        time.sleep(int(timeForAccel))
        smartDot.stopAccel()

    elif consInput == "E":
        pass

    else:
        print("Invalid Input, Please Try Again\n")



