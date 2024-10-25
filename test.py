from mbientlab.metawear import MetaWear, libmetawear
import ConnectionTools
import MetaMotion
import SmartDotEmulator
from time import sleep

# When scan cancelled, connect to first SmartDot in Dict
smartDot = ConnectionTools.MetaMotion()

findDotMacAddress = ConnectionTools.asyncio.run(ConnectionTools.scanAll())

#connects to first SmartDot module found 
smartDot.connect(findDotMacAddress.popitem()[0])

smartDot.configAccel(200, 2)

#Samples for 99 seconds, cancel to stop
try: 
    smartDot.startAccel()
    sleep(99)
except:
    smartDot.stopAccel()

