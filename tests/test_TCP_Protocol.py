from BallSpinnerController import *
import unittest
import asyncio
import struct
import threading
from concurrent.futures import ThreadPoolExecutor
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from datetime import datetime
import sys
import socket
from time import sleep
import multiprocessing 

class ProtocolTests(unittest.TestCase):
    
    ready_event = multiprocessing.Event()  # Event to signal when the server is ready

    @classmethod
    def setUpClass(cls):
        # Start the BallSpinnerController in a separate process
        cls.bsc_process = multiprocessing.Process(target=BallSpinnerController) 
        cls.bsc_process.start()

        # Give time for BallSpinner 
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
        
            print("Connecting")
            client_socket.connect((server_ip, server_port))

            print("Connected to server")
            sleep(1)
            # Send and receive data
            client_socket.sendall(bytearray([0x81, 0x00, 0x01, 0x00]))
            response = client_socket.recv(1024)
            print("Received:", response)
            self.commsPort = client_socket
            
        except socket.error as e:
            self.fail(e)

    def testBSC(self):
        self._test_socket_Established()
        #self._test_APP_INIT_ACK()
        

        #Send BSC_NAME_REQ
        self.commsPort.sendall(bytearray([0x85, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

        #Receive 
        data = self.commsPort.recv(1024)
        print(data)

        bytesData = bytearray([0x85, 0x00, 0x06])
        bytesData.extend(data[3:9])

        #Send SmartDot Data
        self.commsPort.sendall(bytesData)

        #Receive Confirmation
        print(self.commsPort.recv(1024))

        
        self.commsPort.sendall(bytearray([0x88, 0x00, 0x03, 0x0A, 0x0A, 0x0A]))

        print(self.commsPort.recv(1024))

        #receive 10 data then stop
        count = 0
        while count <= 10:
            data = self.commsPort.recv(1024)
            if not data == b'':
                print("TEST RECEIVED:")
                print(data)
                count += 1
                pass
        
        self.commsPort.close()

        self.commsPort.sendall(bytearray([0x8B]))
        self.commsPort.recv(1024)

        

    def tearDown(self):
        pass