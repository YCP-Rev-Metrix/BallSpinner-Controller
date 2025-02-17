 
from abc import ABCMeta, abstractmethod

class iSmartDot(metaclass=ABCMeta): 

    
    #Confirm all class under this interface have called all functions
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        return (hasattr(subclass, 'connect') and 
                hasattr(subclass, 'disconnect'))    

    def setSampleRates(self, XL=None, GY=None, MG=None, LT=None):
        #Set any Sampling Rates that were passed in
        if XL != None: self.XL_SampleRate = XL
        if GY != None: self.GY_SampleRate = GY
        if MG != None: self.MG_SampleRate = MG
        if LT != None: self.LT_SampleRate = LT

    def setRanges(self, XL=None, GY=None, MG=None, LT=None):
        #Set any Sampling Rates that were passed in
        if XL != None: self.XL_Range = XL
        if GY != None: self.GY_Range = GY
        if MG != None: self.MG_Range = MG
        if LT != None: self.LT_Range = LT
        
    @abstractmethod
    def connect(self, MAC_Address) -> bool:
        pass

    @abstractmethod
    def disconnect(MAC_Address):
        pass
    
    def setDataSignals(self, accelDataSig, gyroDataSig, magDataSig, lightDataSig):
        self.accelDataSig =  accelDataSig
        self.gyroDataSig = gyroDataSig
        self.magDataSig = magDataSig
        self.lightDataSig = lightDataSig

    @abstractmethod
    def startMag(self,  dataRate : int, odr : None):   
        pass

    @abstractmethod
    def stopMag(self):
        pass

    @abstractmethod
    def startAccel(self, dataRate : int, range : int):
        pass

    @abstractmethod
    def stopAccel(self):
        pass

    @abstractmethod
    def startGyro(self, dataRate : int, range : int):
        pass

    @abstractmethod
    def stopGyro(self):
        pass
    
    @abstractmethod
    def startLight(self,  dataRate : int, odr : None):
        pass

    @abstractmethod
    def stopLight(self):
        pass 

    @abstractmethod
    def UUID(self) -> str: 
        pass
        # Scan Bluetooth Devices and filters for specific devices

    def sendConfigSettings(self) -> bytearray:
        configSettingsBytes = bytearray([0, 0, 0, 0, 0, 0, 0, 0])
        
        for x in self.XL_availSampleRate:
            if x == 12.5:  configSettingsBytes[0] |= 1
            if x ==   25:  configSettingsBytes[0] |= 2
            if x ==   50:  configSettingsBytes[0] |= 4
            if x ==  100:  configSettingsBytes[0] |= 8
            if x ==  200:  configSettingsBytes[0] |= 16
            if x ==  400:  configSettingsBytes[0] |= 32
            if x ==  800:  configSettingsBytes[0] |= 64
            if x ==  1600: configSettingsBytes[0] |= 128

        for x in self.XL_availRange:
            if x ==    2:  configSettingsBytes[1] |= 1
            if x ==    4:  configSettingsBytes[1] |= 2
            if x ==    8:  configSettingsBytes[1] |= 4
            if x ==   16:  configSettingsBytes[1] |= 8
            
        for x in self.GY_availSampleRate:
            if x ==   25:  configSettingsBytes[2] |= 1
            if x ==   50:  configSettingsBytes[2] |= 2
            if x ==  100:  configSettingsBytes[2] |= 4
            if x ==  200:  configSettingsBytes[2] |= 8
            if x ==  400:  configSettingsBytes[2] |= 16
            if x ==  800:  configSettingsBytes[2] |= 32
            if x ==  1600: configSettingsBytes[2] |= 64
            if x ==  3200: configSettingsBytes[2] |= 128
            if x ==  6400: configSettingsBytes[3] |= 128

        for x in self.GY_availRange:
            if x ==    125:  configSettingsBytes[3] |= 1
            if x ==    250:  configSettingsBytes[3] |= 2
            if x ==    500:  configSettingsBytes[3] |= 4
            if x ==   1000:  configSettingsBytes[3] |= 8
            if x ==   2000:  configSettingsBytes[3] |= 16


        for x in self.MG_availSampleRate:
            if x == 12.5:  configSettingsBytes[4] |= 1
            if x ==   25:  configSettingsBytes[4] |= 2
            if x ==   50:  configSettingsBytes[4] |= 4
            if x ==  100:  configSettingsBytes[4] |= 8
            if x ==  200:  configSettingsBytes[4] |= 16
            if x ==  400:  configSettingsBytes[4] |= 32
            if x ==  800:  configSettingsBytes[4] |= 64
            if x ==  1600: configSettingsBytes[4] |= 128
        
        for x in self.MG_availRange:
            if x ==    2:  configSettingsBytes[3] |= 1
            if x ==    4:  configSettingsBytes[3] |= 2
            if x ==    8:  configSettingsBytes[3] |= 4
            if x ==   16:  configSettingsBytes[3] |= 8


        '''
        for x in self.smartDot.XL_availSampleRate:
            if x ==    2: XL_rangeByte |= 1
            if x ==    4: XL_rangeByte |= 2
            if x ==    8: XL_rangeByte |= 4
            if x ==   16: XL_rateByte  |= 8
        '''     
        
        return configSettingsBytes 