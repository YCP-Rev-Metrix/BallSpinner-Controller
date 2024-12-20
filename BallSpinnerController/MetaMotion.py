from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
import time
from time import sleep
from threading import Event
import struct
from datetime import datetime
import platform
import sys

from .iSmartDot import iSmartDot

class MetaMotion(iSmartDot):

    
    def UUID(self) -> str:
        return "326a9000-85cb-9195-d9dd-464cfbbae75a"
        
    def __init__(self, MAC_Address="", commChannel=None, autoConnect=False):
        self.commsChannel = commChannel
        if autoConnect:
            self.connect(MAC_Address)
    
    def setCommsPort(self, connection): #Check if we need
        self.commsChannel = connection

    def connect(self, MAC_Address) -> bool:
        #print("Attempting to connect to device")
        #print(MAC_Address)
        #try:
            self.device = MetaWear(MAC_Address)
            self.device.connect()
            #set connection parameters 7.5ms connection interval, 0 Slave interval, 6s timeout
            libmetawear.mbl_mw_settings_set_connection_parameters(self.device.board, 7.5, 7.5, 0, 6000)
            
            self.accelCallback = FnVoid_VoidP_DataP(self.accelDataHandler)
            self.magCallback = FnVoid_VoidP_DataP(self.magDataHandler)
            self.gyroCallback = FnVoid_VoidP_DataP(self.gyroDataHandler)
            self.lightCallback = FnVoid_VoidP_DataP(self.lightDataHandler)

            print("Connected to device")
            return True

        #Timeout occured and Connection was unsuccessful     
        #except:
        #    print("Unable to connect to device")
        #    return False
    
    def accelDataHandler(self, ctx, data): 
        #Parse data into Cartesian Values
        parsedData = parse_value(data)

        # Set the Timestamps from the First Received Sample
        if self.AccelSampleCount == 0:
            self.prevAccelEpoch = data.contents.epoch
        timeStamp = (data.contents.epoch - self.prevAccelEpoch)/1000 #Epoch is given in ms
        
        #Pack Sample Count into 3 Byte Big Endian Int
        self.AccelSampleCount += 1
        sampleCountInBytes = struct.pack('>I',self.AccelSampleCount )[1:4]
        
        # Pack Timestamp, and x,y,z into 4 Byte Little Endian Floats
        timeStampInBytes : bytearray = struct.pack("<f", timeStamp)
        xValInBytes : bytearray = struct.pack('<f', parsedData.x) 
        yValInBytes : bytearray = struct.pack('<f', parsedData.y)
        zValInBytes : bytearray = struct.pack('<f', parsedData.z)
        
        mess = sampleCountInBytes + timeStampInBytes + xValInBytes + yValInBytes + zValInBytes

        try: # Check if TCP connection is set up, if not, just print xyz values in terminal
            self.accelDataSig(mess)
            #print("Encoded Data " + xValInBytes.hex() + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex())

        except:    
            print(parsedData)

    def magDataHandler(self, ctx, data):
        #Parse data into Cartesian Values
        parsedData = parse_value(data)

        # Set the Timestamps from the First Received Sample
        if self.MagSampleCount == 0:
            self.prevMagEpoch = data.contents.epoch

        timeStamp = (data.contents.epoch - self.prevMagEpoch)/1000 #Epoch is given in ms

        #Pack Sample Count into 3 Byte Big Endian Int
        self.MagSampleCount += 1
        sampleCountInBytes = struct.pack('>I',self.MagSampleCount )[1:4]
        
        # Pack Timestamp, and x,y,z into 4 Byte Little Endian Floats
        timeStampInBytes : bytearray = struct.pack("<f", timeStamp)
        xValInBytes : bytearray = struct.pack('<f', parsedData.x) 
        yValInBytes : bytearray = struct.pack('<f', parsedData.y)
        zValInBytes : bytearray = struct.pack('<f', parsedData.z)

        mess = sampleCountInBytes + timeStampInBytes + xValInBytes + yValInBytes + zValInBytes
        
        try: # Check if TCP connection is set up, if not, just print xyz values in terminal
            self.magDataSig(mess)
            #print("Encoded Data " + xValInBytes.hex() + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex())
        except Exception as e:
            print(f"Unexpected error in accelDataHandler: {e}")
            print(parsedData)

    def gyroDataHandler(self, ctx, data):
        #Parse data into Cartesian Values
        parsedData = parse_value(data)
        
        # Set the Timestamps from the First Received Sample
        if self.GyroSampleCount == 0:
            self.prevGyroEpoch = data.contents.epoch

        timeStamp = (data.contents.epoch - self.prevGyroEpoch)/1000 #Epoch is given in ms

        #Pack Sample Count into 3 Byte Big Endian Int
        self.GyroSampleCount+=1
        sampleCountInBytes = struct.pack('>I',self.GyroSampleCount )[1:4]
        
        # Pack Timestamp, and x,y,z into 4 Byte Little Endian Floats
        timeStampInBytes : bytearray = struct.pack("<f", timeStamp)
        xValInBytes : bytearray = struct.pack('<f', parsedData.x) 
        yValInBytes : bytearray = struct.pack('<f', parsedData.y)
        zValInBytes : bytearray = struct.pack('<f', parsedData.z)

        mess = sampleCountInBytes + timeStampInBytes + xValInBytes + yValInBytes + zValInBytes
        
        try: # Check if TCP connection is set up, if not, just print in terminal
            self.gyroDataSig(mess)
            print("Encoded Data " + xValInBytes + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex())
        except:
            print(parsedData)
            
    def lightDataHandler(self, ctx, data):
        parsedData = parse_value(data)
        timeStamp = datetime.now().timestamp() - self.startLightTime
        sampleCountInBytes = struct.pack('>I',self.LightSampleCount )[1:4]
        self.LightSampleCount+=1

        timeStampInBytes : bytearray = struct.pack("<f", timeStamp)
        valInBytes : bytearray = struct.pack('<f', parsedData) 

        mess = sampleCountInBytes + timeStampInBytes + valInBytes 
        try:
            self.lightDataSig(mess)
            print("Encoded Data " + valInBytes.hex()+ " 0000 0000")
        except Exception as e:
            print(parsedData)
            print(e)

    def startMag(self,  dataRate : int, odr : None):  
        libmetawear.mbl_mw_mag_bmm150_stop(self.device.board)
        #List of Valid Data as depicted from Metawear API
        magDataRates = {
                            MagBmm150Odr._2Hz  :  2, 
                            MagBmm150Odr._6Hz  :  6,
                            MagBmm150Odr._8Hz  :  8,
                            MagBmm150Odr._10Hz : 10,
                            MagBmm150Odr._15Hz : 15,
                            MagBmm150Odr._20Hz : 20,
                            MagBmm150Odr._25Hz : 25,
                            MagBmm150Odr._30Hz : 30}
        
        #determine actual datarate based from finding value closest to parameter datarate
        dataRate = min(magDataRates, key=lambda k: abs(magDataRates[k] - dataRate))
        libmetawear.mbl_mw_mag_bmm150_configure(self.device.board, 5, 5, dataRate)
       
        self.magSignal = libmetawear.mbl_mw_mag_bmm150_get_b_field_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.magSignal, None, self.magCallback)

        libmetawear.mbl_mw_mag_bmm150_enable_b_field_sampling(self.device.board)
        libmetawear.mbl_mw_mag_bmm150_start(self.device.board)
        self.MagSampleCount = 0

    def stopMag(self):
        print("Stopping Magnetometer sampling")
        libmetawear.mbl_mw_mag_bmm150_stop(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(self.magSignal)
        
    def disconnect(self):
        self.device.disconnect()
      
    def startAccel(self, dataRate : int, range : int):
        
        print("Configuring Accelerometer")
        libmetawear.mbl_mw_acc_set_odr(self.device.board, dataRate)
        print("ODR SET")        
        libmetawear.mbl_mw_acc_set_range(self.device.board, range)  
        print("RANGE SET")
        libmetawear.mbl_mw_acc_write_acceleration_config(self.device.board)

        print("Subscribing to acceleration data")
        self.accelSignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.accelSignal, None, self.accelCallback)
           
        print("Enabling acceleration sampling")
        libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
        
        if(self.accelSignal != None):
            libmetawear.mbl_mw_acc_start(self.device.board)
        else:
            print("Unable to Start Polling Data: Acceleration Not Enabled")
        self.AccelSampleCount = 0

    def stopAccel(self):
        print("Stopping acceleration sampling")
        libmetawear.mbl_mw_acc_stop(self.device.board)
        libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(self.accelSignal)
    
    def startGyro(self, dataRate : int, range : int):
        # Set ODR to 100Hz
        libmetawear.mbl_mw_gyro_bmi160_set_odr(self.device.board, 100)

        # Set data range to +/250 degrees per second
        libmetawear.mbl_mw_gyro_bmi160_set_range(self.device.board, range)

        # Write the changes to the sensor
        libmetawear.mbl_mw_gyro_bmi160_write_config(self.device.board)

        self.gyroSig = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(self.device.board)

        libmetawear.mbl_mw_datasignal_subscribe(self.gyroSig, None, self.gyroCallback)
        libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(self.device.board)
        
        libmetawear.mbl_mw_gyro_bmi160_start(self.device.board)
        self.GyroSampleCount = 0

    def stopGyro(self):
        print("Stopping Gyroscope Sampling")
        libmetawear.mbl_mw_gyro_bmi160_stop(self.device.board)
        libmetawear.mbl_mw_gyro_bmi160_disable_rotation_sampling(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(self.gyroSig)
        
    def startLight(self,  dataRate : int, odr : None):
        libmetawear.mbl_mw_als_ltr329_set_gain(self.device.board, AlsLtr329Gain._96X)
        libmetawear.mbl_mw_als_ltr329_set_integration_time(self.device.board, AlsLtr329IntegrationTime._400ms)
        libmetawear.mbl_mw_als_ltr329_set_measurement_rate(self.device.board, AlsLtr329MeasurementRate._1000ms)
        libmetawear.mbl_mw_als_ltr329_write_config(self.device.board)

        self.lightSig = libmetawear.mbl_mw_als_ltr329_get_illuminance_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.lightSig, None, self.lightCallback)
        
        self.startLightTime = datetime.now().timestamp()
        libmetawear.mbl_mw_als_ltr329_start(self.device.board)
        self.LightSampleCount = 0

    def stopLight(self):
        pass

    def turnOnRedLED(self):
        pattern = LedPattern(delay_time_ms= 5000, repeat_count= Const.LED_REPEAT_INDEFINITELY)
        libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
        libmetawear.mbl_mw_led_write_pattern(self.device.board, byref(pattern), LedColor.RED)        
        libmetawear.mbl_mw_led_play(self.device.board)

    def turnOnBlueLED(self):
        pattern = LedPattern(delay_time_ms= 5000, repeat_count= Const.LED_REPEAT_INDEFINITELY)
        libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
        libmetawear.mbl_mw_led_write_pattern(self.device.board, byref(pattern), LedColor.BLUE)
        libmetawear.mbl_mw_led_play(self.device.board)

    def turnOnGreenLED(self):
        pattern = LedPattern(delay_time_ms= 5000, repeat_count= Const.LED_REPEAT_INDEFINITELY)
        libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
        libmetawear.mbl_mw_led_write_pattern(self.device.board, byref(pattern), LedColor.GREEN)
        libmetawear.mbl_mw_led_play(self.device.board)

    def turnOffLED(self):
        libmetawear.mbl_mw_led_stop_and_clear(self.device.board)


