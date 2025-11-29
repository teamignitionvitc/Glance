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
# File:        test_backend.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Unit tests for backend module.
# @details     Tests data reading functionality.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side layout and QStackedWidget
####################################################################################################

####################################################################################################
# Imports

import pytest
from unittest.mock import MagicMock, patch
from app.core.backend import DataReader

class TestDataReader:
    def test_initialization(self):
        # Test default initialization
        with patch('app.core.backend.serial') as mock_serial:
            reader = DataReader(mode='serial')
            assert reader.mode == 'serial'
            assert reader.timeout == 1.0
            assert reader.data_format == 'json_array'

    def test_read_line_json(self):
        # Subclass to mock _read_bytes for testing parsing logic
        class MockDataReader(DataReader):
            def __init__(self, data_to_return):
                super().__init__(mode='serial') # Mode doesn't matter much here if we override _read_bytes
                self.data_to_return = data_to_return
                self.call_count = 0

            def _read_bytes(self):
                if self.call_count < len(self.data_to_return):
                    data = self.data_to_return[self.call_count]
                    self.call_count += 1
                    return data
                return None

        # Test valid JSON
        reader = MockDataReader([b'[1.0, 2.0, 3.0]'])
        data = reader.read_line()
        assert data == [1.0, 2.0, 3.0]

        # Test invalid JSON
        reader = MockDataReader([b'invalid'])
        data = reader.read_line()
        assert data is None

    def test_read_line_csv(self):
        class MockDataReader(DataReader):
            def __init__(self, data_to_return, **kwargs):
                super().__init__(mode='serial', data_format='csv', **kwargs)
                self.data_to_return = data_to_return
                self.call_count = 0

            def _read_bytes(self):
                if self.call_count < len(self.data_to_return):
                    data = self.data_to_return[self.call_count]
                    self.call_count += 1
                    return data
                return None

        # Test valid CSV
        reader = MockDataReader([b'1.0,2.0,3.0'])
        data = reader.read_line()
        assert data == [1.0, 2.0, 3.0]

        # Test with custom separator
        reader = MockDataReader([b'1.0;2.0;3.0'], csv_separator=';')
        data = reader.read_line()
        assert data == [1.0, 2.0, 3.0]
