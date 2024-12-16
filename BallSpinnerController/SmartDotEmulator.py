from .iSmartDot import iSmartDot
from mbientlab.metawear import MetaWear
from mbientlab.warble import WarbleException
import asyncio
from datetime import datetime
from time import sleep
import struct

class SmartDotEmulator(iSmartDot):
    #Value in Str because all MAC Adress checks use strings (Currently)

    def __init__(self):
        # Start the task with the current event loop
        self.loop = asyncio.new_event_loop()
        self._MAC_ADDRESS = "11:11:11:11:11:11"


    def UUID(self) -> str:
        return "326a9000-85cb-9195-d9dd-464cfbbae75b"
    
    def connect(self, MAC_Address) -> bool:
        #Confirm the 
        if not MAC_Address == self._MAC_ADDRESS:
            print("SmartDot Emulator: Incorrect MAC Adress")
            print("SmartDot Emulator: Expected 11:11:11:11:11 and got %s" % MAC_Address)
            return False
        print("SmartDotEmulator: Attempting open CSV data")
        # Open the CSV file
        try:
            csvFile = open('data/SmartDotEmulatorData.csv', 'r') 
            self.smartDotData = csvFile.readlines()
        except:
            return False
        
        finally: 
            csvFile.close()
            print("SmartDotEmulator: CSV File stored locally")
        
        return True  
        
    def disconnect(MAC_Address):
        return super().disconnect()
    
    def my_handler(self, dataRate, type):
        "Handler Called"
        count = 1
        sleepPeriod = 1/dataRate
        while self.sendingGyroData:
            
            sampleCountInBytes = struct.pack('>I', count)[1:4]
            timeStampInBytes : bytearray = struct.pack("<f", datetime.now().timestamp())

            sensorXValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[7])
            sensorYValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[8])
            sensorZValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[9])

            xValInBytes : bytearray = struct.pack('<f', sensorXValue) 
            yValInBytes : bytearray = struct.pack('<f', sensorYValue)
            zValInBytes : bytearray = struct.pack('<f', sensorZValue)
        
            
            mess = sampleCountInBytes + timeStampInBytes + xValInBytes + yValInBytes + zValInBytes

            print("SmartDotEmulator: %lf, %lf, %lf" % (sensorXValue, sensorYValue, sensorZValue))
            count+=1
            if type == "Gyroscope":   
                print(self.gyroDataSig) #delee
                try: ## Check if TCP connection is set up, if not, just print in terminal
                    print("Encoded Data " + xValInBytes.hex() + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex())
                except:
                    print("Mess Sent: " + mess.hex())

            sleep(sleepPeriod)

    def startMag(self,  dataRate : int, odr : None):   
        # Run the event loop
        pass
    
    def stopMag(self):
        pass

    def startAccel(self, dataRate : int, range : int):
        pass

    def stopAccel(self):
        pass

    def startGyro(self, dataRate : int, range : int):
        self.sendingGyroData = True
        self.loop.create_task(self.my_handler(dataRate, "Gyroscope"))  # Schedule the handler           
        


    def stopGyro(self):
        self.sendingGyroData = False
    
        