"""
                                        ::                                                      
                                        ::                                                      
                                        ::                                                      
                                        ::                                                      
                                        ::                                                      
    ..    ..........    :.      ::      ::     .........  ..    ..........    ...      .        
    ::    ::            : .:.   ::     .::.       ::      ::    ::       :    :: :.    :        
    ::    ::   ..:::    :   .:. ::    ::::::      ::      ::    ::       :    ::   ::  :        
    ::    ::......::    :      :::    ::::::      ::      ::    ::.......:    ::     :::        
                                      ::::::                                                    
                                      :.::.:                                                    
                         .::::          ::          ::::.                                      
                       .::::::::.       ::       .:::::::::                                    
                       ::::::::::::....::::.....:::::::::::                                    
                        .:::::::::::::::::::::::::::::::::.        

                    Copyright (c) 2025 Ignition Software Department

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3, with the additional restriction
that this software may not be used for commercial purposes without
explicit written permission from the authors.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
####################################################################################################
# File:        backend.py
# Author:      Shawn Liju Thomas
# Created On:  16-09-2025
#
# @brief       This module serves as the backend for the Dashboard Builder project
# @details     Detailed explanation of module functionality and behavior
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MODify | ADD | DELete)
#       |
# No#   |       when       who                  what
######+*********+**********+********************+**************************************************
# 000  NEW      <Date>      <Author Name>        Initial creation
####################################################################################################

####################################################################################################
# Imports

import json
import re
import socket
import struct
from typing import Optional, List, Union

try:
    import serial  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    serial = None

####################################################################################################

class DataReader:
    """Flexible line-based reader supporting Serial, TCP, and UDP input.

    Expected payload format per line: JSON array like [1,2,3]. Semicolons are
    tolerated and converted to commas.
    """

    def __init__(
        self,
        mode: str = "serial",  # serial | tcp | udp
        serial_port: str = "COM4",
        baudrate: int = 115200,
        tcp_host: str = "127.0.0.1",
        tcp_port: int = 9000,
        udp_host: str = "0.0.0.0",
        udp_port: int = 9000,
        timeout: float = 1.0,
        data_format: str = "json_array",  # json_array | csv | raw_bytes | bits
        channel_count: int = 32,
        sample_width_bytes: int = 2,
        little_endian: bool = True,
        csv_separator: str = ",",
        parameters: list = None,
    ) -> None:
        self.mode = mode.lower()
        self.timeout = timeout
        self.rx_bytes: int = 0
        self._buffer = b""
        self.data_format = data_format
        self.channel_count = max(1, int(channel_count))
        self.sample_width_bytes = max(1, int(sample_width_bytes))
        self.little_endian = bool(little_endian)
        self.csv_separator = csv_separator or ","
        self.parameters = parameters or []
        
        # Pre-calculate struct format if possible
        self._struct_fmt = ""
        self._struct_size = 0
        self._bit_parsers = []
        if self.data_format == "binary_struct" and self.parameters:
            self._compile_struct()

        self.ser = None
        self.sock: Optional[socket.socket] = None

        if self.mode == "serial":
            if serial is None:
                print("pyserial not available; cannot open serial port")
                self.ser = None
            else:
                try:
                    self.ser = serial.Serial(port=serial_port, baudrate=baudrate, timeout=timeout)  # type: ignore
                except Exception as exc:
                    print("Could not open serial port", exc)
                    self.ser = None
        elif self.mode in ("tcp", "udp"):
            try:
                if self.mode == "tcp":
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(timeout)
                    s.connect((tcp_host, tcp_port))
                    self.sock = s
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(timeout)
                    s.bind((udp_host, udp_port))
                    self.sock = s
            except Exception as exc:
                print("Could not open network socket", exc)
                self.sock = None
        else:
            print(f"Unknown mode '{mode}', expected serial|tcp|udp")

    def _read_bytes(self) -> Optional[bytes]:
        try:
            if self.mode == "serial" and self.ser:
                data = self.ser.readline()
                if data:
                    self.rx_bytes += len(data)
                return data or None
            elif self.mode == "tcp" and self.sock:
                # Read chunks until we find a newline
                if b"\n" not in self._buffer:
                    chunk = self.sock.recv(4096)
                    if not chunk:
                        return None
                    self.rx_bytes += len(chunk)
                    self._buffer += chunk
                if b"\n" in self._buffer:
                    line, self._buffer = self._buffer.split(b"\n", 1)
                    return line + b"\n"
                return None
            elif self.mode == "udp" and self.sock:
                chunk, _ = self.sock.recvfrom(8192)
                if not chunk:
                    return None
                self.rx_bytes += len(chunk)
                # Assume each datagram is a logical line
                return chunk
            else:
                return None
        except Exception:
            return None

    def _compile_struct(self):
        """Compile the binary structure definition from parameters"""
        endian = "<" if self.little_endian else ">"
        fmt = endian
        total_bytes = 0
        current_bit_offset = 0
        
        # We need to handle bitfields manually, but standard types can be struct-packed
        # For simplicity in this version, we'll assume a mix of standard types and we'll
        # read them sequentially. Bitfields will need special handling if they are packed
        # into standard types (e.g. 32-bit int containing flags).
        
        # Current implementation: strictly sequential standard types
        # TODO: Advanced bit-packing support
        
        type_map = {
            'int8': 'b', 'uint8': 'B',
            'int16': 'h', 'uint16': 'H',
            'int32': 'i', 'uint32': 'I',
            'float32': 'f', 'float64': 'd'
        }
        
        self._parsers = []
        
        for p in self.parameters:
            ptype = p.get('type', 'float32')
            if ptype in type_map:
                char = type_map[ptype]
                fmt += char
                self._parsers.append({'type': 'standard', 'fmt': char})
            elif ptype == 'Bitfield':
                # For now, treat bitfield as uint32
                fmt += 'I'
                self._parsers.append({'type': 'bitfield', 'bits': p.get('bit_length', 32)})
            else:
                # Default to float
                fmt += 'f'
                self._parsers.append({'type': 'standard', 'fmt': 'f'})
                
        try:
            self._struct_size = struct.calcsize(fmt)
            self._struct_fmt = fmt
        except Exception as e:
            print(f"Struct compilation failed: {e}")
            self._struct_size = 0

    def _read_exact(self, size) -> Optional[bytes]:
        """Read exactly size bytes"""
        # Check buffer first
        if len(self._buffer) >= size:
            data = self._buffer[:size]
            self._buffer = self._buffer[size:]
            return data
            
        # Need more data
        needed = size - len(self._buffer)
        try:
            if self.mode == "serial" and self.ser:
                chunk = self.ser.read(needed)
                if chunk:
                    self._buffer += chunk
            elif self.mode in ("tcp", "udp") and self.sock:
                chunk = self.sock.recv(4096)
                if chunk:
                    self._buffer += chunk
        except Exception:
            pass
            
        if len(self._buffer) >= size:
            data = self._buffer[:size]
            self._buffer = self._buffer[size:]
            return data
        return None

    def _parse_binary_struct(self) -> Optional[List[float]]:
        if self._struct_size == 0:
            return None
            
        raw = self._read_exact(self._struct_size)
        if not raw:
            return None
            
        self.rx_bytes += len(raw)
        
        try:
            values = list(struct.unpack(self._struct_fmt, raw))
            # Post-process if needed (e.g. bitfields)
            # For now, we return the unpacked values directly
            # They map 1:1 to parameters in order
            return [float(v) for v in values]
        except Exception as e:
            print(f"Struct unpack error: {e}")
            return None

    def read_line(self) -> Union[None, List[float], str]:
        if self.data_format == "binary_struct":
            return self._parse_binary_struct()
            
        raw = self._read_bytes()
        if raw is None:
            return None
        try:
            if self.data_format == "json_array":
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    return None
                cleaned = line.replace(";", ",")
                if cleaned and cleaned[0] == "[":
                    arr = json.loads(cleaned)
                    return [float(x) for x in arr]
                return None
            elif self.data_format == "csv":
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    return None
                if self.csv_separator != ';':
                    line = line.replace(";", ",")
                parts = [p.strip() for p in line.split(self.csv_separator)]
                values = []
                for p in parts:
                    if p:
                        try:
                            values.append(float(p))
                        except ValueError:
                            pass
                if values:
                    return values
                return None
            elif self.data_format == "raw_bytes":
                buf = bytes(raw)
                width = self.sample_width_bytes
                total = len(buf) - (len(buf) % width)
                if total <= 0:
                    return None
                values: List[float] = []
                for i in range(0, min(total, self.channel_count * width), width):
                    chunk = buf[i:i+width]
                    val = int.from_bytes(chunk, byteorder="little" if self.little_endian else "big", signed=False)
                    values.append(float(val))
                return values if values else None
            elif self.data_format == "bits":
                # Parse an integer then expand to bits
                base_val: Optional[int] = None
                # Try JSON first
                try:
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if line and line[0] == "[":
                        arr = json.loads(line)
                        if isinstance(arr, list) and arr:
                            base_val = int(float(arr[0]))
                    elif line:
                        line = line.replace(";", ",")
                        parts = [p.strip() for p in line.split(self.csv_separator)]
                        if parts and parts[0]:
                            base_val = int(float(parts[0]))
                except Exception:
                    base_val = None
                if base_val is None:
                    # Fall back to raw bytes
                    buf = bytes(raw)
                    if len(buf) > 0:
                        base_val = int.from_bytes(buf, byteorder="little" if self.little_endian else "big", signed=False)
                if base_val is None:
                    return None
                bits: List[float] = []
                for b in range(self.channel_count):
                    bits.append(1.0 if (base_val >> b) & 1 else 0.0)
                return bits
            else:
                return None
        except Exception as e:
            print("Parse error:", e)
            return "Parse"

    def close(self) -> None:
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass



 