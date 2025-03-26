from .iAuxSensor import iAuxSensor
import struct

class AuxSensorSimulator(iAuxSensor): 
    
    def __init__(self, GPIOPin : int):
        self.value = 0.00

    def readData(self): 
        value = self.value
        self.value += .001
        data: bytearray = struct.pack('<f', value) 

        return data