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
# 000  NEW      04-02-2026  Shawn        First commit with the error checking logic

####################################################################################################

####################################################################################################
# Imports

import math
from typing import Dict, Tuple, Optional


class ErrorChecker:
    """
    @brief Lightweight error checker for telemetry parameter values.
    @details Validates values against their declared types and detects common error conditions.
    """
    
    # Type ranges for validation
    TYPE_RANGES = {
        'int8': (-128, 127),
        'int16': (-32768, 32767),
        'int32': (-2147483648, 2147483647),
        'uint8': (0, 255),
        'uint16': (0, 65535),
        'uint32': (0, 4294967295),
    }
    
    def __init__(self):
        """Initialize the error checker."""
        pass
    
    def check_value(self, param_meta: Dict, raw_value: any) -> Tuple[str, Optional[str]]:
        """
        @brief Check a parameter value for errors.
        @param param_meta: Parameter metadata dictionary with 'type', 'bit_length', etc.
        @param raw_value: The raw value to check
        @return Tuple of (status, message) where status is 'OK', 'WARNING', or 'ERROR'
        """
        if raw_value is None:
            return ('ERROR', 'Null value')
        
        # Convert to float for numeric checks if needed
        try:
            if isinstance(raw_value, (int, float)):
                numeric_value = float(raw_value)
            else:
                # Try to convert string to number
                numeric_value = float(raw_value)
        except (ValueError, TypeError):
            return ('ERROR', f'Invalid numeric type: {type(raw_value).__name__}')
        
        param_type = param_meta.get('type', 'float32')
        
        # Type-specific validation
        if param_type.startswith('int'):
            return self._check_int(param_type, numeric_value)
        elif param_type.startswith('uint'):
            return self._check_uint(param_type, numeric_value)
        elif param_type.startswith('float'):
            return self._check_float(param_type, numeric_value)
        elif param_type == 'Bitfield':
            return self._check_bitfield(param_meta, numeric_value)
        else:
            # Unknown type, do basic validation
            return self._check_generic(numeric_value)
    
    def _check_int(self, param_type: str, value: float) -> Tuple[str, Optional[str]]:
        """Check signed integer types."""
        # Check for NaN or infinity first
        if math.isnan(value) or math.isinf(value):
            return ('ERROR', f'{param_type}: NaN or Infinity')
        
        # Check if value is an integer (or close enough)
        if not isinstance(value, int) and abs(value - round(value)) > 1e-6:
            # Allow small floating point errors, but warn if significantly non-integer
            if abs(value - round(value)) > 0.1:
                return ('WARNING', f'{param_type}: Non-integer value')
        
        # Check range
        if param_type in self.TYPE_RANGES:
            min_val, max_val = self.TYPE_RANGES[param_type]
            if value < min_val or value > max_val:
                return ('ERROR', f'{param_type}: Out of range [{min_val}, {max_val}]')
        
        return ('OK', None)
    
    def _check_uint(self, param_type: str, value: float) -> Tuple[str, Optional[str]]:
        """Check unsigned integer types."""
        # Check for NaN or infinity first
        if math.isnan(value) or math.isinf(value):
            return ('ERROR', f'{param_type}: NaN or Infinity')
        
        # Check for negative values
        if value < 0:
            return ('ERROR', f'{param_type}: Negative value for unsigned type')
        
        # Check if value is an integer (or close enough)
        if not isinstance(value, int) and abs(value - round(value)) > 1e-6:
            if abs(value - round(value)) > 0.1:
                return ('WARNING', f'{param_type}: Non-integer value')
        
        # Check range
        if param_type in self.TYPE_RANGES:
            min_val, max_val = self.TYPE_RANGES[param_type]
            if value > max_val:
                return ('ERROR', f'{param_type}: Out of range [0, {max_val}]')
        
        return ('OK', None)
    
    def _check_float(self, param_type: str, value: float) -> Tuple[str, Optional[str]]:
        """Check float types."""
        # Check for NaN
        if math.isnan(value):
            return ('ERROR', f'{param_type}: NaN')
        
        # Check for infinity
        if math.isinf(value):
            return ('ERROR', f'{param_type}: Infinity')
        
        # Optional: Check for extremely large values (may indicate overflow)
        # Using reasonable limits for float32/64
        if param_type == 'float32':
            max_abs = 3.4e38  # Approximate max for float32
            if abs(value) > max_abs:
                return ('WARNING', f'{param_type}: Very large value (possible overflow)')
        elif param_type == 'float64':
            max_abs = 1.7e308  # Approximate max for float64
            if abs(value) > max_abs:
                return ('WARNING', f'{param_type}: Very large value (possible overflow)')
        
        return ('OK', None)
    
    def _check_bitfield(self, param_meta: Dict, value: float) -> Tuple[str, Optional[str]]:
        """Check bitfield types."""
        # Check for NaN or infinity
        if math.isnan(value) or math.isinf(value):
            return ('ERROR', 'Bitfield: NaN or Infinity')
        
        # Check if value is an integer
        if not isinstance(value, int) and abs(value - round(value)) > 1e-6:
            return ('ERROR', 'Bitfield: Non-integer value')
        
        int_value = int(round(value))
        
        # Check if value is non-negative
        if int_value < 0:
            return ('ERROR', 'Bitfield: Negative value')
        
        # Check bit length
        bit_length = param_meta.get('bit_length', 32)
        max_value = (1 << bit_length) - 1
        
        if int_value > max_value:
            return ('WARNING', f'Bitfield: Value exceeds {bit_length}-bit range')
        
        return ('OK', None)
    
    def _check_generic(self, value: float) -> Tuple[str, Optional[str]]:
        """Generic check for unknown types."""
        if math.isnan(value) or math.isinf(value):
            return ('ERROR', 'Invalid numeric value (NaN/Infinity)')
        return ('OK', None)
