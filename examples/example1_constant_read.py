#!/usr/bin/env python3
"""
Example 1: Constant Read

Constantly reads and outputs any RFID tags detected.

This is a Python port of the Arduino example.
"""

import time
from sparkfun_rfid import RFID, ModuleType
from sparkfun_rfid.constants import (
    RESPONSE_IS_KEEPALIVE,
    RESPONSE_IS_TAGFOUND,
    RESPONSE_IS_HIGHRETURNLOSS,
    ERROR_CORRUPT_RESPONSE,
    REGION_NORTHAMERICA
)


def main():
    # Configure your serial port here
    SERIAL_PORT = '/dev/ttyUSB0'  # Change to 'COM3' on Windows, etc.
    BAUDRATE = 115200
    MODULE_TYPE = ModuleType.M6E_NANO  # or ModuleType.M7E_HECTO

    print("SparkFun RFID Reader - Constant Read Example")
    print("=" * 50)

    # Create RFID reader instance
    rfid = RFID()

    try:
        # Initialize the reader
        print(f"Connecting to module on {SERIAL_PORT}...")
        rfid.begin(SERIAL_PORT, BAUDRATE, MODULE_TYPE)

        # Configure the reader
        print("Configuring module...")
        rfid.set_region(REGION_NORTHAMERICA)
        rfid.set_read_power(500)  # 5.00 dBm
        rfid.set_tag_protocol()   # GEN2
        rfid.set_antenna_port()

        # Get version info
        rfid.get_version()
        print("Module initialized successfully!")

        print("\nPress Ctrl+C to stop scanning")
        print("Starting continuous read...\n")

        # Start continuous reading
        rfid.start_reading()

        # Main loop
        while True:
            # Check for new data
            if rfid.check():
                response_type = rfid.parse_response()

                if response_type == RESPONSE_IS_KEEPALIVE:
                    print("Scanning...")

                elif response_type == RESPONSE_IS_TAGFOUND:
                    # Extract tag information
                    rssi = rfid.get_tag_rssi()
                    freq = rfid.get_tag_freq()
                    timestamp = rfid.get_tag_timestamp()
                    epc_bytes = rfid.get_tag_epc_bytes()

                    # Extract EPC data
                    epc = bytes(rfid.msg[31:31+epc_bytes])

                    print(f"Tag Found!")
                    print(f"  RSSI: {rssi} dBm")
                    print(f"  Freq: {freq} Hz")
                    print(f"  Time: {timestamp} ms")
                    print(f"  EPC:  {epc.hex(' ').upper()}")
                    print()

                elif response_type == ERROR_CORRUPT_RESPONSE:
                    print("Error: Bad CRC")

                elif response_type == RESPONSE_IS_HIGHRETURNLOSS:
                    print("Warning: High return loss, check antenna!")

                else:
                    print(f"Unknown response: {response_type}")

            time.sleep(0.01)  # Small delay to prevent CPU spinning

    except KeyboardInterrupt:
        print("\n\nStopping...")
        rfid.stop_reading()
        time.sleep(2)  # Give module time to stop

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        rfid.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
