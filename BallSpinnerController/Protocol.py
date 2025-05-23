from enum import Enum


class MsgType:

    #Section 1 Protocol
    A_B_INIT_HANDSHAKE = 0x01
    
    B_A_INIT_HANDSHAKE_ACK = 0x02

    A_B_NAME_REQ = 0x03

    B_A_NAME = 0x04

    A_B_START_SCAN_FOR_SD = 0x05

    B_A_SCANNED_SD = 0x06

    A_B_CHOSEN_SD = 0x07

    B_A_RECEIVE_CONFIG_INFO = 0x08

    A_B_RECEIVE_CONFIG_INFO = 0x09

    A_B_SD_TOGGLE_TAKE_DATA = 0x0A
    
    B_A_SD_SENSOR_DATA = 0x0B

    A_B_MOTOR_INSTRUCTIONS = 0x0C

    A_B_STOP_MOTOR = 0x0D

    A_B_DISCONNECT_FROM_BSC = 0x0E

    _reverse_mapping = {value: name for name, value in locals().items() if not name.startswith('_') and not callable(value)}

    @classmethod
    def name_from_value(cls, value):
        return cls._reverse_mapping.get(value)
    
class SensorType:
    SD_XL = 0x41

    SD_GY = 0x47

    SD_MG = 0x4D

    SD_MG = 0x4D

    SD_LT = 0x4C
    
    SD_Test = 0x54


    C1_SNSR = 0x43

    C2_SNSR = 0x56

    C3_SNSR = 0x52

    #Motor Encoders    
    M1_ENC = 0x6D

    M2_ENC = 0x6F

    M3_ENC = 0x74


    _reverse_mapping = {value: name for name, value in locals().items() if not name.startswith('_') and not callable(value)}


class ErrType:
    pass

class bitMappings():
    
    def sendConfigSettings(XL_availSampleRate, XL_availRange,
                           GY_availSampleRate, GY_availRange,
                           MG_availSampleRate, MG_availRange,
                           LT_availSampleRate, LT_availRange,):
        
        # Pre-allocate array
        configSettingsBytes = bytearray([0, 0, 0, 0, 0, 0, 0, 0])

        for x in XL_availSampleRate:
            if x == 12.5:  configSettingsBytes[0] |= 1     #Set BIT0
            if x ==   25:  configSettingsBytes[0] |= 2     #Set BIT1
            if x ==   50:  configSettingsBytes[0] |= 4     #Set BIT2
            if x ==  100:  configSettingsBytes[0] |= 8     #Set BIT3
            if x ==  200:  configSettingsBytes[0] |= 16    #Set BIT4
            if x ==  400:  configSettingsBytes[0] |= 32    #Set BIT5
            if x ==  800:  configSettingsBytes[0] |= 64    #Set BIT6
            if x ==  1600: configSettingsBytes[0] |= 128   #Set BIT7

        for x in XL_availRange:
            if x ==    2:  configSettingsBytes[1] |= 1
            if x ==    4:  configSettingsBytes[1] |= 2
            if x ==    8:  configSettingsBytes[1] |= 4
            if x ==   16:  configSettingsBytes[1] |= 8

        for x in GY_availSampleRate:
            if x ==   25:  configSettingsBytes[2] |= 1
            if x ==   50:  configSettingsBytes[2] |= 2
            if x ==  100:  configSettingsBytes[2] |= 4
            if x ==  200:  configSettingsBytes[2] |= 8
            if x ==  400:  configSettingsBytes[2] |= 16
            if x ==  800:  configSettingsBytes[2] |= 32
            if x ==  1600: configSettingsBytes[2] |= 64
            if x ==  3200: configSettingsBytes[2] |= 128
            if x ==  6400: configSettingsBytes[3] |= 128

        for x in GY_availRange:
            if x ==    125:  configSettingsBytes[3] |= 1
            if x ==    250:  configSettingsBytes[3] |= 2
            if x ==    500:  configSettingsBytes[3] |= 4
            if x ==   1000:  configSettingsBytes[3] |= 8
            if x ==   2000:  configSettingsBytes[3] |= 16


        for x in MG_availSampleRate:
            if x ==    2:  configSettingsBytes[4] |= 1
            if x ==    6:  configSettingsBytes[4] |= 2
            if x ==    8:  configSettingsBytes[4] |= 4
            if x ==   10:  configSettingsBytes[4] |= 8
            if x ==   15:  configSettingsBytes[4] |= 16
            if x ==   20:  configSettingsBytes[4] |= 32
            if x ==   25:  configSettingsBytes[4] |= 64
            if x ==   30:  configSettingsBytes[4] |= 128

        for x in MG_availRange:
            if x ==    2500:  configSettingsBytes[5] |= 1

        for x in LT_availSampleRate:
            if x ==      .5:  configSettingsBytes[6] |= 1
            if x ==       1:  configSettingsBytes[6] |= 2
            if x ==       2:  configSettingsBytes[6] |= 4
            if x ==       5:  configSettingsBytes[6] |= 8
            if x ==      10:  configSettingsBytes[6] |= 16
            if x ==      20:  configSettingsBytes[6] |= 32

            
        for x in LT_availRange:
            if x ==    600:   configSettingsBytes[7] |= 1
            if x ==    1300:  configSettingsBytes[7] |= 2
            if x ==    8000:  configSettingsBytes[7] |= 4
            if x ==   16000:  configSettingsBytes[7] |= 8
            if x ==   32000:  configSettingsBytes[7] |= 16
            if x ==   64000:  configSettingsBytes[7] |= 32
   
        '''
        for x in self.smartDot.XL_availSampleRate:
        if x ==    2: XL_rangeByte |= 1
        if x ==    4: XL_rangeByte |= 2
        if x ==    8: XL_rangeByte |= 4
        if x ==   16: XL_rateByte  |= 8
        '''     
        return configSettingsBytes