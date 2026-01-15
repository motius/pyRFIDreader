"""
RFID Reader class for ThingMagic M6E Nano and M7E Hecto modules

This is a Python port of the SparkFun Arduino library for controlling
UHF RFID readers over serial connection.
"""

import time
import serial
from enum import Enum
from typing import Optional, Tuple

from . import constants as c


class ModuleType(Enum):
    """Supported RFID module types"""
    M6E_NANO = 0
    M7E_HECTO = 1


class PinMode(Enum):
    """GPIO pin modes"""
    INPUT = 0
    OUTPUT = 1


class RFID:
    """
    RFID Reader class for ThingMagic modules

    This class provides an interface to read and write RFID tags using
    ThingMagic M6E Nano or M7E Hecto modules over a serial connection.
    """

    def __init__(self):
        """Initialize the RFID reader"""
        self.serial_port: Optional[serial.Serial] = None
        self.module_type = ModuleType.M6E_NANO
        self.msg = bytearray(c.MAX_MSG_SIZE)
        self._head = 0
        self._print_debug = False

    def begin(self, port: str, baudrate: int = 115200,
              module_type: ModuleType = ModuleType.M6E_NANO,
              timeout: float = 1.0):
        """
        Initialize the serial connection to the RFID module

        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Baud rate for serial communication
            module_type: Type of ThingMagic module
            timeout: Serial port timeout in seconds
        """
        self.serial_port = serial.Serial(port, baudrate, timeout=timeout)
        self.module_type = module_type

        # Give the module time to initialize
        time.sleep(0.1)

        # Clear any startup messages
        if self.serial_port.in_waiting:
            self.serial_port.read(self.serial_port.in_waiting)

    def enable_debugging(self):
        """Enable debug message printing"""
        self._print_debug = True

    def disable_debugging(self):
        """Disable debug message printing"""
        self._print_debug = False

    def set_baud(self, baudrate: int):
        """
        Set the baud rate of the module

        Args:
            baudrate: Desired baud rate
        """
        data = baudrate.to_bytes(4, byteorder='big')
        self.send_message(c.TMR_SR_OPCODE_SET_BAUD_RATE, data,
                         wait_for_response=False)

    def get_version(self):
        """Get the firmware version from the module"""
        self.send_message(c.TMR_SR_OPCODE_VERSION)

    def set_read_power(self, power_setting: int):
        """
        Set the read TX power

        Args:
            power_setting: Power in centibels (e.g., 2700 = 27.00 dBm)
                          Maximum is 2700 (27.00 dBm)
        """
        if power_setting > 2700:
            power_setting = 2700

        data = power_setting.to_bytes(2, byteorder='big', signed=True)
        self.send_message(c.TMR_SR_OPCODE_SET_READ_TX_POWER, data)

    def get_read_power(self):
        """Get the current read TX power"""
        data = bytes([0x00])
        self.send_message(c.TMR_SR_OPCODE_GET_READ_TX_POWER, data)

    def set_write_power(self, power_setting: int):
        """
        Set the write TX power

        Args:
            power_setting: Power in centibels (e.g., 2700 = 27.00 dBm)
        """
        data = power_setting.to_bytes(2, byteorder='big', signed=True)
        self.send_message(c.TMR_SR_OPCODE_SET_WRITE_TX_POWER, data)

    def get_write_power(self):
        """Get the current write TX power"""
        data = bytes([0x00])
        self.send_message(c.TMR_SR_OPCODE_GET_WRITE_TX_POWER, data)

    def set_region(self, region: int):
        """
        Set the frequency region

        Args:
            region: Region code (e.g., REGION_NORTHAMERICA, REGION_EUROPE)
        """
        # Handle backwards compatibility for M6E Nano
        if region == c.REGION_NORTHAMERICA and self.module_type == ModuleType.M6E_NANO:
            region = c.REGION_NORTHAMERICA2

        data = bytes([region])
        self.send_message(c.TMR_SR_OPCODE_SET_REGION, data)

    def set_antenna_port(self):
        """Set TX and RX antenna ports to 1"""
        data = bytes([0x01, 0x01])  # TX port = 1, RX port = 1
        self.send_message(c.TMR_SR_OPCODE_SET_ANTENNA_PORT, data)

    def set_antenna_search_list(self):
        """Set antenna search list"""
        data = bytes([0x02, 0x01, 0x01])
        self.send_message(c.TMR_SR_OPCODE_SET_ANTENNA_PORT, data)

    def set_tag_protocol(self, protocol: int = 0x05):
        """
        Set the tag protocol

        Args:
            protocol: Protocol ID (default 0x05 = GEN2)
        """
        data = bytes([0x00, protocol])
        self.send_message(c.TMR_SR_OPCODE_SET_TAG_PROTOCOL, data)

    def start_reading(self):
        """
        Start continuous reading of tags

        This disables filtering and begins scanning for all tags continuously.
        """
        self.disable_read_filter()

        # Configuration blob for continuous reading
        config_blob = bytes([
            0x00, 0x00, 0x01, 0x22, 0x00, 0x00, 0x05, 0x07,
            0x22, 0x10, 0x00, 0x1B, 0x03, 0xE8, 0x01, 0xFF
        ])

        self.send_message(c.TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, config_blob)

    def stop_reading(self):
        """
        Stop continuous reading

        Give 1000-2000ms for the module to stop reading.
        """
        config_blob = bytes([0x00, 0x00, 0x02])
        self.send_message(c.TMR_SR_OPCODE_MULTI_PROTOCOL_TAG_OP, config_blob,
                         wait_for_response=False)

    def enable_read_filter(self):
        """Enable read filter"""
        self.set_reader_configuration(0x0C, 0x01)

    def disable_read_filter(self):
        """Disable read filter (allows continuous reading)"""
        self.set_reader_configuration(0x0C, 0x00)

    def set_reader_configuration(self, option1: int, option2: int):
        """
        Set reader configuration options

        Args:
            option1: First configuration option
            option2: Second configuration option
        """
        data = bytes([0x01, option1, option2])
        self.send_message(c.TMR_SR_OPCODE_SET_READER_OPTIONAL_PARAMS, data)

    def pin_mode(self, pin: int, mode: PinMode):
        """
        Set GPIO pin mode

        Args:
            pin: Pin number
            mode: PinMode.INPUT or PinMode.OUTPUT
        """
        data = bytes([0x01, pin, mode.value, 0x00])
        self.send_message(c.TMR_SR_OPCODE_SET_USER_GPIO_OUTPUTS, data)

    def digital_write(self, pin: int, state: int):
        """
        Set GPIO pin state (for OUTPUT pins)

        Args:
            pin: Pin number
            state: 0 (LOW) or 1 (HIGH)
        """
        data = bytes([pin, state])
        self.send_message(c.TMR_SR_OPCODE_SET_USER_GPIO_OUTPUTS, data)

    def digital_read(self, pin: int) -> bool:
        """
        Read GPIO pin state (for INPUT pins)

        Args:
            pin: Pin number

        Returns:
            Pin state (True=HIGH, False=LOW)
        """
        data = bytes([0x01])
        self.send_message(c.TMR_SR_OPCODE_GET_USER_GPIO_INPUTS, data)

        # Parse response
        length = self.msg[1] - 1
        offset = 6

        # Data is in sets of 3 bytes per pin
        for i in range(0, length, 3):
            if self.msg[i + offset] == pin:
                return bool(self.msg[i + offset + 2])

        return False

    def check(self) -> bool:
        """
        Check for incoming data and parse complete messages

        Returns:
            True if a complete message was received
        """
        if not self.serial_port or self.serial_port.in_waiting == 0:
            return False

        while self.serial_port.in_waiting > 0:
            incoming_byte = self.serial_port.read(1)[0]

            # Wait for header byte
            if self._head == 0 and incoming_byte != 0xFF:
                continue

            # Load value into array
            self.msg[self._head] = incoming_byte
            self._head += 1
            self._head %= c.MAX_MSG_SIZE

            # Check if we have a complete message
            if self._head > 0 and self._head == self.msg[1] + 7:
                # Complete message received

                # Clear remainder of array
                for x in range(self._head, c.MAX_MSG_SIZE):
                    self.msg[x] = 0

                self._head = 0

                if self._print_debug:
                    print("Response:", self._format_msg())

                return True

        return False

    def read_tag_epc(self, timeout: int = c.COMMAND_TIME_OUT) -> Tuple[int, bytes]:
        """
        Read a single tag's EPC

        Args:
            timeout: Timeout in milliseconds

        Returns:
            Tuple of (response_code, epc_data)
        """
        bank = 0x01  # EPC bank
        address = 0x02

        return self.read_data(bank, address, timeout=timeout)

    def write_tag_epc(self, new_epc: bytes, timeout: int = c.COMMAND_TIME_OUT) -> int:
        """
        Write a new EPC to a tag

        Use with caution - this writes to the first tag detected.

        Args:
            new_epc: New EPC data to write
            timeout: Timeout in milliseconds

        Returns:
            Response code
        """
        bank = 0x01
        address = 0x02

        return self.write_data(bank, address, new_epc, timeout)

    def read_user_data(self, timeout: int = c.COMMAND_TIME_OUT) -> Tuple[int, bytes]:
        """
        Read user data from tag (0-64 bytes typically available)

        Args:
            timeout: Timeout in milliseconds

        Returns:
            Tuple of (response_code, user_data)
        """
        bank = 0x03
        address = 0x00

        return self.read_data(bank, address, timeout=timeout)

    def write_user_data(self, user_data: bytes, timeout: int = c.COMMAND_TIME_OUT) -> int:
        """
        Write user data to tag

        Args:
            user_data: Data to write
            timeout: Timeout in milliseconds

        Returns:
            Response code
        """
        bank = 0x03
        address = 0x00

        return self.write_data(bank, address, user_data, timeout)

    def read_kill_password(self, timeout: int = c.COMMAND_TIME_OUT) -> Tuple[int, bytes]:
        """Read kill password (should be 4 bytes)"""
        return self.read_data(0x00, 0x00, timeout=timeout)

    def write_kill_password(self, password: bytes, timeout: int = c.COMMAND_TIME_OUT) -> int:
        """Write kill password (should be 4 bytes)"""
        return self.write_data(0x00, 0x00, password, timeout)

    def read_access_password(self, timeout: int = c.COMMAND_TIME_OUT) -> Tuple[int, bytes]:
        """Read access password (should be 4 bytes)"""
        return self.read_data(0x00, 0x02, timeout=timeout)

    def write_access_password(self, password: bytes, timeout: int = c.COMMAND_TIME_OUT) -> int:
        """Write access password (should be 4 bytes)"""
        return self.write_data(0x00, 0x02, password, timeout)

    def read_tid(self, timeout: int = c.COMMAND_TIME_OUT) -> Tuple[int, bytes]:
        """Read TID (Tag Identifier) - deprecated, use read_uid()"""
        return self.read_data(0x02, 0x02, timeout=timeout)

    def read_uid(self, timeout: int = c.COMMAND_TIME_OUT) -> Tuple[int, bytes]:
        """Read UID (Unique Identifier) from tag"""
        return self.read_data(0x02, 0x02, timeout=timeout)

    def read_data(self, bank: int, address: int,
                  timeout: int = c.COMMAND_TIME_OUT) -> Tuple[int, bytes]:
        """
        Read data from a specific memory bank and address

        Args:
            bank: Memory bank (0=passwords, 1=EPC, 2=TID, 3=user)
            address: Starting address
            timeout: Timeout in milliseconds

        Returns:
            Tuple of (response_code, data)
        """
        data = bytearray([
            (timeout >> 8) & 0xFF,  # Timeout MSB
            timeout & 0xFF,          # Timeout LSB
            0x10,                    # Option byte
            0x00,                    # Metadata MSB
            0x00,                    # Metadata LSB
            bank,                    # Bank
            (address >> 24) & 0xFF,  # Address bytes
            (address >> 16) & 0xFF,
            (address >> 8) & 0xFF,
            address & 0xFF,
            0x00                     # Read entire bank
        ])

        self.send_message(c.TMR_SR_OPCODE_READ_TAG_DATA, bytes(data),
                         timeout=timeout)

        if self.msg[0] == c.ALL_GOOD:
            status = (self.msg[3] << 8) | self.msg[4]

            if status == 0x0000:
                response_length = self.msg[1] - 3
                read_data = bytes(self.msg[8:8+response_length])
                return (c.RESPONSE_SUCCESS, read_data)

        return (c.RESPONSE_FAIL, b'')

    def write_data(self, bank: int, address: int, data_to_write: bytes,
                   timeout: int = c.COMMAND_TIME_OUT) -> int:
        """
        Write data to a specific memory bank and address

        Args:
            bank: Memory bank (0=passwords, 1=EPC, 2=TID, 3=user)
            address: Starting address
            data_to_write: Data to write
            timeout: Timeout in milliseconds

        Returns:
            Response code
        """
        data = bytearray([
            (timeout >> 8) & 0xFF,   # Timeout MSB
            timeout & 0xFF,           # Timeout LSB
            0x00,                     # Option initialize
            (address >> 24) & 0xFF,   # Address bytes
            (address >> 16) & 0xFF,
            (address >> 8) & 0xFF,
            address & 0xFF,
            bank                      # Bank
        ])

        data.extend(data_to_write)

        self.send_message(c.TMR_SR_OPCODE_WRITE_TAG_DATA, bytes(data), timeout)

        if self.msg[0] == c.ALL_GOOD:
            status = (self.msg[3] << 8) | self.msg[4]

            if status == 0x0000:
                return c.RESPONSE_SUCCESS

        return c.RESPONSE_FAIL

    def kill_tag(self, password: bytes, timeout: int = c.COMMAND_TIME_OUT) -> int:
        """
        Permanently kill a tag

        Use with extreme caution. This is irreversible.

        Args:
            password: Kill password (4 bytes)
            timeout: Timeout in milliseconds

        Returns:
            Response code
        """
        data = bytearray([
            (timeout >> 8) & 0xFF,  # Timeout MSB
            timeout & 0xFF,          # Timeout LSB
            0x00                     # Option initialize
        ])

        data.extend(password)
        data.append(0x00)  # RFU

        self.send_message(c.TMR_SR_OPCODE_KILL_TAG, bytes(data), timeout)

        if self.msg[0] == c.ALL_GOOD:
            status = (self.msg[3] << 8) | self.msg[4]

            if status == 0x0000:
                return c.RESPONSE_SUCCESS

        return c.RESPONSE_FAIL

    def parse_response(self) -> int:
        """
        Parse the response message

        Returns:
            Response type code
        """
        msg_length = self.msg[1] + 7
        opcode = self.msg[2]

        # Check CRC
        message_crc = self.calculate_crc(bytes(self.msg[1:msg_length-2]))
        if (self.msg[msg_length - 2] != (message_crc >> 8) or
            self.msg[msg_length - 1] != (message_crc & 0xFF)):
            return c.ERROR_CORRUPT_RESPONSE

        if opcode == c.TMR_SR_OPCODE_READ_TAG_ID_MULTIPLE:
            if self.msg[1] == 0x00:  # Keep alive
                status_msg = (self.msg[3] << 8) | self.msg[4]

                if status_msg == 0x0400:
                    return c.RESPONSE_IS_KEEPALIVE
                elif status_msg == 0x0504:
                    return c.RESPONSE_IS_TEMPTHROTTLE
                elif status_msg == 0x0505:
                    return c.RESPONSE_IS_HIGHRETURNLOSS
                else:
                    return c.RESPONSE_IS_UNKNOWN
            elif self.msg[1] == 0x08:
                return c.RESPONSE_IS_UNKNOWN
            elif self.msg[1] == 0x0A:
                return c.RESPONSE_IS_TEMPERATURE
            else:
                # Full tag record
                return c.RESPONSE_IS_TAGFOUND
        else:
            if self._print_debug:
                print(f"Unknown opcode in response: 0x{opcode:02X}")
            return c.ERROR_UNKNOWN_OPCODE

    def get_tag_epc_bytes(self) -> int:
        """Get the number of EPC bytes from the response"""
        tag_data_bytes = self.get_tag_data_bytes()

        epc_bits = (self.msg[27 + tag_data_bytes] << 8) | self.msg[28 + tag_data_bytes]
        epc_bytes = epc_bits // 8
        epc_bytes -= 4  # Ignore first two and last two bytes

        return epc_bytes

    def get_tag_data_bytes(self) -> int:
        """Get the number of tag data bytes from the response"""
        tag_data_length = (self.msg[24] << 8) | self.msg[25]
        tag_data_bytes = tag_data_length // 8

        if tag_data_length % 8 > 0:
            tag_data_bytes += 1  # Ceiling

        return tag_data_bytes

    def get_tag_timestamp(self) -> int:
        """Get the timestamp from the response"""
        timestamp = 0
        for x in range(4):
            timestamp |= self.msg[17 + x] << (8 * (3 - x))

        return timestamp

    def get_tag_freq(self) -> int:
        """Get the frequency from the response"""
        freq = 0
        for x in range(3):
            freq |= self.msg[14 + x] << (8 * (2 - x))

        return freq

    def get_tag_rssi(self) -> int:
        """Get the RSSI from the response"""
        return self.msg[12] - 256

    def send_message(self, opcode: int, data: bytes = b'',
                    timeout: int = c.COMMAND_TIME_OUT,
                    wait_for_response: bool = True):
        """
        Send a message to the module

        Args:
            opcode: Operation code
            data: Data bytes to send
            timeout: Timeout in milliseconds
            wait_for_response: Whether to wait for a response
        """
        self.msg[1] = len(data)
        self.msg[2] = opcode

        # Copy data into message array
        for x, byte in enumerate(data):
            self.msg[3 + x] = byte

        self.send_command(timeout, wait_for_response)

    def send_command(self, timeout: int = c.COMMAND_TIME_OUT,
                    wait_for_response: bool = True):
        """
        Send a command to the module

        Args:
            timeout: Timeout in milliseconds
            wait_for_response: Whether to wait for a response
        """
        self.msg[0] = 0xFF  # Universal header
        message_length = self.msg[1]
        opcode = self.msg[2]

        # Calculate and attach CRC
        crc = self.calculate_crc(bytes(self.msg[1:message_length + 3]))
        self.msg[message_length + 3] = crc >> 8
        self.msg[message_length + 4] = crc & 0xFF

        if self._print_debug:
            print("Send command:", self._format_msg()[:message_length + 5])

        if not self.serial_port:
            if self._print_debug:
                print("Error: Serial port not initialized")
            return

        # Clear incoming buffer
        if self.serial_port.in_waiting:
            self.serial_port.read(self.serial_port.in_waiting)

        # Send command
        self.serial_port.write(bytes(self.msg[:message_length + 5]))

        if not wait_for_response:
            self.serial_port.flush()
            return

        # Wait for response
        start_time = time.time()
        timeout_seconds = timeout / 1000.0

        while self.serial_port.in_waiting == 0:
            if time.time() - start_time > timeout_seconds:
                if self._print_debug:
                    print("Timeout: No response from module")
                self.msg[0] = c.ERROR_COMMAND_RESPONSE_TIMEOUT
                return
            time.sleep(0.001)

        # Read response
        message_length = c.MAX_MSG_SIZE - 1
        spot = 0

        while spot < message_length:
            if time.time() - start_time > timeout_seconds:
                if self._print_debug:
                    print("Timeout: Incomplete response")
                self.msg[0] = c.ERROR_COMMAND_RESPONSE_TIMEOUT
                return

            if self.serial_port.in_waiting > 0:
                self.msg[spot] = self.serial_port.read(1)[0]

                if spot == 1:
                    message_length = self.msg[1] + 7

                spot += 1

        if self._print_debug:
            print("Response:", self._format_msg()[:message_length])

        # Check CRC
        crc = self.calculate_crc(bytes(self.msg[1:message_length - 2]))
        if (self.msg[message_length - 2] != (crc >> 8) or
            self.msg[message_length - 1] != (crc & 0xFF)):
            self.msg[0] = c.ERROR_CORRUPT_RESPONSE
            if self._print_debug:
                print("Corrupt response")
            return

        # Check opcode matches
        if self.msg[2] != opcode:
            self.msg[0] = c.ERROR_WRONG_OPCODE_RESPONSE
            if self._print_debug:
                print("Wrong opcode response")
            return

        # All good
        self.msg[0] = c.ALL_GOOD

    @staticmethod
    def calculate_crc(data: bytes) -> int:
        """
        Calculate ThingMagic CRC

        Args:
            data: Data bytes to calculate CRC for

        Returns:
            16-bit CRC value
        """
        crc = 0xFFFF

        for byte in data:
            crc = ((crc << 4) | (byte >> 4)) ^ c.CRC_TABLE[crc >> 12]
            crc &= 0xFFFF  # Keep it 16-bit
            crc = ((crc << 4) | (byte & 0x0F)) ^ c.CRC_TABLE[crc >> 12]
            crc &= 0xFFFF  # Keep it 16-bit

        return crc

    def _format_msg(self) -> str:
        """Format message array for debug printing"""
        amt_to_print = min(self.msg[1] + 5, c.MAX_MSG_SIZE)
        return ' '.join([f"[{self.msg[x]:02X}]" for x in range(amt_to_print)])

    def close(self):
        """Close the serial connection"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
