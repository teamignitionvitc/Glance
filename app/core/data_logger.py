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
# File:        data_logger.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Data logging functionality.
# @details     Handles logging of telemetry data to CSV and JSON formats with buffering.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side
#                                                layout and QStackedWidget
####################################################################################################

####################################################################################################
# Imports

import os
import csv
import json
import time
from datetime import datetime

####################################################################################################

class DataLogger:
    """
    @brief Handles data logging to CSV and JSON formats.
    @details Manages file creation, buffering, and writing of telemetry data.
    """
    
    def __init__(self):
        self.is_logging = False
        self.log_format = 'csv'  # 'csv' or 'json'
        self.log_file_path = None
        self.log_file = None
        self.csv_writer = None
        self.log_start_time = None
        self.parameters = []
        self.log_buffer = []
        self.buffer_size = 100  # Write to file every N entries
        
    def configure(self, format_type='csv', file_path=None, parameters=None, buffer_size=100):
        """
        @brief Configure the data logger.
        @param format_type The format to log data in ('csv' or 'json').
        @param file_path Optional custom path for the log file.
        @param parameters List of parameters to log.
        @param buffer_size Number of entries to buffer before writing to disk.
        """
        self.log_format = format_type
        self.parameters = parameters or []
        self.buffer_size = buffer_size
        
        if file_path:
            self.log_file_path = file_path
        else:
            # Create logs directory if it doesn't exist
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Generate default filename with timestamp in logs folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if format_type == 'csv':
                self.log_file_path = os.path.join(logs_dir, f"dashboard_data_{timestamp}.csv")
            else:
                self.log_file_path = os.path.join(logs_dir, f"dashboard_data_{timestamp}.json")
    
    def start_logging(self):
        """
        @brief Start data logging.
        @details Opens the log file and writes headers.
        @throws ValueError If log file path is not configured.
        """
        if not self.log_file_path:
            raise ValueError("No log file path configured")
        
        self.log_file = open(self.log_file_path, 'w', newline='', encoding='utf-8')
        self.log_start_time = time.time()
        
        if self.log_format == 'csv':
            # Write CSV header
            headers = ['timestamp', 'elapsed_time']
            for param in self.parameters:
                headers.append(f"{param['id']}_{param['name']}")
            self.csv_writer = csv.writer(self.log_file)
            self.csv_writer.writerow(headers)
        else:  # JSON format
            # Write JSON header comment
            self.log_file.write("# Dashboard Data Log\n")
            self.log_file.write("# Format: JSON Lines (one JSON object per line)\n")
            self.log_file.write(f"# Parameters: {', '.join([p['id'] for p in self.parameters])}\n")
            self.log_file.write("# Start Time: " + datetime.fromtimestamp(self.log_start_time).isoformat() + "\n\n")
        
        self.is_logging = True
        self.log_buffer = []
    
    def stop_logging(self):
        """
        @brief Stop data logging and flush buffer.
        @details Closes the log file and resets logging state.
        """
        if self.is_logging:
            self.flush_buffer()
            if self.log_file:
                self.log_file.close()
                self.log_file = None
            self.is_logging = False
    
    def log_data(self, packet_data, data_history):
        """
        @brief Log incoming data.
        @param packet_data The raw packet data (unused here, but kept for interface consistency).
        @param data_history Dictionary containing historical data for parameters.
        """
        if not self.is_logging:
            return
        
        timestamp = time.time()
        elapsed_time = timestamp - self.log_start_time
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'elapsed_time': elapsed_time,
            'data': {}
        }
        
        # Add parameter values from data history
        for param in self.parameters:
            param_id = param['id']
            if param_id in data_history and data_history[param_id]:
                latest_value = data_history[param_id][-1]['value']
                log_entry['data'][param_id] = latest_value
            else:
                log_entry['data'][param_id] = None
        
        self.log_buffer.append(log_entry)
        
        # Flush buffer if it's full
        if len(self.log_buffer) >= self.buffer_size:
            self.flush_buffer()
    
    def flush_buffer(self):
        """
        @brief Write buffered data to file.
        @details Flushes the internal buffer to the open log file.
        """
        if not self.log_buffer or not self.log_file:
            return
        
        if self.log_format == 'csv':
            for entry in self.log_buffer:
                row = [
                    datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    f"{entry['elapsed_time']:.3f}"
                ]
                for param in self.parameters:
                    value = entry['data'].get(param['id'])
                    row.append(f"{value:.6f}" if value is not None else "")
                self.csv_writer.writerow(row)
        else:  # JSON
            for entry in self.log_buffer:
                json_entry = {
                    'timestamp': datetime.fromtimestamp(entry['timestamp']).isoformat(),
                    'elapsed_time': entry['elapsed_time'],
                    'parameters': entry['data']
                }
                self.log_file.write(json.dumps(json_entry) + '\n')
        
        self.log_file.flush()
        self.log_buffer = []
