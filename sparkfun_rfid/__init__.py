"""
SparkFun UHF RFID Reader Library for Python

This is a Python port of the SparkFun Simultaneous RFID Tag Reader Library
for controlling the ThingMagic M6E Nano and M7E Hecto modules.

Original Arduino library by Nathan Seidle @ SparkFun Electronics
Python port maintains the same MIT License

https://github.com/sparkfun/Simultaneous_RFID_Tag_Reader
"""

from .rfid_reader import RFID, ModuleType, PinMode
from .constants import *

__version__ = "1.2.0"
__all__ = ["RFID", "ModuleType", "PinMode"]
