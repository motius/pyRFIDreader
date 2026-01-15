#!/usr/bin/env python3
"""
Setup Helper Script

A utility to help configure and test your RFID reader connection.
This script will:
1. Test the serial connection
2. Get module version
3. Configure basic settings
4. Test tag reading

Useful for initial setup and troubleshooting.
"""

import sys
import traceback
from sparkfun_rfid import RFID, ModuleType
from sparkfun_rfid.constants import (
    ALL_GOOD,
    RESPONSE_SUCCESS,
    REGION_NORTHAMERICA,
    REGION_EUROPE,
    REGION_JAPAN,
    REGION_CHINA,
    REGION_KOREA,
    REGION_AUSTRALIA,
    REGION_NEWZEALAND,
    REGION_INDIA,
    REGION_OPEN,
)


def test_connection(rfid: RFID) -> bool:
    """Test basic connection to the module"""
    print("\nTesting connection...")
    rfid.get_version()

    if len(rfid.msg) == 0:
        print("✗ No response from module")
        return False

    if rfid.msg[0] == ALL_GOOD:
        print("✓ Connection successful!")

        # Parse version info
        if len(rfid.msg) > 10:
            # Extract version string
            version_data = bytes(rfid.msg[7:rfid.msg[1]+7])
            try:
                version_str = version_data.decode('ascii', errors='ignore')
                print(f"  Firmware: {version_str}")
            except:
                print(f"  Version data: {version_data.hex()}")

        return True
    else:
        print("✗ Connection failed!")
        print(f"  Error code: {rfid.msg[0]}")
        return False


def setup_basic_config(rfid: RFID, region: int, power: int) -> bool:
    """Configure basic settings"""
    print("\nConfiguring module...")

    try:
        rfid.set_tag_protocol()
        print("✓ Protocol set to GEN2")

        rfid.set_antenna_port()
        print("✓ Antenna ports configured")

        rfid.set_region(region)
        region_names = {
            REGION_NORTHAMERICA: "North America",
            REGION_EUROPE: "Europe",
            REGION_JAPAN: "Japan",
            REGION_CHINA: "China",
            REGION_KOREA: "Korea",
            REGION_AUSTRALIA: "Australia",
            REGION_NEWZEALAND: "New Zealand",
            REGION_INDIA: "India",
            REGION_OPEN: "Open/Custom",
        }
        print(f"✓ Region set to {region_names.get(region, 'Unknown')}")

        rfid.set_read_power(power)
        print(f"✓ Read power set to {power/100:.2f} dBm")

        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False


def test_tag_read(rfid: RFID) -> bool:
    """Test reading a tag"""
    print("\nTesting tag read...")
    print("Place a tag near the reader...")

    response, epc = rfid.read_tag_epc(timeout=2000)
    rssi = rfid.get_tag_rssi()

    if response == RESPONSE_SUCCESS:
        print("✓ Tag read successful!")
        print(f"  EPC: {epc.hex(' ').upper()}")
        print(f"  Length: {len(epc)} bytes")
        print(f"  RSSI: {rssi} dBm")
        return True
    else:
        print("✗ No tag found (this is okay if no tag is present)")
        print("  Try placing a tag near the antenna")
        return False


def main():
    print("=" * 60)
    print("SparkFun RFID Reader - Setup Helper")
    print("=" * 60)

    port = "/dev/ttyUSB0"
    baudrate = 115200
    module_type = ModuleType.M7E_HECTO


    # Get region
    print("\nRegion:")
    print("  [1] North America")
    print("  [2] Europe")
    print("  [3] Japan")
    print("  [4] China")
    print("  [5] Korea")
    print("  [6] Australia")
    print("  [7] New Zealand")
    print("  [8] India")
    region = REGION_EUROPE
    power = 500

    # Create RFID instance
    rfid = RFID()
    rfid.enable_debugging()  # Enable debug output

    try:
        print("\n" + "=" * 60)
        print("TESTING CONNECTION")
        print("=" * 60)

        # Connect
        print(f"\nConnecting to {port} at {baudrate} baud...")
        rfid.begin(port, baudrate, module_type)
        print("✓ Serial port opened")

        # Test connection
        if not test_connection(rfid):
            print("\nFailed to communicate with module.")
            print("Please check:")
            print("  - Serial port is correct")
            print("  - Module is powered on")
            print("  - Baud rate is correct")
            sys.exit(1)

        # Configure
        if not setup_basic_config(rfid, region, power):
            print("\nConfiguration failed, but connection is working.")

        # Test read
        test_tag_read(rfid)

        print("\n" + "=" * 60)
        print("SETUP COMPLETE")
        print("=" * 60)
        print("\nYour configuration:")
        print(f"  Port: {port}")
        print(f"  Baudrate: {baudrate}")
        print(f"  Module: {module_type.name}")
        print(f"  Power: {power/100:.2f} dBm")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        traceback.print_exc()
        sys.exit(1)

    finally:
        rfid.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
