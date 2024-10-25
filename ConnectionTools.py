import asyncio
from mbientlab.warble import BleScanner
import six
from MetaMotion import MetaMotion
from SmartDotEmulator import SmartDotEmulator
from iSmartDot import iSmartDot

#Scans all modules to see which to connect to
async def scanAll() -> dict:
    
    availDevices = {}
    smartDot : iSmartDot = [MetaMotion(), SmartDotEmulator()]

    #self.mode = "Scanning"
    selection = -1
    #Continuously rescans for MetaWear Devices
    print("scanning for devices...")

    #Check if the Bluetooth device has ANY UUID's from any of the iSmartDot Modules
    def handler(result):
        for listedConnect in range(len(smartDot)):
            if result.has_service_uuid(smartDot[listedConnect].UUID()):
                availDevices[result.mac] = result.name

    BleScanner.set_handler(handler)
    BleScanner.start()
    
    try :
        i = 0
        while True: #self.mode == "Scanning":
            #update list every 5s
            await asyncio.sleep(1.0)  

            #print all BLE devices found and append to connectable list                
            count = 0
            for address, name in six.iteritems(availDevices):
                if count >= i :
                    print("[%d] %s (%s)" % (i, address, name))
                    i += 1
                count += 1

    except : 
        return availDevices

