#!/usr/bin/env python3
"""
Example 2: Read EPC

Single shot read - asks the reader to read a tag's EPC when prompted.

This is a Python port of the Arduino example.
"""

import time
from sparkfun_rfid import RFID, ModuleType
from sparkfun_rfid.constants import (
    RESPONSE_SUCCESS,
    REGION_NORTHAMERICA
)


def main():
    # Configure your serial port here
    SERIAL_PORT = '/dev/ttyUSB0'  # Change to 'COM3' on Windows, etc.
    BAUDRATE = 115200
    MODULE_TYPE = ModuleType.M6E_NANO  # or ModuleType.M7E_HECTO

    print("SparkFun RFID Reader - Read EPC Example")
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
        print("Module initialized successfully!\n")

        while True:
            input("Press Enter to scan for a tag (Ctrl+C to quit)...")

            print("Searching for tag...")
            response_type = RESPONSE_SUCCESS
            attempts = 0
            max_attempts = 5

            while response_type != RESPONSE_SUCCESS and attempts < max_attempts:
                response_type, epc = rfid.read_tag_epc(timeout=500)
                attempts += 1

                if response_type != RESPONSE_SUCCESS:
                    print(f"  Attempt {attempts}/{max_attempts}...")
                    time.sleep(0.1)

            if response_type == RESPONSE_SUCCESS:
                print(f"\n✓ Tag Found!")
                print(f"  EPC: {epc.hex(' ').upper()}")
                print(f"  Length: {len(epc)} bytes\n")
            else:
                print("\n✗ No tag found after maximum attempts\n")

    except KeyboardInterrupt:
        print("\n\nExiting...")

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        rfid.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
