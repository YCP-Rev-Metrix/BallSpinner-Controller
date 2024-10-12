 
from abc import ABCMeta, ABC, abstractmethod

class iSmartDot(metaclass=ABCMeta): 

    #Confirm all class under this interface have called all functions
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        return (hasattr(subclass, 'connect') and 
                hasattr(subclass, 'disconnect'))    

    @abstractmethod
    def connect(MAC_Address):
        pass

    @abstractmethod
    def disconnect(MAC_Address):
        pass

    # Scan Bluetooth Devices and filters for specific devices

    def scan():
        pass

    