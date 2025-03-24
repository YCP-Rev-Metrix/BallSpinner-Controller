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
import random

from .iSmartDot import iSmartDot

class MetaMotion(iSmartDot):

    XL_availSampleRate = [12.5, 25, 50, 100, 200, 400, 800]
    XL_availRange = [2,4,8,16]

    GY_availSampleRate = [25, 50, 100, 200, 400, 800, 1600]
    GY_availRange = [125,250,500,1000,2000]

    
    MG_availSampleRate = [2, 4, 6, 8, 10, 15, 20, 25, 30]
    MG_availRange      = [2500]

    LT_availSampleRate = [.5, 1, 2, 5, 10, 20]
    LT_availRange = [600, 1300, 8000, 16000, 32000, 64000]
    
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
            
            #setup event loops
            self.accelCallback = FnVoid_VoidP_DataP(self.accelDataHandler)
            self.magCallback = FnVoid_VoidP_DataP(self.magDataHandler)
            self.gyroCallback = FnVoid_VoidP_DataP(self.gyroDataHandler)
            self.lightCallback = FnVoid_VoidP_DataP(self.lightDataHandler)

            #I2C Reading setup
            self.XL_ODR_Callback = FnVoid_VoidP_DataP(self.i2c_data_handler)
            #0x68 is bmi270 i2c addr. 0x40 is odr register addr.
            self.XL_ODR_parameters= I2cReadParameters(device_addr= 0x68, register_addr= 0x40)


            #set configurabe settings for each sensor's Rate and Range
            self.XL_availSampleRate = MetaMotion.XL_availSampleRate
            self.XL_availRange = MetaMotion.XL_availRange
            self.GY_availSampleRate = MetaMotion.GY_availSampleRate
            self.GY_availRange = MetaMotion.GY_availRange
            self.MG_availSampleRate = MetaMotion.MG_availSampleRate
            self.MG_availRange = MetaMotion.MG_availRange
            self.LT_availRange = MetaMotion.LT_availRange
            self.LT_availSampleRate = MetaMotion.LT_availSampleRate

            #set default Sample Rates and Ranges
            self.setSampleRates(XL=100, GY=100, MG=10, LT=.5)
            #self.setSampleRanges(XL=100, GY=100, MG=10)

            self.XL_Range = 2
            self.GY_Range = 2
            
            self.MG_SampleRate = 10
        
            print("Connected to device")
            return True
    
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

        except Exception as e:
            print(parsedData)
            print(e)


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
            print(f"Unexpected error in MGDataHandler: {e}")
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
           # print("Encoded Data " + xValInBytes.hex() + ' ' + yValInBytes.hex() + ' ' + zValInBytes.hex())
        except Exception as e:
            print(parsedData)
            print(e)

            
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
        except Exception as e:
            print(parsedData)
            print(e)

    def startMag(self):  
        libmetawear.mbl_mw_mag_bmm150_stop(self.device.board)
        libmetawear.mbl_mw_mag_bmm150_configure(self.device.board, 5, 5, self.MG_SampleRate)
       
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
      
    # Define a callback function to handle data
    def i2c_data_handler(self, ctx, data):
        data_obj = data.contents
        print(f"Raw Data: {data_obj}")
        print("Datadata%s -> %s &  %s" % (self.device.address, parse_value(data), data.contents))
        #print("ur problem here bro")DatadataC8:30:26:28:92:4A -> [] &  {epoch : 1742670940955, extra : 4108379404, value : 4098885936, type_id : 4, length : 0}
    
    def startAccel(self):
        
        print("Configuring Accelerometer")
        libmetawear.mbl_mw_acc_set_odr(self.device.board, self.XL_SampleRate)
        print("ODR SET")        
        libmetawear.mbl_mw_acc_set_range(self.device.board, self.XL_Range)  
        print("RANGE SET")
        libmetawear.mbl_mw_acc_write_acceleration_config(self.device.board)

        print("Subscribing to acceleration data")
        self.accelSignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.accelSignal, None, self.accelCallback)
           
        print("Enabling acceleration sampling")
        libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
        
        if(self.accelSignal != None):
            libmetawear.mbl_mw_acc_start(self.device.board)
            # self.i2c_signal = libmetawear.mbl_mw_i2c_get_data_signal(self.device.board, 1, 0xA)
            # libmetawear.mbl_mw_datasignal_subscribe(self.i2c_signal, None, self.XL_ODR_Callback)
            # print("Now reading data signal with parameters")
            # libmetawear.mbl_mw_datasignal_read_with_parameters(self.i2c_signal, byref(self.XL_ODR_parameters))
        else:
            print("Unable to Start Polling Data: Acceleration Not Enabled")
        self.AccelSampleCount = 0

       

    def stopAccel(self):
        print("Stopping acceleration sampling")
        libmetawear.mbl_mw_acc_stop(self.device.board)
        libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(self.accelSignal)
    
    def startGyro(self):
        # Set ODR to 100Hz
        libmetawear.mbl_mw_gyro_bmi160_set_odr(self.device.board, self.GY_SampleRate)

        # Set data range to +/250 degrees per second
        libmetawear.mbl_mw_gyro_bmi160_set_range(self.device.board, self.GY_Range)

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
        
    def startLight(self):
        libmetawear.mbl_mw_als_ltr329_set_gain(self.device.board, AlsLtr329Gain._96X)
        libmetawear.mbl_mw_als_ltr329_set_integration_time(self.device.board, self.LT_IntRate)
        libmetawear.mbl_mw_als_ltr329_set_measurement_rate(self.device.board, self.LT_SampleRate)
        libmetawear.mbl_mw_als_ltr329_write_config(self.device.board)

        self.lightSig = libmetawear.mbl_mw_als_ltr329_get_illuminance_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.lightSig, None, self.lightCallback)
        
        self.startLightTime = datetime.now().timestamp()
        libmetawear.mbl_mw_als_ltr329_start(self.device.board)
        self.LightSampleCount = 0

    def stopLight(self):
        libmetawear.mbl_mw_als_ltr329_stop(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(self.lightSig)



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

    def setSampleRates(self, XL=None, GY=None, MG=None, LT=None):
        if XL != None: 
            #Setting the Sample Rate is done in the API based on
            #Set Sample Rate
            self.XL_SampleRate = XL
            print("Accelerometer Set To %sHz " % self.XL_SampleRate)

        if GY != None: 
            #Create Mapping of Enums to Sample Rates

            #List of Valid Data as depicted from Metawear API
            GYDataRates = {
                    GyroBoschOdr._25Hz   :   25,
                    GyroBoschOdr._50Hz   :   50, 
                    GyroBoschOdr._100Hz  :  100,
                    GyroBoschOdr._200Hz  :  200,
                    GyroBoschOdr._400Hz  :  400,
                    GyroBoschOdr._800Hz  :  800,
                    GyroBoschOdr._1600Hz : 1600,
                    GyroBoschOdr._3200Hz : 3200
            }
            #Calculate Closest sample rate of what was entered vs. what is possible to set
            dataRate = min(GYDataRates, key=lambda k: abs(GYDataRates[k] - GY))

            print("Gyroscope Set To %sHz " % GYDataRates[dataRate])
            
            #Choose Enum associated with set value
            magDataRates = tuple(GYDataRates.keys())
            self.GY_SampleRate = GYDataRates[dataRate]
        
        if MG != None: 
            #Create Mapping of Enums to Sample Rates

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
            
            #Calculate Closest sample rate of what was entered vs. what is possible to set
            dataRate = min(magDataRates, key=lambda k: abs(magDataRates[k] - MG))

            print("Magnetometer Set To %sHz " % magDataRates[dataRate])
            
            #Choose Enum associated with set value
            magDataRates = tuple(magDataRates.keys())
            self.MG_SampleRate = magDataRates[dataRate]

        if LT != None: 

            #List of Valid Data as depicted from Metawear API
            LTDataRates = {
                    AlsLtr329MeasurementRate._2000ms : .5,
                    AlsLtr329MeasurementRate._1000ms :  1, 
                    AlsLtr329MeasurementRate._500ms  :  2,
                    AlsLtr329MeasurementRate._200ms  :  5,
                    AlsLtr329MeasurementRate._100ms  : 10,
                    AlsLtr329MeasurementRate._50ms   : 20 
            }

            #List of Measurement Times associated with each Sample Rate as depicted from Metawear API
            #Integration Time < Sample Rate
            LTIntegrationTime = [
                AlsLtr329IntegrationTime._400ms,
                AlsLtr329IntegrationTime._400ms,
                AlsLtr329IntegrationTime._400ms,
                AlsLtr329IntegrationTime._150ms,
                AlsLtr329IntegrationTime._100ms,
                AlsLtr329IntegrationTime._50ms
            ] 

            #Calculate Closest sample rate of what was entered vs. what is possible to set
            dataRate = min(LTDataRates, key=lambda k: abs(LTDataRates[k] - LT))

            print("Light Set To %sHz " % LTDataRates[dataRate])
            
            #Choose Enum associated with set value
            LTDataRates = tuple(LTDataRates.keys())
            self.LT_SampleRate = LTDataRates[dataRate]
            self.LT_IntRate = LTIntegrationTime[dataRate]