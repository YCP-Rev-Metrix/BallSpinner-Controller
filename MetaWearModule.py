from __future__ import print_function
from mbientlab.metawear import MetaWear
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
import asyncio

from iSmartDot import iSmartDot
#from pymetawear.client import MetaWearClient

import platform

class MetaMotion(iSmartDot):
    def __init__(self):
        self.UUID = "326a9000-85cb-9195-d9dd-464cfbbae75a"
        self.mode = "Not_Initialized"
        pass

    #Scans for Metawear Devices and appends to devices list
    async def scan(self, devices : dict):
        self.mode = "Scanning"
        selection = -1
        #Continuously rescans for MetaWear Devices
        print("scanning for devices...")

        #Check if the Bluetooth device has the MetaWear UUID
        def handler(result):
            if result.has_service_uuid("326a9000-85cb-9195-d9dd-464cfbbae75a"):
               devices[result.mac] = result.name
        BleScanner.set_handler(handler)
        BleScanner.start()

        while self.mode == "Scanning":
            i = 0
            #update list every 5s
            await asyncio.sleep(15.0)            
            for address, name in six.iteritems(devices):
                print 
                print("[%d] %s (%s)" % (i, address, name))
                i+= 1
           
            break

        BleScanner.stop()
        print
        print("Done Scanning")
            ## remo

        
    def connect():
        pass
    
    def disconnect(MAC_Address):
        return super().disconnect()