# Ball-Spinner
Pre-Requesites
32-bit Architecture
1. Install Metawear API
        a)Create and Open Virtual Environment
                    ```
            sudo python -m venv /*locationToVenV*/
            source /*LocationToVenV*/bin/activate
            (However, sudo pip install metawear --break-system-packages is the only command that allowed metawear to work properly)
            ```

        b)Install Dev Tools - needed to run application
            ```
            sudo apt-get install libboost-all-dev 
            sudo apt-get install libbluetooth-dev
            ```

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

Run Test Code: sudo python -m package.tests.ProtocolTests

current dependencies
BlueZ - bluetoothd -v = 5.66
Python - python --version = Python 3.11.2
g++ - g++ -version = 12.2.0
g++ - g++ -version = 12.2.0
make - make -version =4.3

