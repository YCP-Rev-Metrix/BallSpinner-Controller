from .iSmartDot import iSmartDot
from mbientlab.metawear import MetaWear
from mbientlab.warble import WarbleException
import threading
from datetime import datetime
from time import sleep
import struct

class SmartDotEmulator(iSmartDot):
    #Value in Str because all MAC Adress checks use strings (Currently)
    XL_availSampleRate = [12.5, 25, 50, 100, 200, 400, 800, 1600, 3200]
    XL_availRange = []

    GY_availSampleRate = []
    GY_availRange = []

    
    MG_availSampleRate = []
    MG_availRange = []

    LT_availRange = []

    def __init__(self):
        global XL_availSampleRate
        # Start the task with the current event loop
        self._MAC_ADDRESS = "11:11:11:11:11:11"
        self.XL_availSampleRate = SmartDotEmulator.XL_availSampleRate

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
        except Exception as e:
            print(e)
            return False
        
        finally: 
            csvFile.close()
            print("SmartDotEmulator: CSV File stored locally")
        
        return True  
        
    def disconnect(MAC_Address):
        return super().disconnect()
    
    def accelHandler(self, dataRate):
        count = 1
        sleepPeriod = 1/dataRate
        while self.sendingAccelData:
            
            sampleCountInBytes = struct.pack('>I', count)[1:4]
            timeStampInBytes : bytearray = struct.pack("<f", datetime.now().timestamp())

            sensorXValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[1])
            sensorYValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[2])
            sensorZValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[3])

            xValInBytes : bytearray = struct.pack('<f', sensorXValue) 
            yValInBytes : bytearray = struct.pack('<f', sensorYValue)
            zValInBytes : bytearray = struct.pack('<f', sensorZValue)
        
            
            mess = sampleCountInBytes + timeStampInBytes + xValInBytes + yValInBytes + zValInBytes

            print("SmartDotEmulator: %lf, %lf, %lf" % (sensorXValue, sensorYValue, sensorZValue))
            count+=1
            try: ## Check if TCP connection is set up, if not, just print in terminal
                self.accelDataSig(mess)
                print("Encoded Data " + xValInBytes.hex() + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex()) #Not with SME Prefix because ALL iSmartDot classes print this
            except:
                print("Mess Sent: " + mess.hex())
            sleep(sleepPeriod)

    def magHandler(self, dataRate):
        count = 1
        sleepPeriod = 1/dataRate
        while self.sendingMagData:
            
            sampleCountInBytes = struct.pack('>I', count)[1:4]
            timeStampInBytes : bytearray = struct.pack("<f", datetime.now().timestamp())

            sensorXValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[4])
            sensorYValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[5])
            sensorZValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[6])

            xValInBytes : bytearray = struct.pack('<f', sensorXValue) 
            yValInBytes : bytearray = struct.pack('<f', sensorYValue)
            zValInBytes : bytearray = struct.pack('<f', sensorZValue)
        
            
            mess = sampleCountInBytes + timeStampInBytes + xValInBytes + yValInBytes + zValInBytes

            print("SmartDotEmulator: %lf, %lf, %lf" % (sensorXValue, sensorYValue, sensorZValue))
            count+=1
            try: ## Check if TCP connection is set up, if not, just print in terminal
                self.magDataSig(mess)
                print("Encoded Data " + xValInBytes.hex() + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex()) #Not with SME Prefix because ALL iSmartDot classes print this
            except:
                print("Mess Sent: " + mess.hex())
            sleep(sleepPeriod)

    def gyroHandler(self, dataRate):
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
            try: ## Check if TCP connection is set up, if not, just print in terminal
                self.gyroDataSig(mess)
                print("Encoded Data " + xValInBytes.hex() + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex()) #Not with SME Prefix because ALL iSmartDot classes print this
            except:
                print("Mess Sent: " + mess.hex())
            sleep(sleepPeriod)

    def startMag(self,  dataRate : int, odr : None):   
        self.sendingMagData = True
        #Create Thread That Handles Accel Data, then kill itself once stopped
        magThread = threading.Thread(target=self.magHandler, args=(dataRate,), daemon=True)        
        magThread.start()
        
    def lightHandler(self, dataRate):
        count = 1
        sleepPeriod = 1/dataRate
        while self.sendingLightData:
            
            sampleCountInBytes = struct.pack('>I', count)[1:4]
            timeStampInBytes : bytearray = struct.pack("<f", datetime.now().timestamp())

            sensorValue = float(self.smartDotData[count % self.smartDotData.__sizeof__()].strip().split(',')[10])
            
            ValInBytes : bytearray = struct.pack('<f', sensorValue) 
            
            mess = sampleCountInBytes + timeStampInBytes + ValInBytes 
            
            print("SmartDotEmulator: %lf" % sensorValue)
            count+=1
            try: ## Check if TCP connection is set up, if not, just print in terminal
                self.lightDataSig(mess)
                print("Encoded Data " + ValInBytes.hex()) #Not with SME Prefix because ALL iSmartDot classes print this
            except:
                print("Mess Sent: " + mess.hex())
            sleep(sleepPeriod)

    def stopMag(self):
        self.sendingMagData = False

    def startAccel(self, dataRate : int, range : int):
        self.sendingAccelData = True
        #Create Thread That Handles Accel Data, then kill itself once stopped
        accelThread = threading.Thread(target=self.accelHandler, args=(dataRate,), daemon=True)        
        accelThread.start()

    def stopAccel(self):
        self.sendingAccelData = False

    def startGyro(self, dataRate : int, range : int):
        self.sendingGyroData = True
        #Create Thread That Handles Accel Data, then kill itself once stopped
        gyroThread = threading.Thread(target=self.gyroHandler, args=(dataRate,), daemon=True)        
        gyroThread.start()

    def stopGyro(self):
        self.sendingGyroData = False

    def startLight(self,  dataRate : int, odr : None):   
        self.sendingLightData = True
        #Create Thread That Handles Accel Data, then kill itself once stopped
        lightThread = threading.Thread(target=self.lightHandler, args=(dataRate,), daemon=True)        
        lightThread.start()

    def stopLight(self):
        self.sendingLightData = False
        