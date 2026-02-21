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
# File:        error_checker.py
# Author:      Shawn Liju Thomas
# Created On:  04-02-2026
#
# @brief       Error checking for data.
# @details     Manages the handling and displaying of error data such as NaN ,Infinity values
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      04-02-2026  Shawn        First change for testing crc 

####################################################################################################

####################################################################################################
# Imports
import pytest
import zlib
import struct
import json
from app.core.error_checker import ErrorChecker

@pytest.fixture
def checker():
    return ErrorChecker()

def test_crc_none(checker):
    assert checker.calculate_crc(None) == zlib.crc32(b"") & 0xFFFFFFFF

def test_crc_string(checker):
    data = "hello world"
    assert checker.calculate_crc(data) == zlib.crc32(data.encode('utf-8')) & 0xFFFFFFFF

def test_crc_int(checker):
    data = 12345
    assert checker.calculate_crc(data) == zlib.crc32(str(data).encode('utf-8')) & 0xFFFFFFFF

def test_crc_float(checker):
    data = 123.456
    expected_bytes = struct.pack('d', data)
    assert checker.calculate_crc(data) == zlib.crc32(expected_bytes) & 0xFFFFFFFF

def test_crc_bytes(checker):
    data = b"\x01\x02\x03\x04"
    assert checker.calculate_crc(data) == zlib.crc32(data) & 0xFFFFFFFF

def test_crc_list(checker):
    data = [1, 2, 3]
    expected_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    assert checker.calculate_crc(data) == zlib.crc32(expected_bytes) & 0xFFFFFFFF

def test_crc_dict(checker):
    data = {"b": 2, "a": 1}
    # sort_keys=True is important for consistency
    expected_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    assert checker.calculate_crc(data) == zlib.crc32(expected_bytes) & 0xFFFFFFFF
    
    # Verify consistency regardless of input order
    data_alt = {"a": 1, "b": 2}
    assert checker.calculate_crc(data) == checker.calculate_crc(data_alt)

def test_crc_tuple(checker):
    data = (1, 2, 3)
    expected_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    assert checker.calculate_crc(data) == zlib.crc32(expected_bytes) & 0xFFFFFFFF
