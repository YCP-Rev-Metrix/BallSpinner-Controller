 
from abc import ABCMeta, abstractmethod

class iSmartDot(metaclass=ABCMeta): 

    #Confirm all class under this interface have called all functions
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        return (hasattr(subclass, 'connect') and 
                hasattr(subclass, 'disconnect'))    

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
    def UUID(self) -> str: ...
    # Scan Bluetooth Devices and filters for specific devices

