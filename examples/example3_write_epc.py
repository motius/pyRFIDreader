#!/usr/bin/env python3
"""
Example 3: Write EPC

Writes a new EPC to a tag.

WARNING: Use with caution! This will write to the first tag detected.
Make sure only one tag is in range.

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

    print("SparkFun RFID Reader - Write EPC Example")
    print("=" * 50)
    print("WARNING: This will write to the first tag detected!")
    print("Make sure only ONE tag is in range.\n")

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
        rfid.set_write_power(500) # 5.00 dBm
        rfid.set_tag_protocol()   # GEN2
        rfid.set_antenna_port()

        # Get version info
        rfid.get_version()
        print("Module initialized successfully!\n")

        # First, read the current EPC
        print("Reading current EPC...")
        response_type, current_epc = rfid.read_tag_epc(timeout=1000)

        if response_type == RESPONSE_SUCCESS:
            print(f"Current EPC: {current_epc.hex(' ').upper()}")
        else:
            print("Could not read current EPC. Make sure a tag is present.")
            return

        # Get new EPC from user
        print("\nEnter new EPC (hex digits, no spaces):")
        print("Example: 0123456789ABCDEF01234567")
        new_epc_str = input("New EPC: ").strip().replace(' ', '')

        try:
            new_epc = bytes.fromhex(new_epc_str)
        except ValueError:
            print("Invalid hex string!")
            return

        # Confirm
        print(f"\nYou are about to write:")
        print(f"  New EPC: {new_epc.hex(' ').upper()}")
        confirm = input("Type 'YES' to confirm: ")

        if confirm != 'YES':
            print("Cancelled.")
            return

        # Write the new EPC
        print("\nWriting new EPC...")
        response_type = rfid.write_tag_epc(new_epc, timeout=1000)

        if response_type == RESPONSE_SUCCESS:
            print("✓ EPC written successfully!")

            # Verify by reading it back
            print("\nVerifying...")
            response_type, read_epc = rfid.read_tag_epc(timeout=1000)

            if response_type == RESPONSE_SUCCESS:
                print(f"Read back EPC: {read_epc.hex(' ').upper()}")

                if read_epc == new_epc:
                    print("✓ Verification successful!")
                else:
                    print("✗ Verification failed - EPCs don't match!")
            else:
                print("Could not verify - read failed")
        else:
            print("✗ Write failed!")

    except KeyboardInterrupt:
        print("\n\nExiting...")

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        rfid.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()
