from package import *
import unittest
import struct
import asyncio
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from datetime import datetime

class Tests(unittest.TestCase):
    def __init__(self):
        print("Setting Up SmartDot Connection")
        availDevices = asyncio.run(ConnectionTools.scanAll())
        self.smartDot = MetaMotion()
        print("Select SmartDot To Connect To")
        consInput = input()
        self.smartDot.connect(tuple(availDevices.keys())[int(consInput)])# Create a socket object
        self.device = self.smartDot.device
        self.testCallback = FnVoid_VoidP_DataP(self.testHandler)
        
    def MagParsingTest(self):
        libmetawear.mbl_mw_mag_bmm150_set_preset(self.device.board, MagBmm150Preset.HIGH_ACCURACY)
        self.magSignal = libmetawear.mbl_mw_mag_bmm150_get_b_field_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.magSignal, None, self.testCallback)

        libmetawear.mbl_mw_mag_bmm150_enable_b_field_sampling(self.device.board)
        self.startMagTime = datetime.now()
        libmetawear.mbl_mw_mag_bmm150_start(self.device.board)
        self.smartDot.MagSampleCount = 0 
        #Create fake data handler to pass into accelSignal
        
    def testHandler(self, ctx, data):    
        
        def test(mess):
            pasedData = parse_value(data)
            self.assertAlmostEqual(pasedData.x, struct.unpack('<f', mess[7:11])[0],delta=0.01)
            self.assertAlmostEqual(pasedData.y, struct.unpack('<f', mess[11:15])[0],delta=0.01)
            self.assertAlmostEqual(pasedData.z, struct.unpack('<f', mess[15:19])[0],delta=0.01)
            #Can't find any other way to call code from BSC so its copied pasted below:
            bytesData = bytearray([0x8A, 0x00, 0x13, 0x54])
            bytesData.extend(mess)
            self.assertTrue(0x8A == bytesData[0])
            msgSize = int(struct.unpack(">I", b"\x00\x00"+ bytesData[1:3])[0])
            self.assertTrue(0x0013 == msgSize)
            #Tests if Sensor Type is Sent Correcty, in Testing it should be T for Test
            self.assertTrue('T' == chr(bytesData[3]))
            self.assertAlmostEqual(pasedData.x, struct.unpack('<f', bytesData[11:15])[0],delta=0.01)
            self.assertAlmostEqual(pasedData.y, struct.unpack('<f', bytesData[15:19])[0],delta=0.01)
            self.assertAlmostEqual(pasedData.z, struct.unpack('<f', bytesData[19:23])[0],delta=0.01)

        self.smartDot.magDataSig = test
        self.smartDot.magDataHandler(ctx,data)
        
        
        #



test = Tests()
test.MagParsingTest()
asyncio.run(asyncio.sleep(10))

