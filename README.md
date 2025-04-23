# Ball-Spinner
Pre-Requesites
1. Download Raspbarrian 32 OS on Raspberry Pi4
        The Metawear API is made for 32-bit archetectures, running on 64-bit causes the metawear library to crash

        Make sure to turn on I2c, if not, there are further steps discussing how to 

1. Install libraries for MMS
        a)Install Dev Tools - dependencies required for Metawear API to use BLE
            ```
            sudo apt-get install libboost-all-dev 
            sudo apt-get install libbluetooth-dev
            ```

        b) Metawear API
            To bypass switching the downloader from apt-get to pip, call:
            ```
            sudo pip install metawear --break-system-packages 
            ```
            There will be a warning to NOT use --break-system-packages, but previous developers has never had issues using this method


2. Confirm Download of other essenstial libraries
    The following libraries should be installed with the OS, but confirm that they are installed by calling:

        sudo apt-get install -y gcc-6 g++-6 clang-3.8    
        sudo apt-get install build-essential cmake
        sudo apt install python3-matplotlib


4. Configure settings for ADC
    a) confirm

    b) Install the following libraries to use the ADS_1115 ADC:
        sudo pip install adafruit-ads1x15 --break-system-packages
        sudo pip install adafruit-circuitpython-ads1x15

3. Download Ball-Spinner Controller Application from repository
    git clone https://github.com/mbientlab/MetaWear-SDK-Python.git


        Open MetaWear-SDK

        python3 setup.py build

        d) Download 

         sudo /*LocationToVenV*/bin/pip3 install six

        run code
            '''
            sudo python -m package.tests.ProtocolTests
            '''

Run BSC Code: sudo python main.py
Run Test Code: sudo python -m package.tests.ProtocolTests
Run all tests: sudo python -m unittest discover -s tests


current dependencies
BlueZ - bluetoothd -v = 5.66
Python - python --version = Python 3.11.2
g++ - g++ -version = 12.2.0
g++ - g++ -version = 12.2.0
make - make -version =4.3

