from .iAuxSensor import iAuxSensor
import busio
import board
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ads

class CurrentSensor(iAuxSensor): 
     
    def __init__(self, GPIOPin : int = 1) -> bool: 
        i2cConfig = busio.I2C(board.SCL, board.SDA)
        adc = ads.ADS1115(i2cConfig)
        ads.gain = 1        
        
        self.chan = AnalogIn(adc, ads.P0)
            
    def readData(self): 
        return self.chan.voltage