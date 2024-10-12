from MetaWearModule import MetaMotion
from iSmartDot import iSmartDot
import asyncio
from mbientlab.warble import BleScanner
import six

## Scan All 9DOF modules
#iSmartDot.UUID

smartDot = [MetaMotion(), MetaMotion()]
UUID= "326a9000-85cb-9195-d9dd-464cfbbae75a"
availDevices = {}

tasks = []
print("Starting Scan")

async def scanAll():
        #self.mode = "Scanning"
        selection = -1
        #Continuously rescans for MetaWear Devices
        print("scanning for devices...")

        #Check if the Bluetooth device has ANY UUID's from any of the iSmartDot Modules
        def handler(result):
            if result.has_service_uuid(UUID):
               availDevices[result.mac] = result.name
        BleScanner.set_handler(handler)
        BleScanner.start()
        
        try :
            i = 0
            while True: #self.mode == "Scanning":
                #update list every 5s
                await asyncio.sleep(5.0)  

                #print all BLE devices found and append to connectable list                
                count = 0
                for address, name in six.iteritems(availDevices):
                    if count >= i :
                        print("[%d] %s (%s)" % (i, address, name))
                        i += 1
                    count += 1


                #Clear buffer
                availDevices.clear 

        except : 
            print()
            """
    async with asyncio.TaskGroup() as tg:    
        for x in range(len(smartDot)):
            tg.create_task(smartDot[x].scan(devices))


    
        msg = "Select your device (-1 to rescan): "
        selection = int(raw_input(msg) if platform.python_version_tuple()[0] == '2' else input(msg))

        address = list(devices)[selection]
        print("Connecting to %s..." % (address))
        device = MetaWear(address)
        device.connect()

        print("Connected to " + device.address + " over " + ("USB" if device.usb.is_connected else "BLE"))
        print("Device information: " + str(device.info))
        sleep(5.0)

        device.disconnect()
        sleep(1.0)
        print("Disconnected")    
    """

asyncio.run(scanAll())
