from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from time import sleep
from threading import Event

from datetime import datetime
import platform
import sys

from iSmartDot import iSmartDot

class MetaMotion(iSmartDot):

    
    def UUID(self) -> str:
        return "326a9000-85cb-9195-d9dd-464cfbbae75a"
        
    def MetaMotion(self, MAC_Address):
        self.connect(MAC_Address)
        
    def setCommsPort(self, connection):
        self.connection = connection

    def connect(self, MAC_Address) -> bool:
        print("Attempting to connect to device")
        print(MAC_Address)
        try:
            if self.connection == None:
                print("socket not set")
            self.device = MetaWear(MAC_Address)
            cnnected = self.device.connect()
            print(cnnected)
            #set connection parameters 7.5ms connection interval, 0 Slave interval, 6s timeout
            libmetawear.mbl_mw_settings_set_connection_parameters(self.device.board, 7.5, 7.5, 0, 6000)
            self.callback = FnVoid_VoidP_DataP(self.data_handler)
            self.samples = 0
            return True

        #Timeout occured and Connection was unsuccessful     
        except:
            print("Unable to connect to device")
            return False
    
    def data_handler(self, ctx, data):
        self.prevAccelTime = self.startAccelTime
        self.startAccelTime = datetime.now()
        sampleRate = int(1/(self.startAccelTime.microsecond - self.prevAccelTime.microsecond)*1000000)
        
        #if connection was established, send data to socket
        if self.connection !=  None:
             self.connection.sendall(bytes("%s -> %s" % (sampleRate, parse_value(data)), 'utf-8'))
        print("%s -> %s" % (sampleRate, parse_value(data)))
        self.samples+= 1

    def disconnect(MAC_Address):
        return super().disconnect()

    def configAccel(self, dataRate : int, range : int):

        print("Configuring Device")
        libmetawear.mbl_mw_acc_set_odr(self.device.board, dataRate)
        print("ODR SET")        
        libmetawear.mbl_mw_acc_set_range(self.device.board, range)  
        print("RANGE SET")
        libmetawear.mbl_mw_acc_write_acceleration_config(self.device.board)

        print("Subscribing to acceleration data")
        self.accelSignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
        print(self.accelSignal)
        libmetawear.mbl_mw_datasignal_subscribe(self.accelSignal, None, self.callback)
           
        print("Enabling acceleration sampling")
        libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
        
    def startAccel(self):

        if(self.accelSignal != None):
            self.startAccelTime = datetime.now()
            libmetawear.mbl_mw_acc_start(self.device.board)
        else:
            print("Unable to Start Polling Data: Acceleration Not Enabled")
        
    def stopAccel(self):
        print("Stopping acceleration sampling")
        libmetawear.mbl_mw_acc_stop(self.device.board)
        libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(self.accelSignal)

        print("Total Samples Received: %d" % self.samples)
    
    def configMag(self, dataRate, range):
        print("Configuring Device")
        libmetawear.mbl_mw_mag_set_odr(self.device.board, dataRate)
        libmetawear.mbl_mw_mag_set_range(self.device.board, range)  
        libmetawear.mbl_mw_mag_write_acceleration_config(self.device.board)

        print("Subscribing to acceleration data")
        self.accelSignal = libmetawear.mbl_mw_mag_get_acceleration_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.accelSignal, None, self.callback)
           
        print("Enabling acceleration sampling")
        libmetawear.mbl_mw_mag_enable_acceleration_sampling(self.device.board)

    def turnOnRedLED(self):
        print()
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

    def getActiveSignals(self):
        self.active_signals = libmetawear.mbl_mw_datasignal_get_active_datasignals(self.device.board)
        print(self.active_signals)
