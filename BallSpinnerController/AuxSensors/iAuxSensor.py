from abc import ABCMeta, abstractmethod

class iAuxSensor(metaclass=ABCMeta): 
     
    @abstractmethod
    def __init__(self, GPIOPin : int):
        pass

    @abstractmethod
    def readData(self): 
        pass