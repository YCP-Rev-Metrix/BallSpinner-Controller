from .iAuxSensor import iAuxSensor
import busio
import board
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ads

class CurrentSensor(iAuxSensor): 
     
    def __init__(self, ADC_IN : int = 1) -> bool: 
        i2cConfig = busio.I2C(board.SCL, board.SDA)
        adc = ads.ADS1115(i2cConfig)
        ads.gain = 1        
        adc_inputPin = [ads.P0, ads.P1, ads.P2]
        self.chan = AnalogIn(adc, adc_inputPin[ADC_IN])
        self.ref  = AnalogIn(adc, ads.P3) 
        #ASSUMING 5v RAIL IS PASSED in to Pin 3
            
    def readData(self): 
        
        return self.chan.voltage - (self.ref.voltage/2) 