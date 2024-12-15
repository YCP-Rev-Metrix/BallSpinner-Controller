from .iSmartDot import iSmartDot
from mbientlab.metawear import MetaWear
from mbientlab.warble import WarbleException
import asyncio
from datetime import datetime

import struct

class SmartDotEmulator(iSmartDot):

    def __init__(self):
        # Start the task with the current event loop
        self.loop = asyncio.new_event_loop()


    def UUID(self) -> str:
        return "326a9000-85cb-9195-d9dd-464cfbbae75b"
    
    def connect(self, MAC_Address) -> bool:
        print("Attempting to connect to device")
        #Add check for CSV File
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
    
    async def my_handler(self, dataRate, type):
        count = 1
        sleepPeriod = 1/dataRate
        while True:
            
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
                self.gyroDataSig(mess)
                #print("Mess Sent: " + mess.hex())

            await asyncio.sleep(sleepPeriod)

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
        self.loop.create_task(self.my_handler(dataRate, "Gyroscope"))  # Schedule the handler           


    def stopGyro(self):
        pass
    
        