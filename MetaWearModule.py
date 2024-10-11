from __future__ import print_function
from mbientlab.metawear import MetaWear
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from time import sleep

import platform
import six

def scan():
    # Requires: sudo pip3 install metawear
    # usage: sudo python3 scan_connect.py


    selection = -1
    devices = None

    #continuously rescans for MetaWear Devices
    while selection == -1:
        print("scanning for devices...")
        devices = {}
        def handler(result):
            if result.has_service_uuid("326a9000-85cb-9195-d9dd-464cfbbae75a"):
                devices[result.mac] = result.name


        BleScanner.set_handler(handler)
        BleScanner.start()

        sleep(10.0)
        BleScanner.stop()

        i = 0
        ## remo
        for address, name in six.iteritems(devices):
            print 
            print("[%d] %s (%s)" % (i, address, name))
            i+= 1

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
