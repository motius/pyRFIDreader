# SparkFun UHF RFID Reader Library for Python

A Python port of the [SparkFun Simultaneous RFID Tag Reader Library](https://github.com/sparkfun/SparkFun_Simultaneous_RFID_Tag_Reader_Library) for controlling ThingMagic M6E Nano and M7E Hecto UHF RFID modules.

Claude Code did most of the work here.

This library enables you to read and write UHF Gen2 RFID tags using Python, with support for multiple simultaneous tag reading.

## Supported Hardware

- [SparkFun Simultaneous RFID Reader - M7E Hecto](https://www.sparkfun.com/sparkfun-simultaneous-rfid-reader-m7e-hecto.html>)

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

## Troubleshooting

### Permission Denied on Linux

Add your user to the dialout group:

```bash
sudo usermod -a -G dialout $USER
```

Then log out and log back in.

## License

This library is a Python port of the original SparkFun Arduino library and maintains the same open source MIT License.

Original Arduino library by Nathan Seidle @ SparkFun Electronics

If you find this code helpful, consider buying a board from [SparkFun](https://www.sparkfun.com)!
