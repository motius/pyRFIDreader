#!/usr/bin/env python3
"""
Example 4: Read User Data

Reads the user data memory bank from a tag (typically 0-64 bytes available).

This is a Python port of the Arduino example.
"""

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

    print("SparkFun RFID Reader - Read User Data Example")
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
            input("Press Enter to read user data from a tag (Ctrl+C to quit)...")

            # First read the EPC to identify the tag
            print("Reading tag EPC...")
            response_type, epc = rfid.read_tag_epc(timeout=1000)

            if response_type != RESPONSE_SUCCESS:
                print("✗ No tag found\n")
                continue

            print(f"Tag EPC: {epc.hex(' ').upper()}")

            # Now read the user data
            print("Reading user data...")
            response_type, user_data = rfid.read_user_data(timeout=1000)

            if response_type == RESPONSE_SUCCESS:
                print(f"✓ User data read successfully!")
                print(f"  Length: {len(user_data)} bytes")
                print(f"  Hex: {user_data.hex(' ').upper()}")

                # Try to decode as ASCII
                try:
                    ascii_text = user_data.decode('ascii').rstrip('\x00')
                    if ascii_text:
                        print(f"  ASCII: {ascii_text}")
                except:
                    pass

                print()
            else:
                print("✗ Failed to read user data\n")

    except KeyboardInterrupt:
        print("\n\nExiting...")

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        rfid.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
