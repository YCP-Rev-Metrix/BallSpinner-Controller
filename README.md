# Ball-Spinner
Pre-Requesites
Raspbarrian 32 OS 

1. Install Metawear API
        a)Install Dev Tools - needed to run application
            ```
            sudo apt-get install libboost-all-dev 
            sudo apt-get install libbluetooth-dev
            ```

        b) Metawear API
            The Metawear API only works with 32-bit architectures (hence, the 32-bit OS)
            ```
            sudo pip install metawear --break-system-packages 
            ```
            is the only command that allowed metawear to work properly


2. Confirm Download of other essenstial libraries

    sudo apt-get install -y gcc-6 g++-6 clang-3.8    
    sudo apt-get install build-essential cmake

           

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

