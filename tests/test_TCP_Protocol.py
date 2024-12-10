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
        cls.bsc_process = multiprocessing.Process(target=cls.run_ball_spinner_controller)
        cls.bsc_process.start()

        # Wait for the server to signal readiness
        cls.ready_event.wait()  # Blocks until the event is set
        sleep(2)

    @classmethod
    def run_ball_spinner_controller(cls):
        # Run the BallSpinnerController in a blocking manner
        cls.ready_event.set()

        
        # Notify that the server is ready
        BallSpinnerController()

        


    def test(self):
        print("Ploop")
        # Create a socket object#determine global ip address
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ipAddr = s.getsockname()[0]

        except Exception:
            # ERROR: Not Connected to Internet
            pass 

        finally:
            s.close()

        try:
                # Create a client socket and connect to the server
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                    server_ip = ipAddr  # Replace with the actual IP address
                    server_port = 8411  # Replace with the actual port
                    
                    client_socket.connect((server_ip, server_port))
                    print("Connected to server")
                    
                    # Send and receive data
                    client_socket.sendall(bytearray([0x81, 0x00, 0x01, 0x00]))
                    response = client_socket.recv(1024)
                    print("Received:", response)
                    self.commsPort = client_socket
                    
        except socket.error as e:
            print("Socket error:", e)

        #Send BSC_NAME_REQ
        self.commsPort.sendall(bytearray([0x85, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

        #Receive 
        data = self.commsPort.recv(1024)
        print(data)

        bytesData = bytearray([0x85, 0x00, 0x06])
        bytesData.extend(data[3:9])
        #Send Motor Instr
        self.commsPort.sendall(bytesData)


        print(data)
        self.commsPort.sendall(bytearray[0x88, 0x00, 0x03, 0x0A, 0x0A, 0x0A])

        print(self.commsPort.recv(1024))

        while True:
            data = self.commsPort.recv(1024)
            if not data == b'':
                print(data)
                pass

    def tearDown(self):
        asyncio.sleep(5000)
        self.commsPort.close()