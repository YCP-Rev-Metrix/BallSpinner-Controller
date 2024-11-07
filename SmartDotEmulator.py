from iSmartDot import iSmartDot
from mbientlab.metawear import MetaWear
from mbientlab.warble import WarbleException

class SmartDotEmulator(iSmartDot):

    def UUID(self) -> str:
        return "326a9000-85cb-9195-d9dd-464cfbbae75b"
    
    def connect(self, MAC_Address) -> bool:
        print("Attempting to connect to device")
        try:
            self.device = MetaWear(MAC_Address)
            self.device.connect()

        #Timeout occured and Connection was unsuccessful     
        except WarbleException:
            print("Unable to connect to device")
            return False
        
        return True
        

        
    
    def disconnect(MAC_Address):
        return super().disconnect()
