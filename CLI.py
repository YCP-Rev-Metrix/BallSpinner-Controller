import ConnectionTools
import MetaMotion
import time
import Motor

def smartDotCLI():
    print("Starting Connection to SmartDot Module")
    print("Press ^C to Stop Scanning SmartDot Module")
    availDevices = ConnectionTools.asyncio.run(ConnectionTools.scanAll())
    print("Select SmartDot to Connect to:")
    consInput = input()
    smartDot = MetaMotion.MetaMotion()
    smartDotConnect = smartDot.connect(tuple(availDevices.keys())[int(consInput)])
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
            smartDot.startMag(10, 10)
            smartDot.startAccel(100, 10)
            smartDot.startGyro(10, 10)
            
        elif consInput == "E":
            pass

        else:
            print("Invalid Input, Please Try Again\n")

def motorCLI():
    print("Which Pin is the Motor Connected to?")
    consInput = input()
    motor = Motor.Motor(int(consInput))
    while(consInput != 'E'):
        print("----------------------")
        print("Choose your function:")
        print("[1] Start Motor")
        print("[2] Stop Motor")
        print('[3] Change Speed of Motor')
        print('[E] Exit')
        consInput = input()

        if consInput == "1":
            motor.turnOnMotor()
            
        elif consInput == "2":
            motor.turnOffMotor()

        elif consInput == "3":
            print("Select Speed Between 0% - 100%")
            consInput = input()
            motor.changeSpeed(int(consInput))
            
        elif consInput == "E":
            pass

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
        smartDotCLI()
    elif consInput == '2':
        motorCLI()
    elif consInput == 'E':
        pass
    else:
        print("Invalid Input, Please Try Again\n")

