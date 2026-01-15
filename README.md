# SparkFun UHF RFID Reader Library for Python

A Python port of the [SparkFun Simultaneous RFID Tag Reader Library](https://github.com/sparkfun/SparkFun_Simultaneous_RFID_Tag_Reader_Library) for controlling ThingMagic M6E Nano and M7E Hecto UHF RFID modules.

This library enables you to read and write UHF Gen2 RFID tags using Python, with support for multiple simultaneous tag reading.

## Features

- ✅ Read multiple RFID tags simultaneously
- ✅ Read/Write EPC (Electronic Product Code)
- ✅ Read/Write user data memory
- ✅ Read/Write passwords (kill and access)
- ✅ Read TID/UID
- ✅ Kill tags
- ✅ GPIO control
- ✅ Configurable power levels and regions
- ✅ Support for M6E Nano and M7E Hecto modules

## Supported Hardware

- [SparkFun Simultaneous RFID Tag Reader - M6E Nano](https://www.sparkfun.com/products/14066)
- ThingMagic M7E Hecto

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Prerequisites

- Python 3.8 or higher
- uv package manager

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install the library

```bash
# Clone the repository
git clone <repository-url>
cd sparkfun-rfid-reader

# Install dependencies
uv sync
```

### Manual installation with pip

If you prefer using pip:

```bash
pip install pyserial
```

## Quick Start

```python
from sparkfun_rfid import RFID, ModuleType
from sparkfun_rfid.constants import REGION_NORTHAMERICA, RESPONSE_SUCCESS

# Create RFID reader instance
rfid = RFID()

# Connect to the module
rfid.begin('/dev/ttyUSB0', 115200, ModuleType.M6E_NANO)

# Configure
rfid.set_region(REGION_NORTHAMERICA)
rfid.set_read_power(500)  # 5.00 dBm
rfid.set_tag_protocol()
rfid.set_antenna_port()

# Read a tag's EPC
response, epc = rfid.read_tag_epc(timeout=1000)
if response == RESPONSE_SUCCESS:
    print(f"EPC: {epc.hex(' ').upper()}")

# Close connection
rfid.close()
```

## Examples

The `examples/` directory contains several example scripts:

### Example 1: Constant Read
Continuously scans for tags and displays their EPC, RSSI, frequency, and timestamp.

```bash
uv run python examples/example1_constant_read.py
```

### Example 2: Read EPC
Single-shot reading of a tag's EPC on demand.

```bash
uv run python examples/example2_read_epc.py
```

### Example 3: Write EPC
Writes a new EPC to a tag (use with caution!).

```bash
uv run python examples/example3_write_epc.py
```

### Example 4: Read User Data
Reads the user data memory bank from a tag.

```bash
uv run python examples/example4_read_user_data.py
```

## Configuration

### Serial Port

Change the serial port in the examples to match your system:

- **Linux**: `/dev/ttyUSB0`, `/dev/ttyACM0`
- **Windows**: `COM3`, `COM4`, etc.
- **macOS**: `/dev/tty.usbserial-XXXXXXXX`

### Module Type

Specify your module type when initializing:

```python
from sparkfun_rfid import ModuleType

# For M6E Nano
rfid.begin(port, baudrate, ModuleType.M6E_NANO)

# For M7E Hecto
rfid.begin(port, baudrate, ModuleType.M7E_HECTO)
```

### Regions

Set the appropriate region for your location:

```python
from sparkfun_rfid.constants import (
    REGION_NORTHAMERICA,
    REGION_EUROPE,
    REGION_JAPAN,
    REGION_CHINA,
    REGION_KOREA,
    REGION_AUSTRALIA,
    REGION_NEWZEALAND,
    REGION_INDIA,
    REGION_OPEN
)

rfid.set_region(REGION_NORTHAMERICA)
```

## API Reference

### RFID Class

#### Connection
- `begin(port, baudrate, module_type, timeout)` - Initialize serial connection
- `close()` - Close serial connection

#### Configuration
- `set_region(region)` - Set frequency region
- `set_read_power(power)` - Set read power (0-2700 = 0-27dBm)
- `set_write_power(power)` - Set write power
- `set_tag_protocol(protocol)` - Set tag protocol (default GEN2)
- `set_antenna_port()` - Configure antenna ports

#### Reading Tags
- `start_reading()` - Start continuous tag reading
- `stop_reading()` - Stop continuous reading
- `check()` - Check for incoming data
- `parse_response()` - Parse response message
- `read_tag_epc(timeout)` - Read tag EPC
- `read_user_data(timeout)` - Read user data
- `read_tid(timeout)` - Read TID
- `read_uid(timeout)` - Read UID

#### Writing Tags
- `write_tag_epc(epc, timeout)` - Write new EPC
- `write_user_data(data, timeout)` - Write user data
- `write_kill_password(password, timeout)` - Write kill password
- `write_access_password(password, timeout)` - Write access password

#### Tag Information
- `get_tag_epc_bytes()` - Get EPC byte count from response
- `get_tag_rssi()` - Get RSSI from response
- `get_tag_freq()` - Get frequency from response
- `get_tag_timestamp()` - Get timestamp from response

#### Advanced
- `kill_tag(password, timeout)` - Permanently disable a tag
- `pin_mode(pin, mode)` - Configure GPIO pin
- `digital_write(pin, state)` - Set GPIO output
- `digital_read(pin)` - Read GPIO input
- `enable_debugging()` - Enable debug output
- `disable_debugging()` - Disable debug output

## Response Codes

```python
from sparkfun_rfid.constants import (
    ALL_GOOD,
    RESPONSE_SUCCESS,
    RESPONSE_FAIL,
    RESPONSE_IS_TAGFOUND,
    RESPONSE_IS_KEEPALIVE,
    ERROR_COMMAND_RESPONSE_TIMEOUT,
    ERROR_CORRUPT_RESPONSE,
    ERROR_WRONG_OPCODE_RESPONSE
)
```

## Troubleshooting

### Permission Denied on Linux

Add your user to the dialout group:

```bash
sudo usermod -a -G dialout $USER
```

Then log out and log back in.

### Module Not Responding

1. Check the serial port connection
2. Verify the correct port name
3. Try resetting the module
4. Check baudrate (usually 115200)
5. Ensure sufficient power supply

### No Tags Found

1. Increase read power: `rfid.set_read_power(2700)` (max)
2. Check antenna connection
3. Verify tag is Gen2 compliant
4. Ensure tag is within range (typically a few cm to 1m)
5. Check region settings match your location

## Context Manager Support

The RFID class supports Python context managers for automatic cleanup:

```python
with RFID() as rfid:
    rfid.begin('/dev/ttyUSB0', 115200)
    rfid.set_region(REGION_NORTHAMERICA)
    # ... your code here ...
# Connection automatically closed
```

## License

This library is a Python port of the original SparkFun Arduino library and maintains the same open source MIT License.

Original Arduino library by Nathan Seidle @ SparkFun Electronics

If you find this code helpful, consider buying a board from [SparkFun](https://www.sparkfun.com)!

## Credits

- Original Arduino Library: [SparkFun Electronics](https://github.com/sparkfun)
- ThingMagic Mercury API Documentation
- Python Port: Based on the Arduino library version 1.2.0

## Links

- [Original Arduino Library](https://github.com/sparkfun/SparkFun_Simultaneous_RFID_Tag_Reader_Library)
- [SparkFun Product Page](https://www.sparkfun.com/products/14066)
- [Hookup Guide](https://learn.sparkfun.com/tutorials/simultaneous-rfid-tag-reader-hookup-guide)
- [ThingMagic Documentation](https://www.jadak.com/thingmagic-rfid/)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
