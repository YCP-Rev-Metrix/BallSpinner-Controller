# Ball-Spinner
Pre-Requesites
32-bit Architecture
1. Install Metawear API
        a)Create and Open Virtual Environment
        Download Development Tools - needed to run application
            ```
            sudo python -m venv /*locationToVenV*/
            source /*LocationToVenV*/bin/activate
            (However, sudo pip install pymetawear --break-system-packages is the only command that allowed metawear to work properly)
            ```

        b)Install Dev Tools 
            ```
            sudo apt-get install libboost-all-dev 
            sudo apt-get install libbluetooth-dev
            ```

        b) In order to download the metawear API, the vir
            ```
            sudo /*LocationToVenV*/bin/pip3 install pymetawear
            sudo /*LocationToVenV*/bin/pip3 install pymetawear --upgrade
            ```
                pipx install warble

        c) Download repository
                git clone https://github.com/mbientlab/MetaWear-SDK-Python.git


        Open MetaWear-SDK

        python3 setup.py build

        d) Download Ball-Spinner Application

         sudo /*LocationToVenV*/bin/pip3 install six




sudo apt-get install -y gcc-6 g++-6 clang-3.8

current dependencies
BlueZ - bluetoothd -v = 5.66
Python - python --version = Python 3.11.2
g++ - g++ -version = 12.2.0
g++ - g++ -version = 12.2.0
make - make -version =4.3

