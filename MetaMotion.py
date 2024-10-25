from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from time import sleep
from threading import Event

import platform
import sys

from iSmartDot import iSmartDot

class MetaMotion(iSmartDot):

    def UUID(self) -> str:
        return "326a9000-85cb-9195-d9dd-464cfbbae75a"
        
    def connect(self, MAC_Address):
        print("Attempting to connect to device")
        print(MAC_Address)
        try:
            self.device = MetaWear(MAC_Address)
            self.device.connect()
            #set connection parameters 7.5ms connection interval, 0 Slave interval, 6s timeout
            libmetawear.mbl_mw_settings_set_connection_parameters(self.device.board, 7.5, 7.5, 0, 6000)
            self.callback = FnVoid_VoidP_DataP(self.data_handler)
            self.samples = 0

    
        #Timeout occured and Connection was unsuccessful     
        except WarbleException:
            print("Unable to connect to device")
            return False
    
    def data_handler(self, ctx, data):
        print("%s -> %s" % (self.device.address, parse_value(data)))
        self.samples+= 1

    def disconnect(MAC_Address):
        return super().disconnect()
    

#for s in states:
    #print("Configuring device")
    def configAccel(self, dataRate, range):
        print("Configuring Device")
        libmetawear.mbl_mw_acc_set_odr(self.device.board, dataRate)
        libmetawear.mbl_mw_acc_set_range(self.device.board, range)  
        libmetawear.mbl_mw_acc_write_acceleration_config(self.device.board)

        print("Subscribing to acceleration data")
        self.accelSignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
        libmetawear.mbl_mw_datasignal_subscribe(self.accelSignal, None, self.callback)
           
        print("Enabling acceleration sampling")
        libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
        
    def startAccel(self):
        if(self.accelSignal):
            libmetawear.mbl_mw_acc_start(self.device.board)
        else:
            print("Unable to Start Polling Data: Acceleration Not Enabled")
        

    def stopAccel(self):
        print("Stopping acceleration sampling")
        libmetawear.mbl_mw_acc_stop(self.device.board)
        libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)
        libmetawear.mbl_mw_datasignal_unsubscribe(self.accelSignal)

        print("Total Samples Received: %d" % self.samples)