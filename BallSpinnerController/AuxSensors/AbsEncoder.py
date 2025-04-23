import iAuxSensor
import serial
import time

# Configure UART serial connection
SERIAL_PORT = "/dev/serial0"  # Adjust if using a different UART port
BAUD_RATE = 115200  # Ensure this matches the encoder's settings

class AbsEncoder(iAuxSensor):

    def readData(self):
        """Reads RPM from AMT212C-V encoder over RS485-UART."""
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                # Command to request velocity (Modify based on AMT212C-V protocol)
                request_cmd = bytes([0x52, 0x56])  # Example: 'RV' command (adjust as per datasheet)
                ser.write(request_cmd)
                time.sleep(0.1)

                # Read response (Modify based on actual response format)
                response = ser.read(2)  # Assuming 2 bytes for velocity data
                if response:
                    """Convert the received velocity bytes to RPM."""
                    if len(response) < 2:
                        return None
                    velocity = int.from_bytes(response, byteorder="big", signed=True)
                    rpm = velocity
                    print(f"RPM: {rpm}")
                else:
                    print("No response received.")

        except serial.SerialException as e:
            print(f"Serial error: {e}")
