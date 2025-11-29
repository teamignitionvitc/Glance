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
# File:        simulator.py
# Author:      Shawn Liju Thomas
# Created On:  16-09-2025
#
# @brief       Simulates telemetry data for the dashboard.
# @details     Generates dummy data or reads from a backend source (Serial/TCP/UDP) and emits it via signals.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MODify | ADD | DELete)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      16-09-2025  Shawn Liju Thomas    Initial creation
####################################################################################################

####################################################################################################
# Imports

import time
import math
import random
from PySide6.QtCore import QThread, Signal
from .backend import DataReader

####################################################################################################

class DataSimulator(QThread):
    """
    @brief Thread for generating or reading telemetry data.
    @details Runs in a separate thread to prevent blocking the UI. Supports dummy data generation and backend connection.
    """
    newData = Signal(list) # Emits a list of values

    def __init__(self, num_channels=32, connection_settings=None, parameters=None):
        """
        @brief Initializes the simulator.
        @param num_channels Number of data channels to simulate/read.
        @param connection_settings Dictionary containing connection parameters.
        """
        super().__init__()
        self.num_channels = num_channels
        self._is_running = True
        self._is_paused = False
        self.mode = "dummy" # "dummy" or "backend"
        self.parameters = parameters or []
        self.connection_settings = connection_settings or {
            'mode': 'dummy',
            'serial_port': 'COM4',
            'baudrate': 115200,
            'tcp_host': '127.0.0.1',
            'tcp_port': 9000,
            'udp_host': '0.0.0.0',
            'udp_port': 9000,
            'timeout': 1.0,
            'data_format': 'json_array',
            'channel_count': 32,
            'sample_width_bytes': 2,
            'little_endian': True,
            'csv_separator': ',',
        }
        self.reader = None
        self._connection_error_shown = False

    def _init_backend_connection(self):
        """
        @brief Initialize backend connection if not already done.
        @return True if connection is successful or already active, False otherwise.
        """
        """Initialize backend connection if not already done"""
        if self.reader is not None:
            # Check if existing connection is still valid
            try:
                if hasattr(self.reader, 'sock') and self.reader.sock:
                    # For TCP/UDP, check if socket is still connected
                    return True
                elif hasattr(self.reader, 'ser') and self.reader.ser and self.reader.ser.is_open:
                    # For serial, check if port is still open
                    return True
                else:
                    # Connection was lost, clean up
                    try:
                        self.reader.close()
                    except:
                        pass
                    self.reader = None
            except:
                self.reader = None
        
        try:
            cs = self.connection_settings
            mode = cs.get('mode', 'serial')
            
            if not self._connection_error_shown:
                print(f"Attempting {mode.upper()} connection to {cs.get('tcp_host' if mode == 'tcp' else 'udp_host', '???')}:{cs.get('tcp_port' if mode == 'tcp' else 'udp_port', '???')}...")
            
            self.reader = DataReader(
                mode=mode,
                serial_port=cs.get('serial_port','COM4'),
                baudrate=cs.get('baudrate',115200),
                tcp_host=cs.get('tcp_host','127.0.0.1'),
                tcp_port=cs.get('tcp_port',9000),
                udp_host=cs.get('udp_host','0.0.0.0'),
                udp_port=cs.get('udp_port',9000),
                timeout=cs.get('timeout',1.0),
                data_format=cs.get('data_format','json_array'),
                channel_count=int(cs.get('channel_count',32)),
                sample_width_bytes=int(cs.get('sample_width_bytes',2)),
                little_endian=bool(cs.get('little_endian',True)),
                csv_separator=cs.get('csv_separator',','),
                parameters=self.parameters
            )
            
            # CRITICAL: Verify the connection actually works
            if mode == 'tcp' or mode == 'udp':
                if not hasattr(self.reader, 'sock') or self.reader.sock is None:
                    raise ConnectionError(f"{mode.upper()} socket not created")
            elif mode == 'serial':
                if not hasattr(self.reader, 'ser') or self.reader.ser is None or not self.reader.ser.is_open:
                    raise ConnectionError("Serial port not opened")
            
            print(f"✓ {mode.upper()} connection established!")
            self._connection_error_shown = False
            return True
            
        except Exception as e:
            # Connection failed
            if self.reader:
                try:
                    self.reader.close()
                except:
                    pass
                self.reader = None
            
            if not self._connection_error_shown:
                print(f"✗ Connection failed: {e}")
                self._connection_error_shown = True
            
            return False

    def run(self):
        """
        @brief Main thread loop.
        @details Continuously generates or reads data and emits the newData signal.
        """
        retry_delay = 1.0  # Start with 1 second delay
        max_retry_delay = 30.0  # Maximum 30 seconds between retries
        
        while self._is_running:
            if not self._is_paused:
                if self.mode == "dummy":
                    # Generate a full packet of dummy data as a list
                    packet = [0.0] * self.num_channels
                    timestamp = time.time()
                    for i in range(self.num_channels):
                        # Each index has a slightly different sine wave
                        value = 50 + 40 * math.sin(timestamp / (10 + i % 5) + i)
                        # Add some random noise/spikes
                        if random.random() > 0.98:
                            value = random.uniform(-10, 120)
                        packet[i] = value
                    self.newData.emit(packet)
                    time.sleep(0.1)

                elif self.mode == "backend":
                    # Try to initialize connection if needed
                    if not self._init_backend_connection():
                        print(f"Connection failed. Retrying in {retry_delay:.1f}s...")
                        time.sleep(retry_delay)
                        # Exponential backoff
                        retry_delay = min(retry_delay * 1.5, max_retry_delay)
                        continue
                    
                    # Connection successful, reset retry delay
                    retry_delay = 1.0
                    
                    try:
                        line = self.reader.read_line()
                        
                        if isinstance(line, list):
                            packet = line
                            self.newData.emit(packet)
                        
                        time.sleep(0.01)  # Small delay to prevent CPU hogging
                        
                    except Exception as e:
                        print(f"Error reading data: {e}")
                        # Close and reset reader on error to trigger reconnection
                        try:
                            if self.reader:
                                self.reader.close()
                        except:
                            pass
                        self.reader = None
                        self._connection_error_shown = False
                        # Don't sleep here - let the retry logic handle it
                        
            else:
                # Paused - just sleep
                time.sleep(0.1)

    def toggle_pause(self):
        """
        @brief Toggles the paused state of the simulator.
        @return The new paused state (True if paused, False if running).
        """
        self._is_paused = not self._is_paused
        return self._is_paused

    def stop(self):
        """
        @brief Stops the simulator thread and closes any active connections.
        """
        self._is_running = False
        if self.reader:
            try:
                self.reader.close()
            except:
                pass
