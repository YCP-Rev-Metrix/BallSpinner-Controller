from BallSpinnerController import *
import unittest
import struct
import asyncio
from mbientlab.metawear import MetaWear, libmetawear, parse_value
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
            
        # Set ODR to 100Hz
        libmetawear.mbl_mw_gyro_bmi160_set_odr(self.device.board, GyroBoschOdr._100Hz)

        # Set data range to +/250 degrees per second
        libmetawear.mbl_mw_gyro_bmi160_set_range(self.device.board, 2)

        # Write the changes to the sensor
        libmetawear.mbl_mw_gyro_bmi160_write_config(self.device.board)

        self.smartDot.gyroSig = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(self.device.board)

        libmetawear.mbl_mw_datasignal_subscribe(self.smartDot.gyroSig, None, self.testCallback)
        libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(self.device.board)
        
        
        
        
    def _testHandler(self, ctx, data):    
        #Create fake data handler to pass into accelSignal        

        def test(mess):
            try:
                pasedData = parse_value(data)
                self.assertAlmostEqual(pasedData.x, struct.unpack('<f', mess[7:11])[0],delta=0.01)
                self.assertAlmostEqual(pasedData.y, struct.unpack('<f', mess[11:15])[0],delta=0.01)
                self.assertAlmostEqual(pasedData.z, struct.unpack('<f', mess[15:19])[0],delta=0.01)
                #Can't find any other way to call code from BSC so its copied pasted below:
                bytesData = bytearray([0x0A, 0x00, 0x13, 0x54])
                bytesData.extend(mess)
                self.assertTrue(0x0A == bytesData[0])
                msgSize = int(struct.unpack(">I", b"\x00\x00"+ bytesData[1:3])[0])
                    
                self.assertTrue(0x0013 == msgSize)
                #Tests if Sensor Type is Sent Correcty, in Testing it should be T for Test
                self.count = int(struct.unpack('>I',b"\x00" + bytesData[4:7])[0])
                                
                timestamp = struct.unpack('<f', bytesData[7:11])[0]
                print(timestamp)

                self.assertTrue('T' == chr(bytesData[3]))
                self.assertAlmostEqual(pasedData.x, struct.unpack('<f', bytesData[11:15])[0],delta=0.01)
                self.assertAlmostEqual(pasedData.y, struct.unpack('<f', bytesData[15:19])[0],delta=0.01)
                self.assertAlmostEqual(pasedData.z, struct.unpack('<f', bytesData[19:23])[0],delta=0.01)

            except AssertionError as e:
                self.fail(f"{e}") #immediately call fail message

        self.smartDot.gyroDataSig = test
        self.smartDot.gyroDataHandler(ctx,data)
    
    def testDataParsing(self):    
        print("Running Gyro Parsing Tests For 10s")
        libmetawear.mbl_mw_gyro_bmi160_start(self.device.board)
        self.smartDot.startGyroTime = datetime.now().timestamp()
        self.smartDot.GyroSampleCount = 0
        
        asyncio.run(asyncio.sleep(10))
        self.smartDot.stopGyro()
        



