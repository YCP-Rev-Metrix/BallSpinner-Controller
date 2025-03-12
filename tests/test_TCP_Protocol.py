from BallSpinnerController import *
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from datetime import datetime
import random
import sys
import socket
import unittest
from time import sleep
import multiprocessing 
import struct

class ProtocolTests(unittest.TestCase): #Test the Protocol Messages Through TCP Socket using SmartDotEmulator
    
    ready_event = multiprocessing.Event()  # Event to signal when the server is ready

    @classmethod
    def setUpClass(cls):
        # Start the BallSpinnerController in a separate process
        cls.bsc_process = multiprocessing.Process(target=BallSpinnerController, args="1") 
        cls.bsc_process.start()

        # Give time for BallSpinnerController to Connect to Socket
        sleep(.5)

        #determine global ip address
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                cls.ipAddr = s.getsockname()[0]

        except Exception:
            # ERROR: Not Connected to Internet
            pass 

        finally:
            s.close()

    def _test_socket_Established(self):
        try:
                # Create a client socket and connect to the server
                    
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            server_ip = self.ipAddr  # Replace with the actual IP address
            server_port = 8411  # Replace with the actual port
        
            print("Test: Connecting to BSC")
            client_socket.connect((server_ip, server_port))

            print("Test: Connected to BSC")

            self.commsPort = client_socket
            
        except socket.error as e:
            self.fail(e)

    def _test_APP_INIT_ACK(self):
        # Send APP_INIT
        print("Test: Sending APP_INIT")
        self.commsPort.sendall(bytearray([0x01, 0x00, 0x01, 0x00]))
            
        #Receive APP_INIT_ACK
        response = self.commsPort.recv(4)

        #Confirm APP_INIT_ACK in Protocol
        self.assertEqual(response, b'\x02\x00\x01\x00')
        print("Test: Received APP_INIT_ACK")

    def _test_BSC_NAME(self):
        pass

    def _test_SMARTDOT_SCAN(self):
        #Send SMARTDOT_SCAN
        print("Test: Sending SMARTDOT_SCAN_INIT")
        self.commsPort.sendall(bytearray([0x05, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

        #Receive ABBREVIATED_SMARTDOT_CONNECTED (ASSUMING THE FIRST RETRIEVED IS THE SMARTDOT_EMULATOR)
        #Confirm SMARTDOT_SCAN in Protocol

        #1) Parse Header
        data = self.commsPort.recv(3)
        self.assertEqual(data[0], 0x06) #Confirm Header
        #Determine Size of Message
        messSize = struct.unpack(">I", b'\x00\x00' + data[1:3])[0]
        data = self.commsPort.recv(messSize)
        expectedMAC = bytearray([0x11, 0x11, 0x11, 0x11, 0x11, 0x11])
        self.assertEqual(data[0:6], expectedMAC)
        expectedName = "smartDotSimulator".encode("utf-8")
        self.assertEqual(data[6:23], expectedName)
        print("Test: Received SMARTDOT_SCAN")      

    def _test_ABBREVIATED_SMARTDOT_CONNECTED(self):
        print("Test: Sending SMART_SCAN_CONNECT")
        self.commsPort.sendall(bytearray([0x05, 0x00, 0x06, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11]))
        response = self.commsPort.recv(9)
        self.assertEqual(response[0], 0x06)
        self.assertEqual(response[1:3], b'\x00\x06')
        self.assertEqual(response[3:10], b'\x11\x11\x11\x11\x11\x11')
        print("Test: Received ABBREVIATED_SMARTDOT_CONNECTED")


    
    def _test_SD_SENSOR_DATA(self):
        print("Test: Sending ABBREVIATED_MOTOR_INSRUCTIONS")
        self.commsPort.sendall(bytearray([0x08, 0x00, 0x03, 0x0A, 0x0A, 0x0A]))

        #Listen For 10 of Each, then Stop
        print("Test: Receiving 10, Then Stopping")
        AccelCount = 0
        GyroCount = 0
        MagCount = 0
        LightCount = 0

        print("Test: Receiving at least 10 of Each 9DOF, Then Stopping")
        while (not (AccelCount >= 10) 
               or not (GyroCount >= 10) 
               or not (MagCount >= 10)
               or not (LightCount  >= 10)) :
            data = self.commsPort.recv(23)
            if not data == b'':
                print("DATA SIZE %s" %data[0]) #delete
                self.assertEqual(bytes([data[0]]), b'\x0A') #Needed to convert first back to bytes because it gets converted to int (idk why)
                self.assertEqual(data[1:3], b'\x00\x13')
                match chr(data[3]): #Acts as check for SensorType
                
                    case 'A':
                        AccelCount+= 1
                        print("Test: Accel Receive %i" % AccelCount)
                        pass

                    case 'M':
                        MagCount += 1
                        print("Test: Mag Receive %i" % MagCount)
                        pass

                    case 'G':
                        GyroCount += 1   
                        print("Test: Gyro Receive %i" % GyroCount)
                        pass
                    
                    case 'L':
                        LightCount += 1
                        print("Test: Light Receive %i" % LightCount)
                        pass 

                    case _:
                        self.fail(f"Unexpected Sensor Type") #Incorrect Sensor Type
                        

        print("Test: Received at least 10 of each 9DOF module")

    def _testAbruptCrashing(self):
        print("Test: Crashing socket and see if it re-opens")
        self.commsPort.close()
        sleep(.5)

        


    def testBSC(self):
        for x in range(2):
            self._test_socket_Established()
            self._test_APP_INIT_ACK()
            self._test_BSC_NAME()
            self._test_SMARTDOT_SCAN()
            self._test_ABBREVIATED_SMARTDOT_CONNECTED()
            self._test_SD_SENSOR_DATA()
            self._testAbruptCrashing()
        
    @classmethod
    def tearDown(cls):
        cls.bsc_process.kill()

    def tearDown(self):
        print("CommsStopped")
        self.commsPort.close()