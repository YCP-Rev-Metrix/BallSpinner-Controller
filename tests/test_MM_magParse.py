from BallSpinnerController import *
import unittest
import struct
import asyncio
from mbientlab.metawear import MetaWear, libmetawear, parse_value,  formatTime
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from datetime import datetime

class MetaMotion_Mag_Tests(unittest.TestCase):
    def setUp(self):
        print("Setting Up MetaMotion Connection")
        availDevices = asyncio.run(scanAll())
        self.smartDot = MetaMotion()
        print("Select SmartDot To Connect To")
        consInput = input()
        self.smartDot.connect(tuple(availDevices.keys())[int(consInput)]) # Create a socket object
        self.device = self.smartDot.device
        self.testCallback = FnVoid_VoidP_DataP(self._testHandler) #sets up Data Handler

        #configure Magnetometer
        libmetawear.mbl_mw_mag_bmm150_set_preset(self.device.board, 5)
        self.smartDot.magSignal = libmetawear.mbl_mw_mag_bmm150_get_b_field_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.smartDot.magSignal, None, self.testCallback)

        libmetawear.mbl_mw_mag_bmm150_enable_b_field_sampling(self.device.board)
        self.smartDot.startMagTime = datetime.now().timestamp()
        self.prevTime = datetime.now().timestamp()
        
    def _testHandler(self, ctx, data):    
        #Create fake data handler to pass into magSignal        

        def test(mess):
            try:
                self.currTime  = float(struct.unpack('<f', mess[3:7])[0]) 
                print(1/(self.currTime - self.prevTime))
                print(data.contents.epoch)
                self.prevTime = self.currTime
                pasedData = parse_value(data)
                print(pasedData.timestamp)
                #Can't find any other way to call code from BSC so its copied pasted below:
                bytesData = bytearray([0x0A, 0x00, 0x13, 0x54])
                bytesData.extend(mess)
                
                #Test Msg Type
                self.assertTrue(0x0A == bytesData[0])
                
                #Test Msg Size
                msgSize = int(struct.unpack(">I", b"\x00\x00"+ bytesData[1:3])[0])
                self.assertTrue(0x0013 == msgSize)

                #Tests if Sensor Type is Sent Correcty, in Testing it should be T for Test
                self.assertTrue('T' == chr(bytesData[3]))
                
                #Test Sample Count
                self.assertTrue(self.receivedSampleCount == int(struct.unpack('>I', b'\x00' + bytesData[4:7])[0]))
                self.receivedSampleCount+=1

                #Test All Cartesian Values 
                self.assertAlmostEqual(pasedData.x, struct.unpack('<f', bytesData[11:15])[0],delta=0.01)
                self.assertAlmostEqual(pasedData.y, struct.unpack('<f', bytesData[15:19])[0],delta=0.01)
                self.assertAlmostEqual(pasedData.z, struct.unpack('<f', bytesData[19:23])[0],delta=0.01)

            except AssertionError as e:
                self.fail(f"{e}") #immediately call fail message
                
        self.smartDot.magDataSig = test
        self.smartDot.magDataHandler(ctx,data)
    
    def testDataParsing(self):    
        print("Running Mag Parsing Tests For 10s")
        
        libmetawear.mbl_mw_mag_bmm150_start(self.device.board)
        self.smartDot.MagSampleCount = 0 
        self.receivedSampleCount = 0
        asyncio.run(asyncio.sleep(10))
        self.smartDot.stopMag()
        



