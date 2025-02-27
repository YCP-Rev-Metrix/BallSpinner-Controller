from abc import ABCMeta, abstractmethod

class iMotor(metaclass=ABCMeta): 
     
    @abstractmethod
    def __init__(self, GPIOPin : int):
        pass

    # Turns on Motor at Specified Power (Duty Cycle)
    @abstractmethod
    def turnOnMotor(self, dutyCycle = 100):
        pass

    @abstractmethod
    def turnOffMotor(self):
        pass

    @abstractmethod
    def changeSpeed(self, dutyCycle : int):
        pass

    @abstractmethod
    def rampUp(self):
        pass