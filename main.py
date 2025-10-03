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
# File:        main.py
# Author:      Neil Baranwal
# Created On:  <Date>
#
# @brief       Brief description of the module purpose
# @details     Detailed explanation of module functionality and behavior
###################################################################################################
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
import sys
import random
import time
import json
import base64
import math
import uuid
import csv
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QComboBox, QLineEdit,
    QLabel, QFrame, QPushButton, QFileDialog, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QTabWidget,
    QDialog, QFormLayout, QDialogButtonBox, QDoubleSpinBox, QDockWidget,
    QSizePolicy, QInputDialog, QMessageBox, QTabBar, QAbstractItemView,
    QSpinBox, QStackedWidget, QCheckBox # --- NEW ---
)
from PySide6.QtCore import QThread, Signal, Qt, QTimer, QByteArray
from PySide6.QtGui import QFont, QColor, QBrush, QAction, QPixmap
import pyqtgraph as pg
import numpy as np
from backend import DataReader
from app.widgets import ValueCard, TimeGraph, LogTable, GaugeWidget, HistogramWidget, LEDWidget, MapWidget
from app.dialogs import ConnectionSettingsDialog, AddWidgetDialog, ParameterEntryDialog, ManageParametersDialog, DataLoggingDialog
try:
    from serial.tools import list_ports as _serial_list_ports  # type: ignore
except Exception:
    _serial_list_ports = None
import webbrowser
####################################################################################################


# --- 1. DATA LOGGING SYSTEM ---

class DataLogger:
    """Handles data logging to CSV and JSON formats"""
    
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
        """Configure the data logger"""
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
        """Start data logging"""
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
        """Stop data logging and flush buffer"""
        if self.is_logging:
            self.flush_buffer()
            if self.log_file:
                self.log_file.close()
                self.log_file = None
            self.is_logging = False
    
    def log_data(self, packet_data, data_history):
        """Log incoming data"""
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
        """Write buffered data to file"""
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


# --- 2. DATA SIMULATOR & WIDGETS ---
# --- 2. RAW TELEMETRY MONITOR ---

class RawTelemetryMonitor(QDialog):
    """Serial monitor-style window for viewing raw incoming data packets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Raw Telemetry Monitor")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
    
        # Header with stats
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(16)
        
        self.packet_count_label = QLabel("Packets: 0")
        self.packet_count_label.setStyleSheet("color: #00ff88; font-weight: bold; font-size: 13px;")
        self.byte_count_label = QLabel("Bytes: 0")
        self.byte_count_label.setStyleSheet("color: #00bfff; font-weight: bold; font-size: 13px;")
        self.rate_label = QLabel("Rate: 0.0/s")
        self.rate_label.setStyleSheet("color: #ffbf00; font-weight: bold; font-size: 13px;")
        
        header_layout.addWidget(QLabel("<b>Raw Telemetry Stream</b>"))
        header_layout.addStretch()
        header_layout.addWidget(self.packet_count_label)
        header_layout.addWidget(self.byte_count_label)
        header_layout.addWidget(self.rate_label)
        
        header.setStyleSheet("background-color: #2a2a2a; border-radius: 6px;")
        layout.addWidget(header)


        # Text display area
        from PySide6.QtWidgets import QTextEdit
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Consolas", 10))
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #0c0c0c;
                color: #00ff88;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.text_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.text_display)


        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_display)
        
        self.autoscroll_btn = QPushButton("Auto-scroll")
        self.autoscroll_btn.setCheckable(True)
        self.autoscroll_btn.setChecked(True)
        
        self.hex_btn = QPushButton("Show Hex")
        self.hex_btn.setCheckable(True)
        
        self.save_btn = QPushButton("Save to File...")
        self.save_btn.clicked.connect(self.save_to_file)
        
        # Only add close button if this is a standalone dialog (not embedded)
        if self.parent() is None or isinstance(self.parent(), QMainWindow):
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.close)
        else:
            close_btn = None
        
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.autoscroll_btn)
        btn_layout.addWidget(self.hex_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        if close_btn:
            btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)


        # Statistics
        self.packet_count = 0
        self.byte_count = 0
        self.packet_timestamps = []
        self.is_paused = False
        self.max_lines = 1000
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px 16px;
                color: #e0e0e0;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #333333;
                border-color: #66b3ff;
            }
            QPushButton:checked {
                background-color: #0a84ff;
                border-color: #0a84ff;
            }
        """)

    def append_packet(self, packet_data):
        """Append a new packet to the display"""
        if self.is_paused:
            return
        
        # Update statistics
        self.packet_count += 1
        current_time = time.time()
        self.packet_timestamps.append(current_time)
        
        # Calculate rolling rate (last 5 seconds)
        self.packet_timestamps = [ts for ts in self.packet_timestamps if current_time - ts < 5.0]
        if len(self.packet_timestamps) > 1:
            time_span = current_time - self.packet_timestamps[0]
            rate = len(self.packet_timestamps) / time_span if time_span > 0 else 0.0
        else:
            rate = 0.0
        
        # Format packet data
        timestamp_str = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        
        if self.hex_btn.isChecked():
            # Show as hex
            if isinstance(packet_data, list):
                hex_data = ' '.join([f'{int(v):02X}' if v is not None else 'XX' for v in packet_data])
                data_str = f"[HEX] {hex_data}"
                self.byte_count += len(packet_data)
            else:
                data_str = f"[HEX] {str(packet_data)}"
                self.byte_count += len(str(packet_data))
        else:
            # Show as decimal/json
            if isinstance(packet_data, list):
                data_str = f"[{', '.join([f'{v:.2f}' if v is not None else 'NULL' for v in packet_data])}]"
                self.byte_count += len(packet_data) * 4
            else:
                data_str = str(packet_data)
                self.byte_count += len(str(packet_data))
        
        # Create formatted line
        line = f"<span style='color: #888888;'>{timestamp_str}</span> " \
               f"<span style='color: #00bfff;'>[PKT {self.packet_count:06d}]</span> " \
               f"<span style='color: #00ff88;'>{data_str}</span>"
        
        # Append to display
        self.text_display.append(line)
        
        # Limit number of lines
        doc = self.text_display.document()
        if doc.blockCount() > self.max_lines:
            cursor = self.text_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
        
        # Auto-scroll to bottom
        if self.autoscroll_btn.isChecked():
            scrollbar = self.text_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        # Update labels
        self.packet_count_label.setText(f"Packets: {self.packet_count}")
        
        if self.byte_count < 1024:
            byte_str = f"{self.byte_count} B"
        elif self.byte_count < 1024 * 1024:
            byte_str = f"{self.byte_count/1024:.1f} KB"
        else:
            byte_str = f"{self.byte_count/(1024*1024):.1f} MB"
        self.byte_count_label.setText(f"Bytes: {byte_str}")
        
        self.rate_label.setText(f"Rate: {rate:.1f}/s")

    def toggle_pause(self):
        """Toggle pause state"""
        self.is_paused = self.pause_btn.isChecked()
        if self.is_paused:
            self.pause_btn.setText("Resume")
            self.text_display.append("<span style='color: #ffbf00;'>[PAUSED]</span>")
        else:
            self.pause_btn.setText("Pause")
            self.text_display.append("<span style='color: #00ff88;'>[RESUMED]</span>")
    
    def clear_display(self):
        """Clear the display"""
        self.text_display.clear()
        self.packet_count = 0
        self.byte_count = 0
        self.packet_timestamps.clear()
        self.packet_count_label.setText("Packets: 0")
        self.byte_count_label.setText("Bytes: 0")
        self.rate_label.setText("Rate: 0.0/s")

    def save_to_file(self):
        """Save the current display to a file"""
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Raw Telemetry", 
            f"raw_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text_display.toPlainText())
                QMessageBox.information(self, "Saved", f"Raw telemetry saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")


class StandaloneTelemetryViewer(QDialog):
    """Advanced standalone telemetry viewer - feature-rich serial monitor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Raw Telemetry Monitor")
        self.setMinimumSize(1100, 750)
        
        # Initialize state
        self.simulator = None
        self.connection_settings = {
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
        
        # Display settings
        self.display_mode = 'decimal'  # decimal, hex, ascii, binary, mixed
        self.timestamp_format = 'time'  # time, elapsed, none
        self.is_paused = False
        self.autoscroll_enabled = True
        self.line_ending = 'LF'  # LF, CR, CRLF, None
        
        # Statistics
        self.packet_count = 0
        self.byte_count = 0
        self.packet_timestamps = []
        self.start_time = time.time()
        self.error_count = 0
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top toolbar
        toolbar = self._build_toolbar()
        main_layout.addWidget(toolbar)
        
        # Statistics bar
        stats_bar = self._build_stats_bar()
        main_layout.addWidget(stats_bar)
        
        # Main display area with splitter
        splitter = QWidget()
        splitter_layout = QHBoxLayout(splitter)
        splitter_layout.setContentsMargins(0, 0, 0, 0)
        splitter_layout.setSpacing(0)
        
        # Left: Text display
        left_panel = self._build_display_panel()
        splitter_layout.addWidget(left_panel, 3)
        
        # Right: Control panel
        right_panel = self._build_control_panel()
        splitter_layout.addWidget(right_panel, 1)
        
        main_layout.addWidget(splitter)
        
        # Bottom: Send panel
        send_panel = self._build_send_panel()
        main_layout.addWidget(send_panel)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e0e0e0;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #333333;
                border-color: #66b3ff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
            QPushButton:checked {
                background-color: #0a84ff;
                border-color: #0a84ff;
            }
            QPushButton#PrimaryCTA {
                background-color: #1c9c4f;
                border-color: #1c9c4f;
            }
            QPushButton#PrimaryCTA:hover {
                background-color: #21b35a;
            }
            QPushButton#DangerCTA {
                background-color: #ff3b30;
                border-color: #ff3b30;
            }
            QPushButton#DangerCTA:hover {
                background-color: #ff4d42;
            }
            QLabel {
                color: #e0e0e0;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #2b2b2b;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px 8px;
                color: #e0e0e0;
                font-size: 11px;
            }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
                border-color: #66b3ff;
            }
            QTextEdit {
                background-color: #0c0c0c;
                border: 1px solid #333;
                border-radius: 4px;
                color: #00ff88;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10px;
                padding: 8px;
            }
            QCheckBox {
                color: #e0e0e0;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #4a4a4a;
                border-radius: 3px;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background-color: #0a84ff;
                border-color: #0a84ff;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(1000)
    
    def _build_toolbar(self):
        """Build top toolbar"""
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #2a2a2a; border-bottom: 1px solid #3a3a3a;")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        layout.addWidget(QLabel("<b>Connection:</b>"))
        
        self.settings_btn = QPushButton("Configure...")
        self.settings_btn.clicked.connect(self.open_connection_settings)
        layout.addWidget(self.settings_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setObjectName("PrimaryCTA")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        self.conn_status_label = QLabel("● Disconnected")
        self.conn_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")
        layout.addWidget(self.conn_status_label)
        
        layout.addWidget(self._create_separator())
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_display)
        layout.addWidget(self.clear_btn)
        
        layout.addWidget(self._create_separator())
        
        self.save_btn = QPushButton("Save Log...")
        self.save_btn.clicked.connect(self.save_to_file)
        layout.addWidget(self.save_btn)
        
        layout.addStretch()
        
        return toolbar
    
    def _build_stats_bar(self):
        """Build statistics bar"""
        stats = QWidget()
        stats.setStyleSheet("background-color: #252525; border-bottom: 1px solid #3a3a3a; padding: 6px;")
        layout = QHBoxLayout(stats)
        layout.setContentsMargins(12, 4, 12, 4)
        
        self.packets_stat = QLabel("Packets: 0")
        self.packets_stat.setStyleSheet("color: #00bfff; font-weight: bold;")
        
        self.bytes_stat = QLabel("Bytes: 0")
        self.bytes_stat.setStyleSheet("color: #00ff88; font-weight: bold;")
        
        self.rate_stat = QLabel("Rate: 0.0/s")
        self.rate_stat.setStyleSheet("color: #ffbf00; font-weight: bold;")
        
        self.errors_stat = QLabel("Errors: 0")
        self.errors_stat.setStyleSheet("color: #ff3131; font-weight: bold;")
        
        self.uptime_stat = QLabel("Uptime: 00:00:00")
        self.uptime_stat.setStyleSheet("color: #aaaaaa; font-weight: bold;")
        
        layout.addWidget(self.packets_stat)
        layout.addWidget(self._create_separator())
        layout.addWidget(self.bytes_stat)
        layout.addWidget(self._create_separator())
        layout.addWidget(self.rate_stat)
        layout.addWidget(self._create_separator())
        layout.addWidget(self.errors_stat)
        layout.addStretch()
        layout.addWidget(self.uptime_stat)
        
        return stats
    
    def _build_display_panel(self):
        """Build main text display panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        
        from PySide6.QtWidgets import QTextEdit
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Consolas", 10))
        self.text_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.text_display)
        
        return panel
    
    def _build_control_panel(self):
        """Build right control panel"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #252525; border-left: 1px solid #3a3a3a;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Display Mode
        display_group = QGroupBox("Display Mode")
        display_layout = QVBoxLayout(display_group)
        
        self.mode_decimal = QPushButton("Decimal")
        self.mode_decimal.setCheckable(True)
        self.mode_decimal.setChecked(True)
        self.mode_decimal.clicked.connect(lambda: self.set_display_mode('decimal'))
        
        self.mode_hex = QPushButton("Hexadecimal")
        self.mode_hex.setCheckable(True)
        self.mode_hex.clicked.connect(lambda: self.set_display_mode('hex'))
        
        self.mode_ascii = QPushButton("ASCII")
        self.mode_ascii.setCheckable(True)
        self.mode_ascii.clicked.connect(lambda: self.set_display_mode('ascii'))
        
        self.mode_binary = QPushButton("Binary")
        self.mode_binary.setCheckable(True)
        self.mode_binary.clicked.connect(lambda: self.set_display_mode('binary'))
        
        self.mode_mixed = QPushButton("Mixed (Hex + ASCII)")
        self.mode_mixed.setCheckable(True)
        self.mode_mixed.clicked.connect(lambda: self.set_display_mode('mixed'))
        
        display_layout.addWidget(self.mode_decimal)
        display_layout.addWidget(self.mode_hex)
        display_layout.addWidget(self.mode_ascii)
        display_layout.addWidget(self.mode_binary)
        display_layout.addWidget(self.mode_mixed)
        
        layout.addWidget(display_group)
        
        # Options
        options_group = QGroupBox("Display Options")
        options_layout = QVBoxLayout(options_group)
        
        self.show_timestamp = QCheckBox("Show Timestamps")
        self.show_timestamp.setChecked(True)
        
        self.show_packet_num = QCheckBox("Show Packet Numbers")
        self.show_packet_num.setChecked(True)
        
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)
        self.autoscroll_check.toggled.connect(lambda checked: setattr(self, 'autoscroll_enabled', checked))
        
        self.highlight_errors = QCheckBox("Highlight Errors")
        self.highlight_errors.setChecked(True)
        
        options_layout.addWidget(self.show_timestamp)
        options_layout.addWidget(self.show_packet_num)
        options_layout.addWidget(self.autoscroll_check)
        options_layout.addWidget(self.highlight_errors)
        
        layout.addWidget(options_group)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter text to highlight...")
        self.search_input.textChanged.connect(self.apply_search_filter)
        filter_layout.addWidget(self.search_input)
        
        layout.addWidget(filter_group)
        
        layout.addStretch()
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        reset_stats_btn = QPushButton("Reset Statistics")
        reset_stats_btn.clicked.connect(self.reset_statistics)
        actions_layout.addWidget(reset_stats_btn)
        
        screenshot_btn = QPushButton("Screenshot Display")
        screenshot_btn.clicked.connect(self.take_screenshot)
        actions_layout.addWidget(screenshot_btn)
        
        layout.addWidget(actions_group)
        
        return panel
    
    def _build_send_panel(self):
        """Build send data panel"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #252525; border-top: 1px solid #3a3a3a;")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        
        layout.addWidget(QLabel("<b>Send:</b>"))
        
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("Enter data to send...")
        self.send_input.returnPressed.connect(self.send_data)
        layout.addWidget(self.send_input)
        
        self.send_format = QComboBox()
        self.send_format.addItems(["Text", "Hex", "Binary"])
        self.send_format.setMinimumWidth(80)
        layout.addWidget(self.send_format)
        
        self.line_ending_combo = QComboBox()
        self.line_ending_combo.addItems(["None", "LF", "CR", "CRLF"])
        self.line_ending_combo.setCurrentText("LF")
        self.line_ending_combo.setMinimumWidth(80)
        layout.addWidget(self.line_ending_combo)
        
        send_btn = QPushButton("Send")
        send_btn.setObjectName("PrimaryCTA")
        send_btn.clicked.connect(self.send_data)
        layout.addWidget(send_btn)
        
        return panel
    
    def _create_separator(self):
        """Create vertical separator"""
        sep = QLabel("|")
        sep.setStyleSheet("color: #4a4a4a;")
        return sep
    
    def set_display_mode(self, mode):
        """Set display mode and update buttons"""
        self.display_mode = mode
        
        # Update button states
        self.mode_decimal.setChecked(mode == 'decimal')
        self.mode_hex.setChecked(mode == 'hex')
        self.mode_ascii.setChecked(mode == 'ascii')
        self.mode_binary.setChecked(mode == 'binary')
        self.mode_mixed.setChecked(mode == 'mixed')
    
    def open_connection_settings(self):
        """Open connection settings dialog"""
        dialog = ConnectionSettingsDialog(self.connection_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.connection_settings = dialog.get_settings()
    
    def toggle_connection(self):
        """Connect or disconnect"""
        if self.simulator and self.simulator.isRunning():
            self.disconnect_source()
        else:
            self.connect_source()
    
    def connect_source(self):
        """Start connection"""
        try:
            self.simulator = DataSimulator(
                num_channels=int(self.connection_settings.get('channel_count', 32)),
                connection_settings=self.connection_settings
            )
            
            if self.connection_settings['mode'] == 'dummy':
                self.simulator.mode = "dummy"
            else:
                self.simulator.mode = "backend"
            
            self.simulator.newData.connect(self.on_data_received)
            self.simulator.start()
            
            self.start_time = time.time()
            
            # Update UI
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setObjectName("DangerCTA")
            self.connect_btn.setStyleSheet("")
            self.settings_btn.setEnabled(False)
            
            mode = self.connection_settings['mode']
            if mode == 'dummy':
                self.conn_status_label.setText("● Connected (Dummy)")
            elif mode == 'serial':
                port = self.connection_settings.get('serial_port', 'N/A')
                self.conn_status_label.setText(f"● Connected ({port})")
            elif mode == 'tcp':
                host = self.connection_settings.get('tcp_host', 'N/A')
                port = self.connection_settings.get('tcp_port', 'N/A')
                self.conn_status_label.setText(f"● Connected ({host}:{port})")
            elif mode == 'udp':
                port = self.connection_settings.get('udp_port', 'N/A')
                self.conn_status_label.setText(f"● Listening (:{port})")
            
            self.conn_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect:\n{str(e)}")
            self.disconnect_source()
    
    def disconnect_source(self):
        """Stop connection"""
        if self.simulator:
            try:
                self.simulator.stop()
                self.simulator._is_paused = True
                if hasattr(self.simulator, 'reader') and self.simulator.reader:
                    try:
                        self.simulator.reader.close()
                    except Exception:
                        pass
                self.simulator.wait(1000)
            except Exception:
                pass
            self.simulator = None
        
        self.connect_btn.setText("Connect")
        self.connect_btn.setObjectName("PrimaryCTA")
        self.connect_btn.setStyleSheet("")
        self.settings_btn.setEnabled(True)
        self.conn_status_label.setText("● Disconnected")
        self.conn_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.is_paused = self.pause_btn.isChecked()
        if self.is_paused:
            self.pause_btn.setText("Resume")
            self.append_system_message("[PAUSED]")
        else:
            self.pause_btn.setText("Pause")
            self.append_system_message("[RESUMED]")
    
    def clear_display(self):
        """Clear display"""
        self.text_display.clear()
    
    def on_data_received(self, packet_data):
        """Handle incoming data"""
        if self.is_paused:
            return
        
        self.packet_count += 1
        timestamp = time.time()
        self.packet_timestamps.append(timestamp)
        
        # Format based on display mode
        if self.display_mode == 'decimal':
            data_str = self._format_decimal(packet_data)
        elif self.display_mode == 'hex':
            data_str = self._format_hex(packet_data)
        elif self.display_mode == 'ascii':
            data_str = self._format_ascii(packet_data)
        elif self.display_mode == 'binary':
            data_str = self._format_binary(packet_data)
        elif self.display_mode == 'mixed':
            data_str = self._format_mixed(packet_data)
        else:
            data_str = str(packet_data)
        
        # Build line
        line_parts = []
        
        if self.show_timestamp.isChecked():
            ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            line_parts.append(f"<span style='color: #888888;'>{ts}</span>")
        
        if self.show_packet_num.isChecked():
            line_parts.append(f"<span style='color: #00bfff;'>[{self.packet_count:06d}]</span>")
        
        line_parts.append(f"<span style='color: #00ff88;'>{data_str}</span>")
        
        line = " ".join(line_parts)
        
        # Append to display
        self.text_display.append(line)
        
        # Auto-scroll
        if self.autoscroll_enabled:
            scrollbar = self.text_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        # Update byte count
        if isinstance(packet_data, list):
            self.byte_count += len(packet_data) * 4  # Approximate
        else:
            self.byte_count += len(str(packet_data))
    
    def _format_decimal(self, data):
        """Format as decimal"""
        if isinstance(data, list):
            return ", ".join([f"{v:.2f}" if v is not None else "NULL" for v in data])
        return str(data)
    
    def _format_hex(self, data):
        """Format as hexadecimal"""
        if isinstance(data, list):
            hex_vals = []
            for v in data:
                if v is not None:
                    hex_vals.append(f"{int(v):02X}")
                else:
                    hex_vals.append("XX")
            return " ".join(hex_vals)
        return str(data)
    
    def _format_ascii(self, data):
        """Format as ASCII"""
        if isinstance(data, list):
            ascii_str = ""
            for v in data:
                if v is not None:
                    char_val = int(v) % 256
                    if 32 <= char_val <= 126:
                        ascii_str += chr(char_val)
                    else:
                        ascii_str += "."
                else:
                    ascii_str += "."
            return ascii_str
        return str(data)
    
    def _format_binary(self, data):
        """Format as binary"""
        if isinstance(data, list):
            return " ".join([f"{int(v):08b}" if v is not None else "........" for v in data])
        return str(data)
    
    def _format_mixed(self, data):
        """Format as hex + ASCII"""
        if isinstance(data, list):
            hex_part = self._format_hex(data)
            ascii_part = self._format_ascii(data)
            return f"{hex_part} | {ascii_part}"
        return str(data)
    
    def append_system_message(self, msg):
        """Append system message"""
        self.text_display.append(f"<span style='color: #ffbf00;'>{msg}</span>")
    
    def update_statistics(self):
        """Update statistics display"""
        # Packets
        self.packets_stat.setText(f"Packets: {self.packet_count}")
        
        # Bytes
        if self.byte_count < 1024:
            byte_str = f"{self.byte_count} B"
        elif self.byte_count < 1024 * 1024:
            byte_str = f"{self.byte_count/1024:.1f} KB"
        else:
            byte_str = f"{self.byte_count/(1024*1024):.1f} MB"
        self.bytes_stat.setText(f"Bytes: {byte_str}")
        
        # Rate
        current_time = time.time()
        self.packet_timestamps = [ts for ts in self.packet_timestamps if current_time - ts < 5.0]
        if len(self.packet_timestamps) > 1:
            time_span = current_time - self.packet_timestamps[0]
            rate = len(self.packet_timestamps) / time_span if time_span > 0 else 0.0
        else:
            rate = 0.0
        self.rate_stat.setText(f"Rate: {rate:.1f}/s")
        
        # Errors
        self.errors_stat.setText(f"Errors: {self.error_count}")
        
        # Uptime
        uptime = int(current_time - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        self.uptime_stat.setText(f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.packet_count = 0
        self.byte_count = 0
        self.packet_timestamps.clear()
        self.error_count = 0
        self.start_time = time.time()
        self.update_statistics()
    
    def save_to_file(self):
        """Save display to file"""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Telemetry Log",
            f"telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text_display.toPlainText())
                QMessageBox.information(self, "Saved", f"Log saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")
    
    def take_screenshot(self):
        """Take screenshot of display"""
        pixmap = self.text_display.grab()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "PNG Images (*.png);;All Files (*)"
        )
        if path:
            pixmap.save(path)
            QMessageBox.information(self, "Saved", f"Screenshot saved to:\n{path}")
    
    def apply_search_filter(self, text):
        """Apply search highlighting"""
        # This is a placeholder - full implementation would use QTextDocument find/highlight
        pass
    
    def send_data(self):
        """Send data through connection"""
        if not self.simulator or not self.simulator.isRunning():
            QMessageBox.warning(self, "Not Connected", "Please connect first before sending data.")
            return
        
        data = self.send_input.text()
        if not data:
            return
        
        # Add line ending
        line_ending = self.line_ending_combo.currentText()
        if line_ending == "LF":
            data += "\n"
        elif line_ending == "CR":
            data += "\r"
        elif line_ending == "CRLF":
            data += "\r\n"
        
        # Send data (this would need backend support)
        self.append_system_message(f"[SENT] {data.strip()}")
        self.send_input.clear()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.disconnect_source()
        super().closeEvent(event)

# --- MODIFIED: Now works with an array/list of data ---
class DataSimulator(QThread):
    newData = Signal(list) # Emits a list of values

    def __init__(self, num_channels=32, connection_settings=None):
        super().__init__()
        self.num_channels = num_channels
        self._is_running = True
        self._is_paused = False
        self.mode = "dummy" # "dummy" or "backend"
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

    def run(self):
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

                elif self.mode == "backend":
                    if not hasattr(self,"reader"):
                        # establish backend connection
                        cs = self.connection_settings
                        self.reader = DataReader(
                            mode=cs.get('mode','serial'),
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
                            csv_separator=cs.get('csv_separator',',')
                        )
                    line = self.reader.read_line()
                    
                    if isinstance(line,list):
                        packet = line
                        timestamp = time.time()
                        self.newData.emit(packet)
                    
            time.sleep(0.1)

    def toggle_pause(self):
        self._is_paused = not self._is_paused
        return self._is_paused

    def stop(self):
        self._is_running = False

class ValueCard(QFrame):
    def __init__(self, param_name, unit, priority):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
 
        # Title with icon
        title_layout = QHBoxLayout()
        title_label = QLabel(param_name)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Unit label
        unit_label = QLabel(unit)
        unit_label.setFont(QFont("Arial", 10))
        unit_label.setStyleSheet("color: #aaaaaa;")
        title_layout.addWidget(unit_label)
        
        # Value display
        self.value_label = QLabel("---")
        value_font = QFont("Monospace", 28, QFont.Weight.Bold)
        value_font.setStyleStrategy(QFont.PreferAntialias)
        self.value_label.setFont(value_font)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("color: #00ff88; padding: 8px;")
        
        layout.addLayout(title_layout)
        layout.addWidget(self.value_label)
        
        self.priority = priority
        self.set_alarm_state('Nominal')
    
    def update_value(self, value, alarm_state):
        if value is not None:
            self.value_label.setText(f"{value:.2f}")
        else:
            self.value_label.setText("NO DATA")
            self.value_label.setStyleSheet("color: #ff4444; padding: 8px;")
        self.set_alarm_state(alarm_state)
    
    def set_alarm_state(self, state):
        alarm_colors = {
            'Critical': '#FF3131', 
            'Warning': '#FFBF00', 
            'Nominal': '#1a1a1a'
        }
        priority_colors = {
            'High': '#FF3131', 
            'Medium': '#0078FF', 
            'Low': 'transparent'
        }
        bg_color = alarm_colors.get(state, '#1a1a1a')
        border_color = priority_colors.get(self.priority, 'transparent')
        self.setStyleSheet(f"""
            background-color: {bg_color}; 
            border-radius: 12px; 
            border: 3px solid {border_color};
            padding: 4px;
        """)

class TimeGraph(QWidget):
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs
        self.curves = {}
        self.last_known_values = {}

        # Toolbar
        container = QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        reset_btn = QPushButton("Reset View")
        reset_btn.setObjectName("SecondaryCTA")
        toolbar.addStretch()
        toolbar.addWidget(reset_btn)

        # Plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(QColor(12, 12, 12))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.25)
        self.plot_widget.setAntialiasing(True)
        self.plot_widget.setLabel('bottom', 'Time (s)', color='#FFFFFF')
        self.plot_widget.addLegend(offset=(10, 10))

        title = ", ".join([p['name'] for p in self.param_configs])
        units = list(set([p['unit'] for p in self.param_configs]))
        unit_label = units[0] if len(units) == 1 else "Multiple Units"
        self.plot_widget.setTitle(title, color='w', size='12pt')
        self.plot_widget.setLabel('left', unit_label, color='#FFFFFF')

        axis_pen = pg.mkPen(color='#FFFFFF', width=1)
        self.plot_widget.getAxis('left').setPen(axis_pen)
        self.plot_widget.getAxis('bottom').setPen(axis_pen)

        for p_config in self.param_configs:
            pen = pg.mkPen(p_config['color'], width=2.5)
            curve = self.plot_widget.plot(pen=pen, name=p_config['name'])
            self.curves[p_config['id']] = curve

        container.addLayout(toolbar)
        container.addWidget(self.plot_widget)
        self.setLayout(container)

        def _reset():
            try:
                self.plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
            except Exception:
                pass

        reset_btn.clicked.connect(_reset)

        self.start_time = time.time()
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('yellow', style=Qt.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('yellow', style=Qt.DashLine))
        self.label = pg.TextItem(color='white', anchor=(0, 1))
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.plot_widget.addItem(self.label)

        self.proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        self.plot_widget.scene().sigMouseClicked.connect(self.mouse_clicked)

    def update_data(self, history):
        for param_id, curve in self.curves.items():
            if param_id in history and history[param_id]:
                param_history = history[param_id]
                self.last_known_values[param_id] = param_history[-1]
                timestamps = [dp['timestamp'] - self.start_time for dp in param_history]
                values = [dp['value'] for dp in param_history]
                curve.setData(x=timestamps, y=values)

    def mouse_moved(self, evt):
        # --- NEW: Ignore hover interaction if Ctrl is pressed ---
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            return

        pos = evt[0]
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_widget.getPlotItem().vb.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            text = f"Time: {mousePoint.x():.2f}s\n"
            for pid, curve in self.curves.items():
                x_data, y_data = curve.getData()
                if x_data is not None and len(x_data) > 0:
                    idx = np.searchsorted(x_data, mousePoint.x())
                    if 0 < idx < len(x_data):
                        y_val = y_data[idx]
                        p_name = next(p['name'] for p in self.param_configs if p['id'] == pid)
                        text += f"{p_name}: {y_val:.2f}\n"
            self.label.setText(text.strip())
            self.label.setPos(mousePoint)

    def mouse_clicked(self, evt):
        if evt.double():
            return
        pos = self.plot_widget.getPlotItem().vb.mapSceneToView(evt.scenePos())
        min_dist = float('inf')
        nearest_point = None
        for pid, curve in self.curves.items():
            x_data, y_data = curve.getData()
            if x_data is None or len(x_data) == 0:
                continue
            for i, (x, y) in enumerate(zip(x_data, y_data)):
                dist = (x - pos.x())**2 + (y - pos.y())**2
                if dist < min_dist:
                    min_dist = dist
                    p_name = next(p['name'] for p in self.param_configs if p['id'] == pid)
                    nearest_point = (p_name, self.start_time + x, y)
        if nearest_point:
            name, ts, val = nearest_point
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
            QMessageBox.information(
                self,
                "Data Point Selected",
                f"Parameter: {name}\nValue: {val:.3f}\nTimestamp: {time_str}"
            )




class HistogramWidget(QWidget):
    def __init__(self, param_config):
        super().__init__(); self.param = param_config
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0)
        self.plot = pg.PlotWidget(); self.plot.setBackground(QColor(12,12,12)); self.plot.setMenuEnabled(False)
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.plot.setLabel('bottom', f"{param_config['name']} ({param_config['unit']})", color='#FFFFFF')
        self.bar_item = pg.BarGraphItem(x=[], height=[], width=0.9, brush='#39CCCC'); self.plot.addItem(self.bar_item)
        layout.addWidget(self.plot)
    def update_histogram(self, values):
        if not values: return
        try:
            arr = np.array(values, dtype=float)
            counts, edges = np.histogram(arr, bins=20)
            centers = (edges[:-1] + edges[1:]) / 2.0
            self.bar_item.setOpts(x=centers, height=counts, width=(edges[1]-edges[0])*0.9)
        except Exception:
            pass

class LEDWidget(QFrame):
    def __init__(self, param_config):
        super().__init__()
        self.param = param_config
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Clean parameter name
        clean_name = param_config['name'].replace('GPS(', '').replace(')', '') if param_config['name'].startswith('GPS(') else param_config['name']
        
        # Title with icon
        title_layout = QHBoxLayout()
        icon_label = QLabel("LED")
        icon_label.setFont(QFont("Arial", 14))
        title = QLabel(f"{clean_name}")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        if param_config.get('unit'):
            unit_label = QLabel(f"({param_config['unit']})")
            unit_label.setFont(QFont("Arial", 10))
            unit_label.setStyleSheet("color: #aaaaaa;")
            title_layout.addWidget(icon_label)
            title_layout.addWidget(title)
            title_layout.addWidget(unit_label)
            title_layout.addStretch()
        else:
            title_layout.addWidget(icon_label)
            title_layout.addWidget(title)
            title_layout.addStretch()
        
        # LED indicator
        self.led = QLabel("")
        self.led.setFixedSize(40, 40)
        self.led.setStyleSheet("""
            border-radius: 20px; 
            background: #555; 
            border: 3px solid #333;
        """)
        
        # Value display
        self.value_lbl = QLabel("--")
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_lbl.setFont(QFont("Monospace", 16, QFont.Weight.Bold))
        self.value_lbl.setStyleSheet("color: #ffffff;")
        
        layout.addLayout(title_layout)
        layout.addWidget(self.led, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_lbl)
        
        # Set frame style
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
            border: 2px solid #333;
        """)

    
    def update_value(self, value):
        try:
            v = float(value)
            self.value_lbl.setText(f"{v:.2f}")
        except Exception:
            self.value_lbl.setText("--")
            v = None
        
        # Determine LED state based on thresholds
        t = self.param.get('threshold', {'low_crit': 0, 'low_warn': 25, 'high_warn': 75, 'high_crit': 100})
        if v is not None:
            if v >= t.get('high_crit', 100):
                # Critical - red
                self.led.setStyleSheet("""
                    border-radius: 20px; 
                    background: #ff3131; 
                    border: 3px solid #ff6666;
                    box-shadow: 0 0 10px #ff3131;
                """)
            elif v >= t.get('high_warn', 75):
                # Warning - yellow
                self.led.setStyleSheet("""
                    border-radius: 20px; 
                    background: #ffbf00; 
                    border: 3px solid #ffcc33;
                    box-shadow: 0 0 10px #ffbf00;
                """)
            elif v >= t.get('low_warn', 25):
                # Normal - green
                self.led.setStyleSheet("""
                    border-radius: 20px; 
                    background: #21b35a; 
                    border: 3px solid #4ade80;
                    box-shadow: 0 0 10px #21b35a;
                """)
            else:
                # Low - blue
                self.led.setStyleSheet("""
                    border-radius: 20px; 
                    background: #0078ff; 
                    border: 3px solid #3b82f6;
                    box-shadow: 0 0 10px #0078ff;
                """)
        else:
            # No data - gray
            self.led.setStyleSheet("""
                border-radius: 20px; 
                background: #555; 
                border: 3px solid #333;
            """)

# Optional: Map widget using QWebEngineView if available
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
except Exception:
    QWebEngineView = None

class MapWidget(QWidget):
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs
        if len(param_configs) != 2:
            lbl = QLabel("Map requires [Lat, Lon] parameters")
            lay = QVBoxLayout(self)
            lay.addWidget(lbl)
            return
        
        self.lat_id = param_configs[0]['id']
        self.lon_id = param_configs[1]['id']
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Clean parameter names
        lat_name = param_configs[0]['name'].replace('GPS(', '').replace(')', '') if param_configs[0]['name'].startswith('GPS(') else param_configs[0]['name']
        lon_name = param_configs[1]['name'].replace('GPS(', '').replace(')', '') if param_configs[1]['name'].startswith('GPS(') else param_configs[1]['name']
        
        # Coordinates display (top label hidden when web map is available)
        self.coords_label = QLabel("No GPS data")
        self.coords_label.setFont(QFont("Monospace", 10))
        self.coords_label.setStyleSheet("color: #aaaaaa; padding: 4px;")
        self.coords_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Map widget
        if QWebEngineView:
            self.web = QWebEngineView()
            self.web.setMinimumHeight(200)
            layout.addWidget(self.web)
            # Embed a lightweight Leaflet map using OSM tiles, with a rocket emoji marker
            html = """
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
                  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
                <style>
                  html, body, #map { height: 100%; margin: 0; padding: 0; background: #1e1e1e; }
                  .leaflet-container { background: #1e1e1e; }
                  .rocket-icon { font-size: 28px; line-height: 28px; }
                  .rocket-icon span { filter: drop-shadow(0 0 2px #000); }
                    /* Make attribution minimally obtrusive while still visible */
                    .leaflet-control-attribution {
                      font-size: 10px;
                      opacity: 0.35;
                      background: rgba(0,0,0,0.25);
                      color: #ddd;
                    }
                    .leaflet-control-attribution:hover { opacity: 0.85; }
                    /* Style for custom magnifier control */
                    .leaflet-bar a.magnifier-btn {
                      font-size: 16px;
                      line-height: 26px;
                      text-align: center;
                      width: 26px;
                      height: 26px;
                      display: block;
                      text-decoration: none;
                      background: #fff;
                      color: #000;
                    }
                    .leaflet-bar a.magnifier-btn:hover { background: #f4f4f4; }
  /* Bottom-left overlay for coordinates */
  #coordsOverlay {
    position: absolute;
    bottom: 8px;
    left: 8px;
    z-index: 1000;
    background: rgba(0, 0, 0, 0.55);
    color: #eee;
    padding: 4px 8px;
    border-radius: 6px;
    font-family: monospace;
    font-size: 12px;
    pointer-events: none;
  }
                                  </style>
                                  <title>Map</title>
                                  <meta name="referrer" content="no-referrer">
                                  </head>
                                  <body>
                <div id="map"></div>
                <div id="coordsOverlay">Lat: ---, Lon: ---</div>
                                  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
                                    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
                                  <script>
                                    const initialLat = 0, initialLon = 0, initialZoom = 2;
                                    const map = L.map('map', { zoomControl: true }).setView([initialLat, initialLon], initialZoom);
                                    // Esri World Imagery (satellite) tiles - no API key required
                                    const tiles = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                                      maxZoom: 19,
                                      maxNativeZoom: 19,
                                      attribution: 'Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community'
                                    });
                                    tiles.addTo(map);
                                    // Prevent over-zooming beyond available data
                  const maxAvailableZoom = tiles.options.maxNativeZoom || tiles.options.maxZoom || 19;
                  const MAX_SAFE_ZOOM = Math.min(maxAvailableZoom, 17); // conservative cap to avoid empty tiles
                                    map.setMaxZoom(MAX_SAFE_ZOOM);
                                  
                                    const rocketIcon = L.divIcon({ className: 'rocket-icon', html: '<span>🚀</span>', iconSize: [28,28], iconAnchor: [14,14] });
                                    const marker = L.marker([initialLat, initialLon], { icon: rocketIcon }).addTo(map);
                                    // Red path line to track rocket trajectory
                                    const pathLine = L.polyline([], { color: 'red', weight: 3, opacity: 0.9 }).addTo(map);

                  function setOverlay(lat, lon) {
                    const el = document.getElementById('coordsOverlay');
                    if (el) {
                      el.textContent = `Lat: ${lat.toFixed(6)}, Lon: ${lon.toFixed(6)}`;
                    }
                  }
                    
                    // Custom magnifier control: zoom to current rocket position in one click
                    const focusControl = L.control({ position: 'topleft' });
                    focusControl.onAdd = function(map) {
                      const container = L.DomUtil.create('div', 'leaflet-bar');
                      const btn = L.DomUtil.create('a', 'magnifier-btn', container);
                      btn.href = '#';
                      btn.title = 'Zoom to rocket';
                      btn.innerHTML = '🔍';
                      L.DomEvent.on(btn, 'click', L.DomEvent.stopPropagation)
                                .on(btn, 'click', L.DomEvent.preventDefault)
                                .on(btn, 'click', function() {
                const ll = marker.getLatLng();
                const desiredZoom = Math.max(map.getZoom(), 18);
                const targetZoom = Math.min(desiredZoom, MAX_SAFE_ZOOM);
                map.setView(ll, targetZoom, { animate: true });
                                });
                      return container;
                    };
                    focusControl.addTo(map);
                
                  window.updatePosition = function(lat, lon) {
                    const ll = [lat, lon];
                    marker.setLatLng(ll);
                    // append to path
                    pathLine.addLatLng(ll);
                    setOverlay(lat, lon);
                    // zoom conservatively to avoid over-zooming beyond imagery
                    const desiredZoom = Math.max(map.getZoom(), 16);
                    const targetZoom = Math.min(desiredZoom, MAX_SAFE_ZOOM);
                    map.setView(ll, targetZoom, { animate: true });
                  };
                </script>
                </body>
                </html>
                """
            from PySide6.QtCore import QUrl
            self.web.setHtml(html, baseUrl=QUrl("https://local/"))
            # Hide the top coords label when web map is available
            self.coords_label.setVisible(False)
            # Prepare throttled updates every 10 seconds
            from PySide6.QtCore import QTimer
            self._last_sent_lat = None
            self._last_sent_lon = None
            self._update_timer = QTimer(self)
            self._update_timer.setInterval(10000)  # 10 seconds
            self._update_timer.timeout.connect(self._push_position)
            self._update_timer.start()
        else:
            self.web = None
            self.fallback = QLabel("WebEngine not available.\nShowing coordinates only.")
            self.fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fallback.setStyleSheet("color: #ffaa00; padding: 20px;")
            layout.addWidget(self.fallback)
        
        self._last_lat = None
        self._last_lon = None
        
        # Set frame style
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
            border: 2px solid #333;
        """)
    
    def update_position(self, history):
        lat_hist = history.get(self.lat_id, [])
        lon_hist = history.get(self.lon_id, [])
        if not lat_hist or not lon_hist:
            return
        
        lat = lat_hist[-1]['value']
        lon = lon_hist[-1]['value']
        self._last_lat, self._last_lon = lat, lon
        
        # Update text for fallback only; web overlay is updated in JS push
        if not self.web:
            self.coords_label.setText(f"Lat: {lat:.6f}° | Lon: {lon:.6f}°")
        else:
            if hasattr(self, 'fallback'):
                self.fallback.setText(f"Lat: {lat:.6f}°\nLon: {lon:.6f}°")

    def _push_position(self):
        # Called by timer every 10 seconds to push latest coords to the map
        if not self.web: return
        if self._last_lat is None or self._last_lon is None: return
        if self._last_sent_lat == self._last_lat and self._last_sent_lon == self._last_lon:
            return
        try:
            self.web.page().runJavaScript(f"updatePosition({self._last_lat}, {self._last_lon});")
            self._last_sent_lat = self._last_lat
            self._last_sent_lon = self._last_lon
        except Exception:
            pass

class LogTable(QWidget):
    # (Unchanged)
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs
        self.param_map = {p['id']: {'name': p['name'], 'col': i + 1} for i, p in enumerate(self.param_configs)}
        self.last_known_values = {}
        self.highlight_brush = QBrush(QColor("#0078FF").lighter(150))
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget()
        headers = ["Timestamp"] + [f"{p['name']} ({p['unit']})" for p in self.param_configs]
        self.table.setColumnCount(len(headers)); self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        search_group = QGroupBox("Search and Highlight")
        search_layout = QHBoxLayout(search_group)
        self.search_param_combo = QComboBox(); self.search_param_combo.addItems([p['name'] for p in self.param_configs])
        self.search_cond_combo = QComboBox(); self.search_cond_combo.addItems(["=", ">", "<", ">=", "<="])
        self.search_value_spinbox = QDoubleSpinBox(); self.search_value_spinbox.setRange(-1e9, 1e9); self.search_value_spinbox.setDecimals(4)
        search_btn = QPushButton("Search Last"); clear_btn = QPushButton("Clear")
        search_layout.addWidget(QLabel("Find in:")); search_layout.addWidget(self.search_param_combo)
        search_layout.addWidget(self.search_cond_combo); search_layout.addWidget(self.search_value_spinbox)
        search_layout.addWidget(search_btn); search_layout.addWidget(clear_btn)
        layout.addWidget(self.table); layout.addWidget(search_group)
        search_btn.clicked.connect(self.search_and_highlight)
        clear_btn.clicked.connect(self.clear_highlights)
    def update_data(self, updated_param_id, history):
        if self.table.rowCount() > 500: self.table.removeRow(500)
        self.table.insertRow(0)
        for pid in self.param_map.keys():
            if pid in history and history[pid]: self.last_known_values[pid] = history[pid][-1]
        ts_str = time.strftime('%H:%M:%S', time.localtime(self.last_known_values[updated_param_id]['timestamp']))
        self.table.setItem(0, 0, QTableWidgetItem(ts_str))
        for pid, pdata in self.param_map.items():
            value_str = "---"
            if pid in self.last_known_values: value_str = f"{self.last_known_values[pid]['value']:.3f}"
            self.table.setItem(0, pdata['col'], QTableWidgetItem(value_str))
    def clear_highlights(self):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item: item.setBackground(QBrush(QColor("transparent")))
    def search_and_highlight(self):
        self.clear_highlights()
        try:
            target_p_name = self.search_param_combo.currentText()
            target_col = self.search_param_combo.currentIndex() + 1
            target_val = self.search_value_spinbox.value()
            condition = self.search_cond_combo.currentText()
        except Exception as e:
            QMessageBox.warning(self, "Search Error", f"Invalid search criteria: {e}")
            return
        found_item = None
        for r in range(self.table.rowCount()):
            item = self.table.item(r, target_col)
            if not item or not item.text(): continue
            try:
                cell_val = float(item.text())
                match = False
                if condition == "=" and math.isclose(cell_val, target_val): match = True
                elif condition == ">" and cell_val > target_val: match = True
                elif condition == "<" and cell_val < target_val: match = True
                elif condition == ">=" and cell_val >= target_val: match = True
                elif condition == "<=" and cell_val <= target_val: match = True
                if match:
                    item.setBackground(self.highlight_brush)
                    found_item = item
                    break
            except ValueError:
                continue
        if found_item:
            self.table.scrollToItem(found_item, QAbstractItemView.ScrollHint.PositionAtCenter)
        else:
            QMessageBox.information(self, "Search", f"No value matching '{condition} {target_val}' found for '{target_p_name}'.")

# --- 2. DIALOGS ---


# --- MODIFIED: Added Array Index field ---
class ParameterEntryDialog(QDialog):
    def __init__(self, param=None, existing_ids=None, parent=None):
        super().__init__(parent); self.existing_ids = existing_ids or []; self.is_edit_mode = param is not None
        self.setWindowTitle("Edit Parameter" if self.is_edit_mode else "Add New Parameter"); layout = QFormLayout(self)
        self.id_edit = QLineEdit(param['id'] if param else "");
        if self.is_edit_mode: self.id_edit.setReadOnly(True)
        self.name_edit = QLineEdit(param['name'] if param else "")
        # --- NEW: Array Index Mapping ---
        self.index_spin = QSpinBox()
        self.index_spin.setRange(0, 255) # Assuming max 256 channels
        self.index_spin.setValue(param.get('array_index', 0) if param else 0)
        # ---
        self.group_edit = QLineEdit(param.get('sensor_group', '') if param else "")
        self.unit_edit = QLineEdit(param['unit'] if param else ""); self.desc_edit = QLineEdit(param.get('description', '') if param else "")
        self.low_crit, self.low_warn, self.high_warn, self.high_crit = QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox()
        for spin in [self.low_crit, self.low_warn, self.high_warn, self.high_crit]: spin.setRange(-100000, 100000); spin.setDecimals(3)
        if param:
            t = param.get('threshold', {}); self.low_crit.setValue(t.get('low_crit', 0)); self.low_warn.setValue(t.get('low_warn', 10))
            self.high_warn.setValue(t.get('high_warn', 80)); self.high_crit.setValue(t.get('high_crit', 100))
        layout.addRow("ID (unique, no spaces):", self.id_edit); layout.addRow("Display Name:", self.name_edit)
        layout.addRow("Array Index:", self.index_spin) # --- NEW ---
        layout.addRow("Sensor Group (e.g. MPU6050):", self.group_edit)
        layout.addRow("Unit:", self.unit_edit); layout.addRow("Description:", self.desc_edit); layout.addRow(QLabel("<b>Alarm Thresholds</b>"))
        layout.addRow("Low Critical:", self.low_crit); layout.addRow("Low Warning:", self.low_warn); layout.addRow("High Warning:", self.high_warn); layout.addRow("High Critical:", self.high_crit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def validate_and_accept(self):
        new_id = self.id_edit.text().strip()
        if ' ' in new_id: QMessageBox.warning(self, "Validation Error", "ID cannot contain spaces."); return
        if not new_id or not self.name_edit.text().strip(): QMessageBox.warning(self, "Validation Error", "ID and Name are required."); return
        if not self.is_edit_mode and new_id in self.existing_ids: QMessageBox.warning(self, "Validation Error", f"ID '{new_id}' already exists."); return
        if not (self.low_crit.value() < self.low_warn.value() < self.high_warn.value() < self.high_crit.value()):
            QMessageBox.warning(self, "Validation Error", "Thresholds must be in increasing order."); return
        self.accept()

    def get_data(self):
        return {'id': self.id_edit.text().strip(), 'name': self.name_edit.text().strip(),
                'array_index': self.index_spin.value(), # --- NEW ---
                'sensor_group': self.group_edit.text().strip(), 'unit': self.unit_edit.text().strip(),
                'description': self.desc_edit.text().strip(), 'threshold': {'low_crit': self.low_crit.value(), 'low_warn': self.low_warn.value(),
                'high_warn': self.high_warn.value(), 'high_crit': self.high_crit.value()}}

# --- MODIFIED: Added Array Index column ---
class ManageParametersDialog(QDialog):
    def __init__(self, parameters, parent=None):
        super().__init__(parent); self.setWindowTitle("Manage Telemetry Parameters"); self.parameters = parameters; self.setMinimumSize(800, 400)
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(6); self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Array Index', 'Sensor Group', 'Unit', 'Description'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.refresh_table()
        btn_layout = QHBoxLayout(); add_btn, edit_btn, remove_btn = QPushButton("Add..."), QPushButton("Edit..."), QPushButton("Remove")
        add_btn.clicked.connect(self.add_parameter); edit_btn.clicked.connect(self.edit_parameter); remove_btn.clicked.connect(self.remove_parameter)
        btn_layout.addWidget(add_btn); btn_layout.addWidget(edit_btn); btn_layout.addWidget(remove_btn)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close); buttons.clicked.connect(self.accept)
        layout.addWidget(self.table); layout.addLayout(btn_layout); layout.addWidget(buttons)

    def refresh_table(self):
        self.table.setRowCount(0)
        for p in self.parameters:
            row = self.table.rowCount(); self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p['id']))
            self.table.setItem(row, 1, QTableWidgetItem(p['name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get('array_index', 'N/A')))) # --- NEW ---
            self.table.setItem(row, 3, QTableWidgetItem(p.get('sensor_group', '')))
            self.table.setItem(row, 4, QTableWidgetItem(p['unit']))
            self.table.setItem(row, 5, QTableWidgetItem(p.get('description', '')))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def add_parameter(self):
        dialog = ParameterEntryDialog(existing_ids=[p['id'] for p in self.parameters], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted: self.parameters.append(dialog.get_data()); self.refresh_table()
    def edit_parameter(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        param_id = self.table.item(selected_rows[0].row(), 0).text()
        param_to_edit = next((p for p in self.parameters if p['id'] == param_id), None)
        if param_to_edit:
            dialog = ParameterEntryDialog(param=param_to_edit, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_data()
                for i, p in enumerate(self.parameters):
                    if p['id'] == param_id: self.parameters[i] = updated_data; break
                self.refresh_table()
    def remove_parameter(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        param_id = self.table.item(selected_rows[0].row(), 0).text()
        self.parameters[:] = [p for p in self.parameters if p['id'] != param_id]
        self.refresh_table()

# --- 3. MAIN APPLICATION WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Ignition Dashboard (PySide6)")
        # Improved initial sizing and centering
        self.setMinimumSize(1200, 720)
        self.resize(1200, 720)
        try:
            screen = self.screen() or QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                x = geo.x() + (geo.width() - self.width()) // 2
                y = geo.y() + (geo.height() - self.height()) // 3
                self.move(x, y)
        except Exception:
            pass
        self.graph_color_palette = ['#00BFFF', '#FF3131', '#39CCCC', '#F012BE', '#FFDC00', '#7FDBFF', '#01FF70', '#FF851B']
        self.next_graph_color_index = 0
        self.parameters = []; self.data_history = {}; self.tab_data = {}
        self.connection_settings = {
            'mode': 'dummy',
            'serial_port': 'COM4',
            'baudrate': 115200,
            'tcp_host': '127.0.0.1',
            'tcp_port': 9000,
            'udp_host': '0.0.0.0',
            'udp_port': 9000,
            'timeout': 1.0,
        }
        
        # Initialize data logger
        self.data_logger = DataLogger()
        self.logging_settings = None

        # Raw telemetry monitor
        self.raw_tlm_monitor = None
        
        # Track unsaved changes
        self.has_unsaved_changes = False
        self.current_project_path = None
        # Four-phase UI: Welcome -> Setup -> Widgets -> Dashboard
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.tab_widget = QTabWidget(); self.tab_widget.setTabsClosable(True)
        self.tab_widget.currentChanged.connect(self.on_tab_changed); self.tab_widget.tabCloseRequested.connect(self.close_tab)
        # Minimal list to track active displays; not shown in UI currently
        self.active_displays_list = QListWidget()
        header_widget = QWidget(); header_layout = QHBoxLayout(header_widget)
        self.stream_status_label = QLabel("Awaiting Parameters")
        self.connection_status_label = QLabel("Not Connected")
        self.pause_button = QPushButton("Pause Stream"); self.pause_button.setCheckable(True)
        self.logging_status_label = QLabel("Logging: OFF")
        # Customizable dashboard title
        self.dashboard_title = QLabel("<h2>Dashboard</h2>")
        self.dashboard_title.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.dashboard_title.customContextMenuRequested.connect(self._show_title_context_menu)
        self.dashboard_title_text = "Dashboard"
        self.dashboard_title_alignment = Qt.AlignmentFlag.AlignLeft

        header_layout.addWidget(self.dashboard_title); header_layout.addStretch()
        header_layout.addWidget(self.connection_status_label)
        header_layout.addWidget(self.stream_status_label)
        header_layout.addWidget(self.logging_status_label)
        header_layout.addWidget(self.pause_button)
        self.header_dock = QDockWidget(); self.header_dock.setTitleBarWidget(QWidget())
        self.header_dock.setWidget(header_widget); self.header_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.header_dock)
        self.health_timer = QTimer(self); self.health_timer.timeout.connect(self.check_data_stream); self.health_timer.start(1000)
        self.pause_button.clicked.connect(self.toggle_pause_stream); self.simulator = None
        self._build_menu_bar()
        self._build_status_bar()
        self.apply_stylesheet()
        self._build_welcome_page()
        self._build_setup_page()
        self._build_widgets_page()
        self._build_dashboard_page()
        self.show_phase("welcome")
        self.restart_simulator()
        self.update_control_states()
        
        # Initialize window title
        self.update_window_title()

    def refresh_setup_serial_ports(self):
        """Refresh the list of available serial ports in setup page"""
        current_text = self.setup_serial_port.currentText()
        self.setup_serial_port.clear()
        
        ports = self.list_serial_ports()
        self.setup_serial_port.addItems(ports)
        
        # Try to restore previous selection
        index = self.setup_serial_port.findText(current_text)
        if index >= 0:
            self.setup_serial_port.setCurrentIndex(index)
        else:
            self.setup_serial_port.setCurrentText(current_text)

    def list_serial_ports(self):
        ports = []
        try:
            if _serial_list_ports:
                ports = [p.device for p in _serial_list_ports.comports()]
        except Exception:
            ports = []
        # Add common defaults if none found
        if not ports:
            if sys.platform.startswith('linux'): ports = ['/dev/ttyUSB0', '/dev/ttyACM0']
            elif sys.platform.startswith('win'): ports = ['COM3','COM4','COM5']
            else: ports = ['/dev/tty.usbserial', '/dev/tty.usbmodem']
        return ports

    def create_control_dock(self):
        # Removed in favor of top-bar menus
        self.control_dock = None

    # --- MODIFIED: Handles new data source selection ---
    def on_source_changed(self, source_text):
        if not self.simulator: return
        if "Dummy" in source_text or "dummy" in self.simulator.mode:
            self.simulator.mode = "dummy"
            source_text = "Dummy Data"
            if self.simulator._is_paused: self.toggle_pause_stream()
        else: # Backend
            self.simulator.mode = "backend"
            source_text = "Backend"
            if not self.simulator._is_paused: self.toggle_pause_stream()
        self.update_status_bar()

    def add_widget_to_dashboard(self, config, tab_index, widget_id=None):
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        if widget_id is None: widget_id = str(uuid.uuid4())
        param_ids = config['param_ids']
        param_configs = [p for p in self.parameters if p['id'] in param_ids]
        if not param_configs: return
        widget_title = ", ".join([p['name'] for p in param_configs])
        widget = None
        if config['displayType'] == 'Time Graph':
            for p_config in param_configs:
                p_config['color'] = self.graph_color_palette[self.next_graph_color_index % len(self.graph_color_palette)]
                self.next_graph_color_index += 1
            widget = TimeGraph(param_configs)
        elif config['displayType'] == 'Log Table':
            widget = LogTable(param_configs)
        elif config['displayType'] == 'Instant Value' and len(param_configs) == 1:
            p_config = param_configs[0]
            widget = ValueCard(p_config['name'], p_config['unit'], config['priority'])
        elif config['displayType'] == 'Gauge' and len(param_configs) == 1:
            widget = GaugeWidget(param_configs[0])
        elif config['displayType'] == 'Histogram' and len(param_configs) == 1:
            widget = HistogramWidget(param_configs[0])
        elif config['displayType'] == 'LED Indicator' and len(param_configs) == 1:
            widget = LEDWidget(param_configs[0])
        elif config['displayType'] == 'Map (GPS)' and len(param_configs) == 2:
            widget = MapWidget(param_configs)
        
        if widget:
            # Set minimum sizes for better visibility
            widget.setMinimumSize(300, 200)
            if hasattr(widget, 'plot_widget'):  # For graphs
                widget.setMinimumSize(400, 300)
            elif hasattr(widget, 'table'):  # For tables
                widget.setMinimumSize(500, 300)
            dock = QDockWidget(f"{widget_title} ({config['displayType']})", self)
            dock.setObjectName(f"dock_{widget_id}")  # Set unique object name
            dock.setWidget(widget)
            dock.setMinimumSize(300, 200)
            # Add right-click context menu
            dock.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            dock.customContextMenuRequested.connect(lambda pos: self._show_dock_context_menu(dock, pos))
            tab_mainwindow = tab_info['mainwindow']
            num_docks = len(tab_info['docks'])
            docks_list = list(tab_info['docks'].values())
            if num_docks == 0:
                # First widget - add to left area
                tab_mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            elif num_docks == 1:
                # Second widget - split horizontally
                tab_mainwindow.splitDockWidget(docks_list[0], dock, Qt.Orientation.Horizontal)
                tab_info['last_orient'] = 'h'
            else:
                # Alternate split orientation relative to the last added dock to tile without removing
                last_dock = docks_list[-1]
                last_orient = tab_info.get('last_orient', 'v')
                orient = Qt.Orientation.Horizontal if last_orient == 'v' else Qt.Orientation.Vertical
                tab_mainwindow.splitDockWidget(last_dock, dock, orient)
                tab_info['last_orient'] = 'h' if orient == Qt.Orientation.Horizontal else 'v'
            tab_info['widgets'][widget_id] = widget; tab_info['docks'][widget_id] = dock; tab_info['configs'][widget_id] = config
            # Maintain layout positions for move/tile operations
            positions = tab_info.setdefault('layout_positions', {})
            positions[widget_id] = self._next_grid_position(positions)
            # Ensure new widget is visible and on top
            dock.show()
            dock.raise_()
            dock.activateWindow()
            self.refresh_active_displays_list()

    def _tile_widgets_in_grid(self, mainwindow, docks):
        """Arrange widgets in a grid pattern for better visibility"""
        if len(docks) < 3: return
        try:
            # Calculate grid dimensions
            cols = int(np.ceil(np.sqrt(len(docks))))
            rows = int(np.ceil(len(docks) / cols))
            # Clear existing layout
            for dock in docks:
                mainwindow.removeDockWidget(dock)
            # Add first dock
            mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, docks[0])
            # Add remaining docks in grid
            for i, dock in enumerate(docks[1:], 1):
                if i < cols:
                    # First row - split horizontally
                    mainwindow.splitDockWidget(docks[0], dock, Qt.Orientation.Horizontal)
                else:
                    # Subsequent rows - split vertically with dock above
                    above_dock = docks[i - cols]
                    mainwindow.splitDockWidget(above_dock, dock, Qt.Orientation.Vertical)
        except Exception:
            # Fallback to simple tabify
            for dock in docks[1:]:
                mainwindow.tabifyDockWidget(docks[0], dock)

    def _show_title_context_menu(self, pos):
        """Show context menu for dashboard title customization"""
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # Edit title action
        edit_action = menu.addAction("Edit Title...")
        edit_action.triggered.connect(self._edit_dashboard_title)
        
        menu.addSeparator()
        
        # Alignment submenu
        align_menu = menu.addMenu("Alignment")
        
        left_action = align_menu.addAction("Left")
        left_action.setCheckable(True)
        left_action.setChecked(self.dashboard_title_alignment == Qt.AlignmentFlag.AlignLeft)
        left_action.triggered.connect(lambda: self._set_title_alignment(Qt.AlignmentFlag.AlignLeft))
        
        center_action = align_menu.addAction("Center")
        center_action.setCheckable(True)
        center_action.setChecked(self.dashboard_title_alignment == Qt.AlignmentFlag.AlignCenter)
        center_action.triggered.connect(lambda: self._set_title_alignment(Qt.AlignmentFlag.AlignCenter))
        
        right_action = align_menu.addAction("Right")
        right_action.setCheckable(True)
        right_action.setChecked(self.dashboard_title_alignment == Qt.AlignmentFlag.AlignRight)
        right_action.triggered.connect(lambda: self._set_title_alignment(Qt.AlignmentFlag.AlignRight))
        
        menu.addSeparator()
        
        # Reset action
        reset_action = menu.addAction("Reset to Default")
        reset_action.triggered.connect(self._reset_dashboard_title)
        
        menu.exec(self.dashboard_title.mapToGlobal(pos))
    
    def _edit_dashboard_title(self):
        """Edit the dashboard title text"""
        new_title, ok = QInputDialog.getText(
            self, 
            "Edit Dashboard Title", 
            "Enter new title:",
            text=self.dashboard_title_text
        )
        if ok and new_title:
            self.dashboard_title_text = new_title
            self._update_dashboard_title()
            self.mark_as_unsaved()
    
    def _set_title_alignment(self, alignment):
        """Set the dashboard title alignment"""
        self.dashboard_title_alignment = alignment
        self._update_dashboard_title()
        self.mark_as_unsaved()
    
    def _reset_dashboard_title(self):
        """Reset dashboard title to default"""
        self.dashboard_title_text = "Dashboard"
        self.dashboard_title_alignment = Qt.AlignmentFlag.AlignLeft
        self._update_dashboard_title()
        self.mark_as_unsaved()
    
    def _update_dashboard_title(self):
        """Update the dashboard title display"""
        self.dashboard_title.setText(f"<h2>{self.dashboard_title_text}</h2>")
        self.dashboard_title.setAlignment(self.dashboard_title_alignment)
        
        # Force the label to expand to take up space for alignment to work
        if self.dashboard_title_alignment == Qt.AlignmentFlag.AlignCenter:
            self.dashboard_title.setMinimumWidth(300)
        elif self.dashboard_title_alignment == Qt.AlignmentFlag.AlignRight:
            self.dashboard_title.setMinimumWidth(300)
        else:
            self.dashboard_title.setMinimumWidth(0)

    def _show_dock_context_menu(self, dock, pos):
        """Right-click context menu for dock widgets"""
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        # Get widget info - store the dock reference directly
        self._context_dock = dock
        current_index = self.tab_widget.currentIndex()
        tinfo = self.tab_data.get(current_index, {})
        widget_id = None
        for wid, d in tinfo.get('docks', {}).items():
            if d == dock:
                widget_id = wid
                break
        
        if widget_id:
            rename_action = menu.addAction("Rename Widget")
            rename_action.triggered.connect(self._rename_widget_direct)
            float_action = menu.addAction("Float / Dock")
            float_action.triggered.connect(self._toggle_float_direct)
            menu.addSeparator()
            close_action = menu.addAction("Close Widget")
            close_action.triggered.connect(self._close_widget_direct)
            menu.addSeparator()
            tile_action = menu.addAction("Tile Evenly")
            tile_action.triggered.connect(lambda: self._tile_evenly_safe(current_index))  # Pass current_index
        else:
            menu.addAction("No actions available")
        menu.exec(dock.mapToGlobal(pos))
    

    def _next_grid_position(self, positions):
        """Compute next row,col for a new widget using a nearly square grid."""
        n = len(positions)
        if n == 0:
            return (0, 0)
        cols = int(np.ceil(np.sqrt(n + 1)))
        row = n // cols
        col = n % cols
        return (row, col)

    def _retile_positions(self, tab_index):
        """Retile docks based on saved positions (row, col) without changing assignments."""
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        docks = tab_info['docks']; positions = tab_info.get('layout_positions', {})
        if not docks: return
        # Order docks by row-major
        ordered = sorted(positions.items(), key=lambda x: (x[1][0], x[1][1]))
        dock_list = [docks[wid] for wid, _ in ordered]
        mw = tab_info['mainwindow']
        try:
            for d in dock_list:
                mw.removeDockWidget(d)
            mw.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_list[0])
            cols = max(1, len(set(c for _, (_, c) in positions.items())))
            for i, d in enumerate(dock_list[1:], 1):
                if i % cols != 0:
                    mw.splitDockWidget(dock_list[i - 1], d, Qt.Orientation.Horizontal)
                else:
                    above = dock_list[i - cols]
                    mw.splitDockWidget(above, d, Qt.Orientation.Vertical)
        except Exception:
            # Fallback to tabify
            for d in dock_list[1:]:
                mw.tabifyDockWidget(dock_list[0], d)

    def _rename_widget(self, widget_id):
        """Rename a widget"""
        tab_info = self.tab_data.get(self.tab_widget.currentIndex())
        if not tab_info or widget_id not in tab_info['docks']: return
        dock = tab_info['docks'][widget_id]
        current_name = dock.windowTitle()
        new_name, ok = QInputDialog.getText(self, "Rename Widget", "Enter new name:", text=current_name)
        if ok and new_name:
            dock.setWindowTitle(new_name)

    def _close_widget_direct(self):
        """Close the dock that was right-clicked"""
        if not hasattr(self, '_context_dock'): return
        dock = self._context_dock
        current_index = self.tab_widget.currentIndex()
        tab_info = self.tab_data.get(current_index)
        if not tab_info: return
        
        # Find the widget_id for this dock
        widget_id = None
        for wid, d in tab_info['docks'].items():
            if d == dock:
                widget_id = wid
                break
        
        if widget_id:
            dock.deleteLater()
            del tab_info['docks'][widget_id]
            if widget_id in tab_info['widgets']: 
                del tab_info['widgets'][widget_id]
            if widget_id in tab_info['configs']: 
                del tab_info['configs'][widget_id]
            if 'layout_positions' in tab_info and widget_id in tab_info['layout_positions']:
                del tab_info['layout_positions'][widget_id]
            self.refresh_active_displays_list()

    def _rename_widget_direct(self):
        """Rename the dock that was right-clicked"""
        if not hasattr(self, '_context_dock'): return
        dock = self._context_dock
        current_name = dock.windowTitle()
        new_name, ok = QInputDialog.getText(self, "Rename Widget", "Enter new name:", text=current_name)
        if ok and new_name:
            dock.setWindowTitle(new_name)

    def _toggle_float_direct(self):
        """Toggle float for the dock that was right-clicked"""
        if not hasattr(self, '_context_dock'): return
        dock = self._context_dock
        dock.setFloating(not dock.isFloating())
        if dock.isFloating():
            dock.raise_()
            dock.activateWindow()

    def _tile_evenly_safe(self, tab_index):
        """Safely tile widgets in a grid pattern"""
        tab_info = self.tab_data.get(tab_index)
        if not tab_info or not tab_info.get('docks'): 
            return
        
        docks_dict = tab_info['docks']
        docks = list(docks_dict.values())
        
        if len(docks) <= 1: 
            return
        
        mainwindow = tab_info['mainwindow']
        
        try:
            # Calculate grid dimensions
            n = len(docks)
            cols = int(np.ceil(np.sqrt(n)))
            
            # Store visibility and floating state
            dock_states = {}
            for dock in docks:
                dock_states[dock] = {
                    'visible': dock.isVisible(),
                    'floating': dock.isFloating()
                }
                # Make sure it's not floating for tiling
                if dock.isFloating():
                    dock.setFloating(False)
            
            # Remove all docks from layout
            for dock in docks:
                mainwindow.removeDockWidget(dock)
            
            # Add first dock
            mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, docks[0])
            docks[0].setVisible(True)
            docks[0].raise_()
            
            # Tile based on count
            if n == 2:
                mainwindow.splitDockWidget(docks[0], docks[1], Qt.Orientation.Horizontal)
                docks[1].setVisible(True)
            elif n == 3:
                mainwindow.splitDockWidget(docks[0], docks[1], Qt.Orientation.Horizontal)
                mainwindow.splitDockWidget(docks[0], docks[2], Qt.Orientation.Vertical)
                docks[1].setVisible(True)
                docks[2].setVisible(True)
            elif n == 4:
                mainwindow.splitDockWidget(docks[0], docks[1], Qt.Orientation.Horizontal)
                mainwindow.splitDockWidget(docks[0], docks[2], Qt.Orientation.Vertical)
                mainwindow.splitDockWidget(docks[1], docks[3], Qt.Orientation.Vertical)
                for dock in docks[1:4]:
                    dock.setVisible(True)
            else:
                # More than 4: create grid
                for i, dock in enumerate(docks[1:], 1):
                    if i < cols:
                        # First row: horizontal split
                        mainwindow.splitDockWidget(docks[0], dock, Qt.Orientation.Horizontal)
                    else:
                        # Subsequent rows: vertical split with dock above
                        above_idx = i - cols
                        if 0 <= above_idx < len(docks):
                            mainwindow.splitDockWidget(docks[above_idx], dock, Qt.Orientation.Vertical)
                    dock.setVisible(True)
            
            # Ensure all docks are visible and raised
            for dock in docks:
                dock.setVisible(True)
                dock.raise_()
            
            # Force layout update
            mainwindow.update()
            QApplication.processEvents()
            
        except Exception as e:
            # Emergency fallback - make sure docks are visible
            print(f"Tiling failed: {e}")
            import traceback
            traceback.print_exc()
            
            for dock in docks:
                try:
                    if not dock.parent():
                        mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
                    dock.setVisible(True)
                    dock.show()
                except Exception as e2:
                    print(f"Failed to recover dock: {e2}")

    def _toggle_float_widget(self, widget_id):
        tab_info = self.tab_data.get(self.tab_widget.currentIndex())
        if not tab_info or widget_id not in tab_info['docks']: return
        dock = tab_info['docks'][widget_id]
        dock.setFloating(not dock.isFloating())
        if dock.isFloating():
            dock.raise_(); dock.activateWindow()

    def _toggle_maximize_widget(self, widget_id):
        tab_info = self.tab_data.get(self.tab_widget.currentIndex())
        if not tab_info or widget_id not in tab_info['docks']: return
        mw = tab_info['mainwindow']
        docks = tab_info['docks']
        maximized = tab_info.get('maximized_widget_id')
        if maximized == widget_id:
            # Restore all docks
            for wid, d in docks.items():
                d.show()
            tab_info['maximized_widget_id'] = None
        elif maximized is None:
            # Hide all except this
            for wid, d in docks.items():
                if wid != widget_id:
                    d.hide()
            tab_info['maximized_widget_id'] = widget_id
        else:
            # Switch maximized target
            for wid, d in docks.items():
                d.setVisible(wid == widget_id)
            tab_info['maximized_widget_id'] = widget_id

    def _tile_evenly(self, tab_index):
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        # Reassign positions into an even grid
        positions = {}
        ids = list(tab_info['docks'].keys())
        for i, wid in enumerate(ids):
            positions[wid] = self._next_grid_position(positions)
        tab_info['layout_positions'] = positions
        self._retile_positions(tab_index)

    def _move_widget(self, widget_id, direction):
        """Move widget in specified direction within the grid and retile."""
        tab_index = self.tab_widget.currentIndex()
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        positions = tab_info.setdefault('layout_positions', {})
        if widget_id not in positions: return
        # Determine grid size
        cols = int(np.ceil(np.sqrt(max(1, len(positions)))))
        row, col = positions[widget_id]
        target = None
        if direction == 'left' and col > 0:
            target = (row, col - 1)
        elif direction == 'right':
            target = (row, col + 1)
        elif direction == 'up' and row > 0:
            target = (row - 1, col)
        elif direction == 'down':
            target = (row + 1, col)
        if target is None:
            return
        # Find widget at target; if none, just move into the spot
        swap_id = None
        for wid, pos in positions.items():
            if pos == target:
                swap_id = wid
                break
        positions[widget_id] = target
        if swap_id:
            positions[swap_id] = (row, col)
        # Normalize positions to a compact grid
        self._normalize_positions(positions)
        self._retile_positions(tab_index)

    def _normalize_positions(self, positions):
        """Compress rows/cols to remove gaps after moves/closures."""
        if not positions: return
        rows = sorted(set(r for (r, c) in positions.values()))
        cols = sorted(set(c for (r, c) in positions.values()))
        row_map = {r: i for i, r in enumerate(rows)}
        col_map = {c: i for i, c in enumerate(cols)}
        for wid, (r, c) in list(positions.items()):
            positions[wid] = (row_map[r], col_map[c])

    # --- HEAVILY MODIFIED: Core logic now processes an array, not a dict ---
    def update_data(self, packet: list):
        timestamp = time.time()

         # Track packets for status bar
        self.packet_count += 1
        self.packet_timestamps.append(timestamp)

        # Iterate through the user-defined parameters, not the incoming data keys
        for param_meta in self.parameters:
            param_id = param_meta['id']
            array_idx = param_meta.get('array_index')

            # Check if the parameter has a valid index and if the index is within the packet bounds
            if array_idx is not None and 0 <= array_idx < len(packet):
                value = packet[array_idx]
                if value is None: continue # Skip if data for this channel is null

                # --- The rest of the logic is the same, but now runs per-parameter ---
                if param_id not in self.data_history: self.data_history[param_id] = []
                self.data_history[param_id].append({'value': value, 'timestamp': timestamp})
                self.data_history[param_id] = self.data_history[param_id][-500:] # Limit history

                # Update relevant widgets for this specific parameter
                for tab_info in self.tab_data.values():
                    for widget_id, widget in tab_info['widgets'].items():
                        config = tab_info['configs'][widget_id]
                        if param_id in config['param_ids']:
                            if isinstance(widget, ValueCard):
                                alarm_state = self.get_alarm_state(value, param_meta['threshold'])
                                widget.update_value(value, alarm_state)
                            elif isinstance(widget, TimeGraph):
                                widget.update_data(self.data_history)
                            elif isinstance(widget, LogTable):
                                widget.update_data(param_id, self.data_history)
                            elif isinstance(widget, GaugeWidget):
                                widget.update_value(value)
                            elif isinstance(widget, HistogramWidget):
                                hist_vals = [dp['value'] for dp in self.data_history.get(param_id, [])]
                                widget.update_histogram(hist_vals)
                            elif isinstance(widget, LEDWidget):
                                widget.update_value(value)
                            elif isinstance(widget, MapWidget):
                                widget.update_position(self.data_history)
        
        # Log data if logging is enabled
        if self.data_logger.is_logging:
            self.data_logger.log_data(packet, self.data_history)

        # Send to raw telemetry monitor if open
        if self.raw_tlm_monitor and self.raw_tlm_monitor.isVisible():
            self.raw_tlm_monitor.append_packet(packet)

    def restart_simulator(self):
        if self.simulator: 
            self.simulator.stop()
            self.simulator.wait()
        
        self.simulator = DataSimulator(num_channels=32, connection_settings=self.connection_settings)
        
        # Set mode based on connection settings
        mode = self.connection_settings.get('mode', 'dummy')
        if mode == 'dummy':
            self.simulator.mode = "dummy"
        else:
            self.simulator.mode = "backend"
        
        # Connect the signal for both modes
        self.simulator.newData.connect(self.update_data)
        self.simulator.start()
        self.update_status_bar()
        self.update_connection_status()

    # --- All other MainWindow methods are unchanged ---
    def open_add_widget_dialog(self):
        index = self.tab_widget.currentIndex()
        if index < 0: QMessageBox.warning(self, "No Tab", "No active tab to add a widget to."); return
        dialog = AddWidgetDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selection = dialog.get_selection()
            if selection: self.add_widget_to_dashboard(selection, index)
    def remove_selected_display(self):
        """Remove a widget via dialog selection"""
        index = self.tab_widget.currentIndex()
        if index < 0: 
            QMessageBox.warning(self, "No Tab", "No active tab.")
            return
        
        tab_info = self.tab_data.get(index)
        if not tab_info or not tab_info['configs']:
            QMessageBox.information(self, "No Widgets", "No widgets to remove in current tab.")
            return
        
        # Create a selection dialog
        widget_names = []
        widget_ids = []
        for widget_id, config in tab_info['configs'].items():
            param_names = [p['name'] for p in self.parameters if p['id'] in config['param_ids']]
            display_name = f"{', '.join(param_names)} ({config['displayType']})"
            widget_names.append(display_name)
            widget_ids.append(widget_id)
        
        item, ok = QInputDialog.getItem(
            self, 
            "Remove Widget", 
            "Select widget to remove:",
            widget_names,
            0,
            False
        )
        
        if ok and item:
            # Find the widget_id for the selected item
            selected_index = widget_names.index(item)
            widget_id = widget_ids[selected_index]
            
            # Remove the widget
            if widget_id in tab_info['docks']:
                tab_info['docks'][widget_id].deleteLater()
                del tab_info['docks'][widget_id]
            if widget_id in tab_info['widgets']:
                del tab_info['widgets'][widget_id]
            if widget_id in tab_info['configs']:
                del tab_info['configs'][widget_id]
            if 'layout_positions' in tab_info and widget_id in tab_info['layout_positions']:
                del tab_info['layout_positions'][widget_id]
            
            self.refresh_active_displays_list()
            self.mark_as_unsaved()

    def refresh_active_displays_list(self):
        self.active_displays_list.clear(); index = self.tab_widget.currentIndex()
        if index < 0 or index not in self.tab_data: return
        tab_info = self.tab_data.get(index)
        for widget_id, config in tab_info['configs'].items():
            param_names = [p['name'] for p in self.parameters if p['id'] in config['param_ids']]
            display_name = f"{', '.join(param_names)} ({config['displayType']})"
            item = QListWidgetItem(display_name); item.setData(Qt.ItemDataRole.UserRole, widget_id)
            self.active_displays_list.addItem(item)
    def open_manage_parameters_dialog(self):
        dialog = ManageParametersDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
             self.update_control_states() # No need to restart simulator anymore
             self.mark_as_unsaved()
             QMessageBox.information(self, "Update", "Parameter definitions have been updated.")
    def update_control_states(self):
        has_params = bool(self.parameters)
        if hasattr(self, 'add_widget_btn') and self.add_widget_btn:
            self.add_widget_btn.setEnabled(has_params)
    def add_new_tab(self, name=None, is_closable=True):
        if name is None:
            name, ok = QInputDialog.getText(self, "New Tab", "Enter tab name:")
            if not ok or not name: return
        tab_main_window = QMainWindow()
        tab_main_window.setDockNestingEnabled(True)
        tab_index = self.tab_widget.addTab(tab_main_window, name)
        self.tab_data[tab_index] = {'mainwindow': tab_main_window, 'widgets': {}, 'docks': {}, 'configs': {}}
        if not is_closable:
            self.tab_widget.tabBar().setTabButton(tab_index, QTabBar.ButtonPosition.RightSide, None)
        self.tab_widget.setCurrentIndex(tab_index)
        return tab_index
    def close_tab(self, index):
        if index < 0 or index not in self.tab_data: return
        tab_info = self.tab_data[index]
        for dock in tab_info['docks'].values(): dock.deleteLater()
        tab_info['mainwindow'].deleteLater()
        del self.tab_data[index]
        self.tab_widget.removeTab(index)
        self.refresh_active_displays_list()
    def rename_current_tab(self):
        index = self.tab_widget.currentIndex()
        if index < 0: return
        current_name = self.tab_widget.tabText(index)
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new tab name:", text=current_name)
        if ok and new_name: self.tab_widget.setTabText(index, new_name)
    def on_tab_changed(self, index): self.refresh_active_displays_list()
    def get_alarm_state(self, value, thresholds):
        if value < thresholds['low_crit'] or value > thresholds['high_crit']: return 'Critical'
        if value < thresholds['low_warn'] or value > thresholds['high_warn']: return 'Warning'
        return 'Nominal'
    def toggle_pause_stream(self):
        if self.simulator:
            is_paused = self.simulator.toggle_pause()
            self.pause_button.setText("Resume Stream" if is_paused else "Pause Stream")
    def check_data_stream(self):
        if not self.parameters:
            self.stream_status_label.setText("Awaiting Parameters")
            self.stream_status_label.setStyleSheet("color: #FFBF00;")
        elif self.simulator and not self.simulator._is_paused:
            self.stream_status_label.setText("STREAMING")
            self.stream_status_label.setStyleSheet("color: #01FF70;")
        else:
            self.stream_status_label.setText("PAUSED")
            self.stream_status_label.setStyleSheet("color: #FF3131;")
        
        # Update connection status
        self.update_connection_status()
    def mark_as_unsaved(self):
        """Mark the project as having unsaved changes"""
        self.has_unsaved_changes = True
        self.update_window_title()
    
    def mark_as_saved(self):
        """Mark the project as saved"""
        self.has_unsaved_changes = False
        self.update_window_title()
    
    def update_window_title(self):
        """Update window title to show unsaved changes"""
        base_title = "Glance"
        if self.current_project_path:
            filename = os.path.basename(self.current_project_path)
            title = f"{base_title} - {filename}"
        else:
            title = f"{base_title} - Untitled"
        
        if self.has_unsaved_changes:
            title += " *"
        
        self.setWindowTitle(title)
    
    def _save_tab_layout_explicit(self, tab_index):
        """Save dock layout using grid positions"""
        tab_info = self.tab_data.get(tab_index)
        if not tab_info:
            return {}
        
        layout_info = {
            'positions': {},  # widget_id -> (row, col, width, height)
        }
        
        mainwindow = tab_info['mainwindow']
        
        # Save each dock's state and relative position
        for widget_id, dock in tab_info['docks'].items():
            layout_info['positions'][widget_id] = {
                'floating': dock.isFloating(),
                'visible': dock.isVisible(),
                'geometry': {
                    'x': dock.x(),
                    'y': dock.y(),
                    'width': dock.width(),
                    'height': dock.height()
                }
            }
        
        # Save layout_positions from tab_info if it exists
        if 'layout_positions' in tab_info:
            layout_info['grid_positions'] = tab_info['layout_positions']
        
        return layout_info

    def save_project(self):
        """Save project with improved functionality"""
        if not self.current_project_path:
            path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "Dashboard Project (*.json)")
            if not path:
                return
            self.current_project_path = path
        
        try:
            layout_data = {}
            for index, tab_info in self.tab_data.items():
                tab_name = self.tab_widget.tabText(index)
                state = tab_info['mainwindow'].saveState()
                explicit_layout = self._save_tab_layout_explicit(index)
                layout_data[tab_name] = {
                    'state': base64.b64encode(state.data()).decode('utf-8'),
                    'configs': tab_info['configs'],
                    'explicit_layout': explicit_layout
                }
            
            # Include data logging settings
            # Include data logging settings and dashboard title customization
            project_data = {
                'parameters': self.parameters,
                'layout': layout_data,
                'connection_settings': self.connection_settings,
                'logging_settings': self.logging_settings,
                'configured_widgets': getattr(self, 'configured_widgets', []),
                'dashboard_title_text': self.dashboard_title_text,
                'dashboard_title_alignment': str(self.dashboard_title_alignment.value),
                'version': '1.0',
                'created': datetime.now().isoformat()
            }
            
            with open(self.current_project_path, 'w') as f:
                json.dump(project_data, f, indent=4)
            
            self.mark_as_saved()
            QMessageBox.information(self, "Success", f"Project saved successfully to:\n{self.current_project_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
    
    def save_project_as(self):
        """Save project with new filename"""
        self.current_project_path = None
        self.save_project()

    def _restore_tab_layout_explicit(self, tab_index, explicit_layout):
        """Restore dock layout from saved positions"""
        if not explicit_layout:
            return
        
        tab_info = self.tab_data.get(tab_index)
        if not tab_info:
            return
        
        # Restore grid positions if available
        if 'grid_positions' in explicit_layout:
            tab_info['layout_positions'] = explicit_layout['grid_positions']
            # Trigger retiling based on saved positions
            self._retile_positions(tab_index)
        
        # Restore individual dock states (floating, geometry)
        if 'positions' in explicit_layout:
            from PySide6.QtCore import QTimer
            
            def restore_dock_states():
                for widget_id, pos_info in explicit_layout['positions'].items():
                    if widget_id not in tab_info['docks']:
                        continue
                    
                    dock = tab_info['docks'][widget_id]
                    
                    # Restore floating and geometry
                    if pos_info['floating']:
                        dock.setFloating(True)
                        geom = pos_info['geometry']
                        dock.setGeometry(geom['x'], geom['y'], geom['width'], geom['height'])
                    
                    # Restore visibility
                    dock.setVisible(pos_info.get('visible', True))
            
            # Delay to let Qt finish initial layout
            QTimer.singleShot(200, restore_dock_states)

    def load_project(self):
        """Load project with improved functionality"""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them before loading a new project?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "Dashboard Project (*.json);;JSON Files (*.json)")
        if not path:
            return
        
        try:
            with open(path, 'r') as f:
                project_data = json.load(f)
            
            # Load parameters
            self.parameters = project_data.get('parameters', [])
            
            # Load connection settings
            if 'connection_settings' in project_data:
                self.connection_settings.update(project_data['connection_settings'])
            
            # Load logging settings
            if 'logging_settings' in project_data:
                self.logging_settings = project_data['logging_settings']
                # Reconfigure data logger if settings exist
                if self.logging_settings:
                    selected_params = [p for p in self.parameters if p['id'] in self.logging_settings['selected_params']]
                    self.data_logger.configure(
                        format_type=self.logging_settings['format'],
                        file_path=self.logging_settings['file_path'],
                        parameters=selected_params,
                        buffer_size=self.logging_settings['buffer_size']
                    )
            
            # Load configured widgets
            if 'configured_widgets' in project_data:
                self.configured_widgets = project_data['configured_widgets']
            
            # Load dashboard title customization
            if 'dashboard_title_text' in project_data:
                self.dashboard_title_text = project_data['dashboard_title_text']
            if 'dashboard_title_alignment' in project_data:
                alignment_val = int(project_data['dashboard_title_alignment'])
                self.dashboard_title_alignment = Qt.AlignmentFlag(alignment_val)
            self._update_dashboard_title()
            
            # Clear existing tabs and data
            
            # Clear existing tabs and data
            self.data_history.clear()
            while self.tab_widget.count() > 0:
                self.close_tab(0)
            
            # Load layout data
            # Load layout data
            layout_data = project_data.get('layout', {})
            for tab_name, tab_layout_data in layout_data.items():
                index = self.add_new_tab(name=tab_name)
                for widget_id, config in tab_layout_data.get('configs', {}).items():
                    self.add_widget_to_dashboard(config, index, widget_id)
                
                # First try Qt's built-in state restoration
                state_data = base64.b64decode(tab_layout_data['state'])
                self.tab_data[index]['mainwindow'].restoreState(QByteArray(state_data))
                
                # Then apply explicit layout restoration for better accuracy
                if 'explicit_layout' in tab_layout_data:
                    self._restore_tab_layout_explicit(index, tab_layout_data['explicit_layout'])
            
            self.current_project_path = path
            self.mark_as_saved()
            
            self.restart_simulator()
            self.update_control_states()
            self.update_status_bar()
            
            QMessageBox.information(self, "Success", f"Project loaded successfully from:\n{path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project: {e}")


    def open_standalone_telemetry_viewer(self):
        """Open standalone telemetry viewer from welcome screen"""
        standalone_viewer = StandaloneTelemetryViewer(self)
        standalone_viewer.exec()
    
    def _build_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")

        new_action = QAction("New Dashboard", self); new_action.triggered.connect(lambda: self.show_phase("setup"))
        load_action = QAction("Load Project...", self); load_action.triggered.connect(self.load_project)
        save_action = QAction("Save Project", self); save_action.triggered.connect(self.save_project)
        save_as_action = QAction("Save Project As...", self); save_as_action.triggered.connect(self.save_project_as)
        conn_action = QAction("Connection Settings...", self); conn_action.triggered.connect(self.open_connection_settings)
        exit_action = QAction("Exit", self); exit_action.triggered.connect(self.close)
        file_menu.addAction(new_action); file_menu.addAction(load_action); file_menu.addAction(save_action); file_menu.addAction(save_as_action); file_menu.addSeparator(); file_menu.addAction(conn_action); file_menu.addSeparator(); file_menu.addAction(exit_action)

        manage_params_action = QAction("Manage Parameters...", self); manage_params_action.triggered.connect(self.open_manage_parameters_dialog)
        add_widget_action = QAction("Add Widget...", self); add_widget_action.triggered.connect(self.open_add_widget_dialog)
        remove_widget_action = QAction("Remove Widget...", self); remove_widget_action.triggered.connect(self.remove_selected_display)
        edit_menu.addAction(manage_params_action); edit_menu.addAction(add_widget_action); edit_menu.addAction(remove_widget_action)
        
        # Data logging menu
        logging_menu = menubar.addMenu("Data Logging")
        config_logging_action = QAction("Configure Logging...", self); config_logging_action.triggered.connect(self.open_logging_config)
        start_logging_action = QAction("Start Logging", self); start_logging_action.triggered.connect(self.start_logging)
        stop_logging_action = QAction("Stop Logging", self); stop_logging_action.triggered.connect(self.stop_logging)
        logging_menu.addAction(config_logging_action); logging_menu.addAction(start_logging_action); logging_menu.addAction(stop_logging_action)

        add_tab_action = QAction("Add Tab", self); add_tab_action.triggered.connect(lambda: self.add_new_tab())
        rename_tab_action = QAction("Rename Current Tab", self); rename_tab_action.triggered.connect(self.rename_current_tab)
        raw_tlm_action = QAction("Raw Telemetry Monitor...", self); raw_tlm_action.triggered.connect(self.open_raw_telemetry_monitor)
        view_menu.addAction(add_tab_action); view_menu.addAction(rename_tab_action); view_menu.addSeparator(); view_menu.addAction(raw_tlm_action)

        help_menu = menubar.addMenu("Help")
        documentation_action = QAction("Documentation", self); documentation_action.triggered.connect(self.show_documentation)
        about_action = QAction("About", self); about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(documentation_action)
        help_menu.addAction(about_action)

    def show_documentation(self):
        """Show the documentation in a viewer window"""
        # Check if documentation exists
        doc_path = os.path.join("docs", "index.html")
        
        if not os.path.exists(doc_path):
            QMessageBox.warning(
                self, 
                "Documentation Not Found", 
                f"Documentation file not found at:\n{doc_path}\n\n"
                "Please ensure the Documentation folder exists and contains index.html"
            )
            return
        
        # Create documentation viewer dialog
        doc_dialog = QDialog(self)
        doc_dialog.setWindowTitle("Glance Documentation")
        doc_dialog.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout(doc_dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Remove spacing between widgets
        
        # Try to use QWebEngineView if available
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtCore import QUrl
            
            web_view = QWebEngineView()
            web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Make it expand
            
            # Load the documentation
            abs_path = os.path.abspath(doc_path)
            web_view.setUrl(QUrl.fromLocalFile(abs_path))
            
            layout.addWidget(web_view, 1)  # Add stretch factor of 1 to make it fill space
            
            # Add close button at bottom
            button_container = QWidget()
            button_container.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #2a2a2a;")
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(12, 8, 12, 8)
            
            close_btn = QPushButton("Close")
            close_btn.setMinimumWidth(100)
            close_btn.clicked.connect(doc_dialog.accept)
            
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            button_layout.addStretch()
            
            layout.addWidget(button_container, 0)  # No stretch, fixed height
            
        except ImportError:
            # Fallback: Show message with option to open in browser
            msg_container = QWidget()
            msg_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg_layout = QVBoxLayout(msg_container)
            msg_layout.setContentsMargins(40, 40, 40, 40)
            msg_layout.setSpacing(20)
            
            info_label = QLabel(
                "<h3>Documentation Viewer</h3>"
                "<p>The built-in documentation viewer requires PySide6-WebEngine.</p>"
                "<p>You can:</p>"
                "<ul>"
                "<li>Install it with: <code>pip install PySide6-WebEngine</code></li>"
                "<li>Or open the documentation in your web browser</li>"
                "</ul>"
            )
            info_label.setWordWrap(True)
            msg_layout.addWidget(info_label)
            msg_layout.addStretch()
            
            button_layout = QHBoxLayout()
            browser_btn = QPushButton("Open in Browser")
            browser_btn.clicked.connect(lambda: self.open_documentation_in_browser(doc_path))
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(doc_dialog.accept)
            
            button_layout.addStretch()
            button_layout.addWidget(browser_btn)
            button_layout.addWidget(close_btn)
            button_layout.addStretch()
            
            msg_layout.addLayout(button_layout)
            
            layout.addWidget(msg_container, 1)
        
        doc_dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 8px 16px;
                color: #e8e8e8;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #383838;
                border-color: #4a9eff;
            }
            QLabel {
                color: #e8e8e8;
            }
        """)
        
        doc_dialog.exec()

    def open_documentation_in_browser(self, doc_path):
        """Open documentation in default web browser"""
        import webbrowser
        abs_path = os.path.abspath(doc_path)
        webbrowser.open(f'file://{abs_path}')
        QMessageBox.information(self, "Documentation Opened", "Documentation opened in your default web browser.")

    def open_raw_telemetry_monitor(self):
        """Open the raw telemetry monitor window"""
        if self.raw_tlm_monitor is None or not self.raw_tlm_monitor.isVisible():
            self.raw_tlm_monitor = RawTelemetryMonitor(self)
            self.raw_tlm_monitor.show()
        else:
            self.raw_tlm_monitor.raise_()
            self.raw_tlm_monitor.activateWindow()
    
    def show_about_dialog(self):
        """Display the About dialog with comprehensive team and project information"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("About Glance")
        dialog.setFixedSize(650, 700)
        
        # Modern professional styling with excellent contrast
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #e8e8e8;
            }
            QLabel#sectionHeader {
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 0 4px 0;
            }
            QLabel a {
                color: #4a9eff;
                text-decoration: none;
            }
            QLabel a:hover {
                color: #6bb3ff;
                text-decoration: underline;
            }
            QFrame#separator {
                background-color: #3a3a3a;
                max-height: 1px;
                min-height: 1px;
            }
            QFrame#card {
                background-color: #242424;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 9px 20px;
                color: #e8e8e8;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #383838;
                border-color: #4a9eff;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5a5a5a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scrollable content
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 28, 32, 28)
        content_layout.setSpacing(20)
        
        # Logo and title section
        logo_label = QLabel()
        logo_path = os.path.join("public", "ign_logo_wht.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("IGNITION")
            font = QFont("Arial", 24, QFont.Weight.Bold)
            logo_label.setFont(font)
            logo_label.setStyleSheet("color: #4a9eff;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(logo_label)
        
        app_name = QLabel("Glance")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        app_name.setStyleSheet("color: #ffffff; padding: 8px 0;")
        content_layout.addWidget(app_name)
        
        version_label = QLabel("Version 2.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(QFont("Arial", 10))
        version_label.setStyleSheet("color: #9a9a9a; padding-bottom: 4px;")
        content_layout.addWidget(version_label)
        
        # Description
        desc = QLabel("Professional real-time telemetry visualization and monitoring platform for aerospace applications, embedded systems, and data acquisition.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setFont(QFont("Arial", 10))
        desc.setStyleSheet("color: #b8b8b8; line-height: 1.5; padding: 0 16px;")
        content_layout.addWidget(desc)
        
        content_layout.addSpacing(12)
        
        # Team Ignition section
        team_header = QLabel("About Team Ignition")
        team_header.setObjectName("sectionHeader")
        content_layout.addWidget(team_header)
        
        team_card = QFrame()
        team_card.setObjectName("card")
        team_layout = QVBoxLayout(team_card)
        team_layout.setContentsMargins(12, 12, 12, 12)
        team_layout.setSpacing(8)
        
        team_info = QLabel(
            "Official student rocketry team of <b>Vellore Institute of Technology, Chennai</b>. "
            "We design, build, and launch experimental rockets while developing all subsystems in-house — "
            "from propulsion and avionics to recovery systems and ground support equipment."
        )
        team_info.setWordWrap(True)
        team_info.setFont(QFont("Arial", 10))
        team_info.setStyleSheet("color: #d0d0d0; line-height: 1.5;")
        team_layout.addWidget(team_info)
        
        content_layout.addWidget(team_card)
        content_layout.addSpacing(8)
        
        # Links section
        links_header = QLabel("Resources & Community")
        links_header.setObjectName("sectionHeader")
        content_layout.addWidget(links_header)
        
        links_card = QFrame()
        links_card.setObjectName("card")
        links_layout = QVBoxLayout(links_card)
        links_layout.setContentsMargins(12, 10, 12, 10)
        links_layout.setSpacing(10)
        
        def create_link(icon, text, url):
            row = QHBoxLayout()
            row.setSpacing(12)
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedWidth(24)
            icon_lbl.setFont(QFont("Arial", 14))
            icon_lbl.setStyleSheet("color: #e8e8e8;")
            link_lbl = QLabel(f'<a href="{url}">{text}</a>')
            link_lbl.setOpenExternalLinks(True)
            link_lbl.setFont(QFont("Arial", 10))
            row.addWidget(icon_lbl)
            row.addWidget(link_lbl)
            row.addStretch()
            return row
        
        links_layout.addLayout(create_link("📦", "GitHub Repository", "https://github.com/teamignitionvitc/Glance"))
        links_layout.addLayout(create_link("📖", "Documentation", "https://glance.teamignition.space/"))
        links_layout.addLayout(create_link("🌐", "Team Website", "https://teamignition.space"))
        links_layout.addLayout(create_link("🐛", "Report Issues", "https://github.com/teamignitionvitc/Glance/issues"))
        
        content_layout.addWidget(links_card)
        content_layout.addSpacing(8)
        
        # Contributing section
        contrib_header = QLabel("Contributing")
        contrib_header.setObjectName("sectionHeader")
        content_layout.addWidget(contrib_header)
        
        contrib_card = QFrame()
        contrib_card.setObjectName("card")
        contrib_layout = QVBoxLayout(contrib_card)
        contrib_layout.setContentsMargins(12, 12, 12, 12)
        contrib_layout.setSpacing(8)
        
        contrib_text = QLabel(
            "We welcome contributions from the community! Whether it's bug fixes, new features, "
            "documentation improvements, or testing — your help makes this project better.<br><br>"
            "To contribute: Fork the repository, create a feature branch, commit your changes, "
            "and submit a pull request. Check our GitHub for contribution guidelines."
        )
        contrib_text.setWordWrap(True)
        contrib_text.setFont(QFont("Arial", 10))
        contrib_text.setStyleSheet("color: #d0d0d0; line-height: 1.5;")
        contrib_layout.addWidget(contrib_text)
        
        content_layout.addWidget(contrib_card)
        content_layout.addSpacing(8)
        
        # Social media
        social_header = QLabel("Connect With Us")
        social_header.setObjectName("sectionHeader")
        content_layout.addWidget(social_header)
        
        social_links = QLabel(
            '<a href="https://x.com/ignitiontech23">Twitter/X</a>  •  '
            '<a href="https://www.linkedin.com/in/teamignition/">LinkedIn</a>  •  '
            '<a href="https://www.instagram.com/ignition_vitc">Instagram</a>'
        )
        social_links.setAlignment(Qt.AlignmentFlag.AlignCenter)
        social_links.setOpenExternalLinks(True)
        social_links.setFont(QFont("Arial", 10))
        social_links.setStyleSheet("padding: 6px 0;")
        content_layout.addWidget(social_links)
        
        content_layout.addSpacing(12)
        
        # License section
        license_header = QLabel("License")
        license_header.setObjectName("sectionHeader")
        content_layout.addWidget(license_header)
        
        license_text = QLabel(
            "GNU General Public License v3.0 with additional restrictions<br>"
            "© 2025 Team Ignition Software Department"
        )
        license_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_text.setFont(QFont("Arial", 9))
        license_text.setStyleSheet("color: #888888; line-height: 1.4;")
        content_layout.addWidget(license_text)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Close button at bottom
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #2a2a2a;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(16, 12, 16, 12)
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addWidget(button_container)
        
        dialog.setLayout(layout)
        dialog.exec()

    # Convenience wrappers for Source menu
    def set_source_backend(self):
        # Open connection settings dialog to let user choose backend type
        self.open_connection_settings()

    def set_source_dummy(self):
        self.connection_settings['mode'] = 'dummy'
        self.restart_simulator()
        self.update_status_bar()

    def _build_status_bar(self):
        sb = self.statusBar()
        sb.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565c0, stop:1 #1976d2);
                border-top: 1px solid #2196f3;
                color: #ffffff;
                padding: 6px 20px;
                font-size: 11px;
                font-weight: 600;
            }
            QStatusBar QLabel {
                color: #ffffff;
                padding: 0 12px;
                margin: 0;
                background: transparent;
                border: none;
                font-weight: 600;
            }
            QStatusBar QLabel#SBClock {
                font-family: 'Consolas', 'Courier New', monospace;
                color: #ffffff;
                font-size: 11px;
                letter-spacing: 0.5px;
                font-weight: 700;
            }
            QStatusBar QLabel#SBConnected {
                color: #ffffff;
                font-weight: 700;
            }
            QStatusBar QLabel#SBDisconnected {
                color: #ffcdd2;
                font-weight: 700;
            }
            QStatusBar QLabel#SBStreaming {
                color: #ffffff;
                font-weight: 700;
            }
            QStatusBar QLabel#SBPaused {
                color: #ffe0b2;
                font-weight: 700;
            }
            QStatusBar QLabel#SBValue {
                color: #e3f2fd;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10px;
                font-weight: 600;
            }
            QStatusBar QLabel#Separator {
                color: rgba(255, 255, 255, 0.4);
                padding: 0 4px;
                font-weight: normal;
            }
            QStatusBar QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 600;
                margin: 0 8px;
            }
            QStatusBar QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.5);
            }
            QStatusBar QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
            QStatusBar QPushButton#LoggingActive {
                background: rgba(76, 175, 80, 0.3);
                border-color: rgba(129, 199, 132, 0.6);
            }
            QStatusBar QPushButton#LoggingActive:hover {
                background: rgba(76, 175, 80, 0.4);
            }
            QStatusBar QPushButton#TelemetryBtn {
                background: rgba(255, 152, 0, 0.2);
                border-color: rgba(255, 152, 0, 0.4);
            }
            QStatusBar QPushButton#TelemetryBtn:hover {
                background: rgba(255, 152, 0, 0.3);
            }
        """)
        
        # Clock - always visible
        self.clock_label = QLabel("")
        self.clock_label.setObjectName("SBClock")
        self.clock_label.setToolTip("Current Time")
        
        # Connection status - hidden initially
        self.conn_label = QLabel("")
        self.conn_label.setToolTip("Connection Status")
        self.conn_label.setVisible(False)
        
        # Stream status - hidden initially
        self.status_label = QLabel("")
        self.status_label.setToolTip("Stream Status")
        self.status_label.setVisible(False)
        
        # Logging button - hidden initially
        self.logging_btn = QPushButton("Start Logging")
        self.logging_btn.setToolTip("Click to start/stop data logging")
        self.logging_btn.clicked.connect(self.toggle_logging_from_statusbar)
        self.logging_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logging_btn.setVisible(False)
        
        # Metrics - hidden initially
        self.uptime_label = QLabel("")
        self.uptime_label.setObjectName("SBValue")
        self.uptime_label.setToolTip("Dashboard Uptime")
        self.uptime_label.setVisible(False)
        
        self.packets_label = QLabel("")
        self.packets_label.setObjectName("SBValue")
        self.packets_label.setToolTip("Packets Received")
        self.packets_label.setVisible(False)
        
        self.rate_label = QLabel("")
        self.rate_label.setObjectName("SBValue")
        self.rate_label.setToolTip("Data Rate")
        self.rate_label.setVisible(False)
        
        self.rx_label = QLabel("")
        self.rx_label.setObjectName("SBValue")
        self.rx_label.setToolTip("Total Data Received")
        self.rx_label.setVisible(False)
        
        # Separators - hidden initially
        self.sep1 = QLabel("•")
        self.sep1.setObjectName("Separator")
        self.sep1.setVisible(False)
        
        self.sep2 = QLabel("•")
        self.sep2.setObjectName("Separator")
        self.sep2.setVisible(False)
        
        self.sep3 = QLabel("•")
        self.sep3.setObjectName("Separator")
        self.sep3.setVisible(False)
        
        self.sep4 = QLabel("•")
        self.sep4.setObjectName("Separator")
        self.sep4.setVisible(False)
        
        # NEW: Raw Telemetry Viewer button - always visible
        self.telemetry_viewer_btn = QPushButton("Raw Telemetry")
        self.telemetry_viewer_btn.setObjectName("TelemetryBtn")
        self.telemetry_viewer_btn.setToolTip("Open standalone telemetry monitor")
        self.telemetry_viewer_btn.clicked.connect(self.open_standalone_telemetry_viewer)
        self.telemetry_viewer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout - Left side
        sb.addWidget(self.clock_label)
        sb.addWidget(self.sep1)
        sb.addWidget(self.conn_label)
        sb.addWidget(self.sep2)
        sb.addWidget(self.status_label)
        sb.addWidget(self.logging_btn)
        
        # Right side - use addPermanentWidget for right alignment
        sb.addPermanentWidget(self.telemetry_viewer_btn)  # NEW: Always on right side
        sb.addPermanentWidget(self.uptime_label)
        sb.addPermanentWidget(self.sep3)
        sb.addPermanentWidget(self.packets_label)
        sb.addPermanentWidget(self.sep4)
        sb.addPermanentWidget(self.rate_label)
        sb.addPermanentWidget(self.rx_label)
        
        # Initialize tracking
        self.start_time = time.time()
        self.packet_count = 0
        self.packet_rate = 0.0
        self.packet_timestamps = []
        
        # Update timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_status_bar)
        self.clock_timer.start(1000)

    def toggle_logging_from_statusbar(self):
        """Toggle data logging from status bar button"""
        if self.data_logger.is_logging:
            # Stop logging
            self.stop_logging()
        else:
            # Start logging - check if configured first
            if not self.logging_settings:
                # Open configuration dialog
                reply = QMessageBox.question(
                    self, 
                    "Configure Logging", 
                    "Data logging is not configured. Would you like to configure it now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.open_logging_config()
                    # After configuration, ask if they want to start
                    if self.logging_settings:
                        start_reply = QMessageBox.question(
                            self, 
                            "Start Logging", 
                            "Configuration saved. Start logging now?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if start_reply == QMessageBox.StandardButton.Yes:
                            self.start_logging()
            else:
                # Configuration exists, start logging
                self.start_logging()
        
        # Update button appearance
        self.update_logging_button()

    def update_logging_button(self):
        """Update logging button text and style based on state"""
        if self.data_logger.is_logging:
            self.logging_btn.setText("Stop Logging")
            self.logging_btn.setObjectName("LoggingActive")
            self.logging_btn.setStyleSheet("")  # Reset to apply new object name
            
            # Update header status
            filename = os.path.basename(self.data_logger.log_file_path) if self.data_logger.log_file_path else "unknown"
            self.logging_status_label.setText(f"Logging: ON ({filename})")
            self.logging_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
        else:
            self.logging_btn.setText("Start Logging")
            self.logging_btn.setObjectName("")  # Remove object name
            self.logging_btn.setStyleSheet("")  # Reset styling
            
            # Update header status
            self.logging_status_label.setText("Logging: OFF")
            self.logging_status_label.setStyleSheet("color: #888888; font-weight: bold;")

    def update_status_bar_visibility(self, phase):
        """Show/hide status bar elements based on current phase"""
        is_dashboard = (phase == "dashboard")
        
        # Show all elements only in dashboard phase
        self.conn_label.setVisible(is_dashboard)
        self.status_label.setVisible(is_dashboard)
        self.logging_btn.setVisible(is_dashboard)
        self.uptime_label.setVisible(is_dashboard)
        self.rx_label.setVisible(is_dashboard)
        self.packets_label.setVisible(is_dashboard)
        self.rate_label.setVisible(is_dashboard)
        self.sep1.setVisible(is_dashboard)
        self.sep2.setVisible(is_dashboard)
        self.sep3.setVisible(is_dashboard)
        self.sep4.setVisible(is_dashboard)

    def update_status_bar(self):
        # Update clock
        current_time = datetime.now()
        self.clock_label.setText(current_time.strftime('%H:%M:%S'))
        
        # Update uptime
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Calculate packet rate
        current_time_ts = time.time()
        self.packet_timestamps = [ts for ts in self.packet_timestamps if current_time_ts - ts < 5.0]
        
        if len(self.packet_timestamps) > 1:
            time_span = current_time_ts - self.packet_timestamps[0]
            if time_span > 0:
                self.packet_rate = len(self.packet_timestamps) / time_span
        else:
            self.packet_rate = 0.0
        
        # Update connection and status
        if self.simulator and self.simulator.mode == 'backend':
            cs = self.connection_settings
            mode = cs.get('mode', 'serial')
            
            if mode == 'serial':
                port = cs.get('serial_port', 'N/A')
                self.conn_label.setText(f"Serial {port}")
            elif mode == 'tcp':
                host = cs.get('tcp_host', 'N/A')
                port = cs.get('tcp_port', 'N/A')
                self.conn_label.setText(f"TCP {host}:{port}")
            elif mode == 'udp':
                host = cs.get('udp_host', 'N/A')
                port = cs.get('udp_port', 'N/A')
                self.conn_label.setText(f"UDP {host}:{port}")
            
            self.conn_label.setObjectName("SBConnected")
            self.conn_label.setStyleSheet("")  # Reset to apply new object name
            
            # Update stream status
            if self.simulator._is_paused:
                self.status_label.setText("Paused")
                self.status_label.setObjectName("SBPaused")
            else:
                self.status_label.setText("Streaming")
                self.status_label.setObjectName("SBStreaming")
            self.status_label.setStyleSheet("")  # Reset to apply new object name
            
            # Update RX bytes
            rx = 0
            if hasattr(self.simulator, 'reader') and self.simulator.reader:
                rx = getattr(self.simulator.reader, 'rx_bytes', 0)
            
            if rx < 1024:
                rx_str = f"{rx} B"
            elif rx < 1024 * 1024:
                rx_str = f"{rx/1024:.1f} KB"
            elif rx < 1024 * 1024 * 1024:
                rx_str = f"{rx/(1024*1024):.1f} MB"
            else:
                rx_str = f"{rx/(1024*1024*1024):.2f} GB"
            
            self.rx_label.setText(rx_str)
        else:
            self.conn_label.setText("Dummy Data")
            self.conn_label.setObjectName("SBConnected")
            self.conn_label.setStyleSheet("")
            
            self.status_label.setText("Simulating")
            self.status_label.setObjectName("SBStreaming")
            self.status_label.setStyleSheet("")
            
            self.rx_label.setText("")
        
        # Update packet count
        if self.packet_count < 1000:
            pkt_str = f"{self.packet_count} pkts"
        elif self.packet_count < 1000000:
            pkt_str = f"{self.packet_count/1000:.1f}K pkts"
        else:
            pkt_str = f"{self.packet_count/1000000:.2f}M pkts"
        self.packets_label.setText(pkt_str)
        
        # Update rate
        self.rate_label.setText(f"{self.packet_rate:.1f} Hz")
        

    def _build_welcome_page(self):
        self.welcome_page = QWidget()
        v = QVBoxLayout(self.welcome_page)
        v.setContentsMargins(60, 40, 60, 40)
        v.setSpacing(24)
        
        # Logo section
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        try:
            from PySide6.QtGui import QPixmap
            logo = QLabel("")
            pix = QPixmap("public/Glance_nobg.png")
            if not pix.isNull():
                logo.setPixmap(pix.scaledToWidth(300, Qt.SmoothTransformation))
                logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                logo_layout.addWidget(logo)
        except Exception:
            pass
        
        # Title and subtitle
        subtitle = QLabel("<p style='color: #cccccc; font-size: 14px; margin: 8px 0;'>Professional industrial data visualization and monitoring</p>")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        
        # Feature highlights
        features = QWidget()
        features_layout = QHBoxLayout(features)
        features_layout.setSpacing(30)
        
        feature1 = QLabel("<div style='text-align: center;'><b>Real-time Data</b><br><small>Live streaming from serial, TCP, UDP</small></div>")
        feature2 = QLabel("<div style='text-align: center;'><b>Multiple Widgets</b><br><small>Graphs, gauges, tables, maps</small></div>")
        feature3 = QLabel("<div style='text-align: center;'><b>Professional UI</b><br><small>Industry-ready interface</small></div>")
        
        for f in [feature1, feature2, feature3]:
            f.setStyleSheet("color: #aaaaaa; padding: 8px;")
            features_layout.addWidget(f)
        
        # Action buttons
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(16)
        
        create_btn = QPushButton("Create New Dashboard")
        load_btn = QPushButton("Load Project...")
        
        create_btn.setObjectName("PrimaryCTA")
        load_btn.setObjectName("SecondaryCTA")
        create_btn.setMinimumSize(200, 45)
        load_btn.setMinimumSize(180, 45)
        
        btn_layout.addStretch()
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addStretch()
        
        # Assemble layout
        v.addStretch()
        v.addWidget(logo_container)
        v.addSpacing(16)
        v.addWidget(subtitle)
        v.addSpacing(24)
        v.addWidget(features)
        v.addSpacing(32)
        v.addWidget(btn_container)
        v.addStretch()
        
        self.stack.addWidget(self.welcome_page)
        create_btn.clicked.connect(lambda: self.show_phase("setup"))
        def _load_and_go():
            self.load_project(); self.show_phase("dashboard")
        load_btn.clicked.connect(_load_and_go)

    def _build_setup_page(self):
        self.setup_page = QWidget()
        main_layout = QVBoxLayout(self.setup_page)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("<h2 style='color: #ffffff; margin: 0 0 16px 0;'>Dashboard Configuration</h2>")
        main_layout.addWidget(title)
        
        # Create scrollable content
        scroll = QWidget()
        scroll_layout = QVBoxLayout(scroll)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connection settings group
        conn_group = QGroupBox("Connection Settings")
        conn_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        conn_form = QFormLayout(conn_group)
        conn_form.setSpacing(12)
        
        self.setup_mode_combo = QComboBox()
        self.setup_mode_combo.addItems(["dummy", "serial", "tcp", "udp"])
        self.setup_mode_combo.setCurrentText(self.connection_settings.get('mode','dummy'))
        
        # Serial settings
        self.setup_serial_port = QComboBox()
        self.setup_serial_port.setEditable(True)
        self.setup_serial_port.addItems(self.list_serial_ports())
        self.setup_serial_port.setCurrentText(self.connection_settings.get('serial_port','COM4'))

        # Refresh button for serial ports
        self.setup_refresh_ports_btn = QPushButton("🔄 Refresh")
        self.setup_refresh_ports_btn.setMaximumWidth(80)
        self.setup_refresh_ports_btn.clicked.connect(self.refresh_setup_serial_ports)

        self.setup_baud = QSpinBox()
        self.setup_baud.setRange(300, 10000000)
        self.setup_baud.setValue(int(self.connection_settings.get('baudrate',115200)))
        
        # TCP/UDP settings
        self.setup_tcp_host = QLineEdit(self.connection_settings.get('tcp_host','127.0.0.1'))
        self.setup_tcp_port = QSpinBox()
        self.setup_tcp_port.setRange(1, 65535)
        self.setup_tcp_port.setValue(int(self.connection_settings.get('tcp_port',9000)))
        self.setup_udp_host = QLineEdit(self.connection_settings.get('udp_host','0.0.0.0'))
        self.setup_udp_port = QSpinBox()
        self.setup_udp_port.setRange(1, 65535)
        self.setup_udp_port.setValue(int(self.connection_settings.get('udp_port',9000)))
        
        conn_form.addRow("Connection Mode:", self.setup_mode_combo)
        # Create horizontal layout for port + refresh button
        setup_serial_port_layout = QHBoxLayout()
        setup_serial_port_layout.addWidget(self.setup_serial_port)
        setup_serial_port_layout.addWidget(self.setup_refresh_ports_btn)
        conn_form.addRow("Serial Port:", setup_serial_port_layout)
        conn_form.addRow("Baudrate:", self.setup_baud)
        conn_form.addRow("TCP Host:", self.setup_tcp_host)
        conn_form.addRow("TCP Port:", self.setup_tcp_port)
        conn_form.addRow("UDP Host:", self.setup_udp_host)
        conn_form.addRow("UDP Port:", self.setup_udp_port)
        
        # Data format group
        format_group = QGroupBox("Data Format")
        format_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        format_form = QFormLayout(format_group)
        format_form.setSpacing(12)
        
        self.setup_format = QComboBox()
        self.setup_format.addItems(["json_array", "csv", "raw_bytes", "bits"])
        self.setup_format.setCurrentText(self.connection_settings.get('data_format','json_array'))
        self.setup_channels = QSpinBox()
        self.setup_channels.setRange(1, 1024)
        self.setup_channels.setValue(int(self.connection_settings.get('channel_count',32)))
        self.setup_width = QSpinBox()
        self.setup_width.setRange(1, 8)
        self.setup_width.setValue(int(self.connection_settings.get('sample_width_bytes',2)))
        self.setup_endian = QComboBox()
        self.setup_endian.addItems(["little", "big"])
        self.setup_endian.setCurrentText('little' if self.connection_settings.get('little_endian',True) else 'big')
        self.setup_csv_sep = QLineEdit(self.connection_settings.get('csv_separator',','))
        
        format_form.addRow("Data Format:", self.setup_format)
        format_form.addRow("Channel Count:", self.setup_channels)
        format_form.addRow("Sample Width (bytes):", self.setup_width)
        format_form.addRow("Endianness:", self.setup_endian)
        format_form.addRow("CSV Separator:", self.setup_csv_sep)
        
        scroll_layout.addWidget(conn_group)
        scroll_layout.addWidget(format_group)
        scroll_layout.addStretch()
        
        main_layout.addWidget(scroll)
        
        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        back_btn = QPushButton("Back")
        manage_btn = QPushButton("Manage Parameters...")
        next_btn = QPushButton("Start Dashboard")
        
        back_btn.setObjectName("SecondaryCTA")
        manage_btn.setObjectName("SecondaryCTA")
        next_btn.setObjectName("PrimaryCTA")
        
        back_btn.setMinimumSize(120, 40)
        manage_btn.setMinimumSize(180, 40)
        next_btn.setMinimumSize(160, 40)
        
        btn_row.addWidget(back_btn)
        btn_row.addStretch()
        btn_row.addWidget(manage_btn)
        btn_row.addWidget(next_btn)
        
        main_layout.addLayout(btn_row)
        self.stack.addWidget(self.setup_page)
        # Dynamic mode visibility
        def _apply_setup_mode(mode):
            is_dummy = (mode == 'dummy')
            is_serial = (mode == 'serial')
            is_tcp = (mode == 'tcp')
            is_udp = (mode == 'udp')
            
            # Serial fields
            # Serial fields
            self.setup_serial_port.setVisible(is_serial)
            self.setup_refresh_ports_btn.setVisible(is_serial)  # Add this line
            self.setup_baud.setVisible(is_serial)
            
            # TCP fields
            self.setup_tcp_host.setVisible(is_tcp)
            self.setup_tcp_port.setVisible(is_tcp)
            
            # UDP fields
            self.setup_udp_host.setVisible(is_udp)
            self.setup_udp_port.setVisible(is_udp)
            
            # Update labels visibility
            for i in range(conn_form.rowCount()):
                item = conn_form.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if item and item.widget():
                    label = item.widget()
                    if "Serial Port" in label.text() or "Baudrate" in label.text():
                        label.setVisible(is_serial)
                    elif "TCP Host" in label.text() or "TCP Port" in label.text():
                        label.setVisible(is_tcp)
                    elif "UDP Host" in label.text() or "UDP Port" in label.text():
                        label.setVisible(is_udp)
            
            # Show dummy data indicator
            if is_dummy:
                if not hasattr(self, 'dummy_indicator'):
                    self.dummy_indicator = QLabel("Using Dummy Data - No real connection required")
                    self.dummy_indicator.setStyleSheet("color: #00ff88; font-weight: bold; padding: 8px; background: #1a3a1a; border-radius: 4px;")
                    self.dummy_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    conn_form.addRow(self.dummy_indicator)
                self.dummy_indicator.setVisible(True)
            else:
                if hasattr(self, 'dummy_indicator'):
                    self.dummy_indicator.setVisible(False)
        
        self.setup_mode_combo.currentTextChanged.connect(_apply_setup_mode)
        _apply_setup_mode(self.setup_mode_combo.currentText())
        back_btn.clicked.connect(lambda: self.show_phase("welcome"))
        manage_btn.clicked.connect(self.open_manage_parameters_dialog)
        def _start():
            self.connection_settings = {
                'mode': self.setup_mode_combo.currentText(),
                'serial_port': (self.setup_serial_port.currentText().strip() if hasattr(self.setup_serial_port, 'currentText') else self.setup_serial_port.text().strip()),
                'baudrate': int(self.setup_baud.value()),
                'tcp_host': self.setup_tcp_host.text().strip(),
                'tcp_port': int(self.setup_tcp_port.value()),
                'udp_host': self.setup_udp_host.text().strip(),
                'udp_port': int(self.setup_udp_port.value()),
                'timeout': 1.0,
                'data_format': self.setup_format.currentText(),
                'channel_count': int(self.setup_channels.value()),
                'sample_width_bytes': int(self.setup_width.value()),
                'little_endian': (self.setup_endian.currentText() == 'little'),
                'csv_separator': self.setup_csv_sep.text() or ',',
            }
            self.restart_simulator(); self.show_phase("widgets")
        next_btn.clicked.connect(_start)

    def _build_widgets_page(self):
        self.widgets_page = QWidget()
        main_layout = QVBoxLayout(self.widgets_page)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("<h2 style='color: #ffffff; margin: 0 0 16px 0;'>Configure Dashboard Widgets</h2>")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("<p style='color: #aaaaaa; margin: 0 0 20px 0;'>Add widgets to display your telemetry data. You can always add more widgets later from the dashboard.</p>")
        main_layout.addWidget(desc)
        
        # Widget configuration area
        config_group = QGroupBox("Widget Configuration")
        config_layout = QVBoxLayout(config_group)
        config_layout.setSpacing(12)
        
        # Current widgets list
        self.widgets_list = QListWidget()
        self.widgets_list.setMinimumHeight(200)
        self.widgets_list.setToolTip("Widgets that will be added to your dashboard")
        config_layout.addWidget(QLabel("Widgets to be added:"))
        config_layout.addWidget(self.widgets_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_widget_btn = QPushButton("Add Widget...")
        add_widget_btn.setObjectName("PrimaryCTA")
        remove_widget_btn = QPushButton("Remove Selected")
        remove_widget_btn.setObjectName("SecondaryCTA")
        clear_widgets_btn = QPushButton("Clear All")
        clear_widgets_btn.setObjectName("SecondaryCTA")
        
        add_widget_btn.clicked.connect(self.add_widget_to_config)
        remove_widget_btn.clicked.connect(self.remove_selected_widget)
        clear_widgets_btn.clicked.connect(self.clear_all_widgets)
        
        btn_layout.addWidget(add_widget_btn)
        btn_layout.addWidget(remove_widget_btn)
        btn_layout.addWidget(clear_widgets_btn)
        btn_layout.addStretch()
        
        config_layout.addLayout(btn_layout)
        main_layout.addWidget(config_group)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Back to Setup")
        back_btn.setObjectName("SecondaryCTA")
        skip_btn = QPushButton("Skip (Add widgets later)")
        skip_btn.setObjectName("SecondaryCTA")
        create_btn = QPushButton("Create Dashboard")
        create_btn.setObjectName("PrimaryCTA")
        
        back_btn.clicked.connect(lambda: self.show_phase("setup"))
        skip_btn.clicked.connect(self.create_dashboard_without_widgets)
        create_btn.clicked.connect(self.create_dashboard_with_widgets)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(skip_btn)
        nav_layout.addWidget(create_btn)
        
        main_layout.addLayout(nav_layout)
        self.stack.addWidget(self.widgets_page)
        
        # Initialize empty widgets list
        self.configured_widgets = []
        
        # Add default parameters if none exist
        if not self.parameters:
            self.create_default_parameters()

    def add_widget_to_config(self):
        """Add a widget to the configuration list"""
        if not self.parameters:
            QMessageBox.warning(self, "No Parameters", "Please add some parameters first using 'Manage Parameters'.")
            return
        
        dialog = AddWidgetDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selection = dialog.get_selection()
            if selection:
                # Create a descriptive name for the widget
                param_names = [p['name'] for p in self.parameters if p['id'] in selection['param_ids']]
                widget_name = f"{selection['displayType']}: {', '.join(param_names)}"
                
                # Add to configured widgets list
                widget_config = {
                    'id': str(uuid.uuid4()),
                    'name': widget_name,
                    'config': selection
                }
                self.configured_widgets.append(widget_config)
                self.mark_as_unsaved()
                
                # Update the display list
                self.refresh_widgets_list()

    def remove_selected_widget(self):
        """Remove the selected widget from configuration"""
        current_row = self.widgets_list.currentRow()
        if current_row >= 0 and current_row < len(self.configured_widgets):
            del self.configured_widgets[current_row]
            self.refresh_widgets_list()

    def clear_all_widgets(self):
        """Clear all configured widgets"""
        if self.configured_widgets:
            reply = QMessageBox.question(self, "Clear All Widgets", 
                                       "Are you sure you want to remove all configured widgets?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.configured_widgets.clear()
                self.refresh_widgets_list()

    def refresh_widgets_list(self):
        """Refresh the widgets list display"""
        self.widgets_list.clear()
        for widget in self.configured_widgets:
            item = QListWidgetItem(widget['name'])
            item.setData(Qt.ItemDataRole.UserRole, widget['id'])
            self.widgets_list.addItem(item)

    def create_dashboard_without_widgets(self):
        """Create dashboard without any widgets"""
        self.create_dashboard_with_widgets()

    def create_dashboard_with_widgets(self):
        """Create dashboard and add configured widgets"""
        # Create the main tab
        self.show_phase("dashboard")
        
        # Ensure we have a tab at index 0
        if self.tab_widget.count() == 0:
            self.add_new_tab(name="Main View", is_closable=False)
        
        # Add configured widgets to the main tab
        if self.configured_widgets:
            for widget_config in self.configured_widgets:
                self.add_widget_to_dashboard(widget_config['config'], 0, widget_config['id'])
        
        # Show success message if widgets were added
        if self.configured_widgets:
            QMessageBox.information(self, "Dashboard Created", 
                                  f"Dashboard created successfully with {len(self.configured_widgets)} widget(s)!")

    def create_default_parameters(self):
        """Create default parameters for demonstration"""
        default_params = [
            {
                'id': 'temp_sensor',
                'name': 'Temperature',
                'array_index': 0,
                'sensor_group': 'Temperature',
                'unit': '°C',
                'description': 'Ambient temperature sensor',
                'color': '#FF3131',
                'decimals': 1,
                'threshold': {'low_crit': -10, 'low_warn': 0, 'high_warn': 80, 'high_crit': 100}
            },
            {
                'id': 'humidity',
                'name': 'Humidity',
                'array_index': 1,
                'sensor_group': 'Environmental',
                'unit': '%',
                'description': 'Relative humidity sensor',
                'color': '#00BFFF',
                'decimals': 1,
                'threshold': {'low_crit': 0, 'low_warn': 20, 'high_warn': 80, 'high_crit': 100}
            },
            {
                'id': 'pressure',
                'name': 'Pressure',
                'array_index': 2,
                'sensor_group': 'Environmental',
                'unit': 'hPa',
                'description': 'Atmospheric pressure sensor',
                'color': '#21b35a',
                'decimals': 2,
                'threshold': {'low_crit': 800, 'low_warn': 900, 'high_warn': 1100, 'high_crit': 1200}
            },
            {
                'id': 'accel_x',
                'name': 'Acceleration X',
                'array_index': 3,
                'sensor_group': 'IMU',
                'unit': 'm/s²',
                'description': 'X-axis acceleration from IMU',
                'color': '#FFBF00',
                'decimals': 2,
                'threshold': {'low_crit': -20, 'low_warn': -10, 'high_warn': 10, 'high_crit': 20}
            },
            {
                'id': 'accel_y',
                'name': 'Acceleration Y',
                'array_index': 4,
                'sensor_group': 'IMU',
                'unit': 'm/s²',
                'description': 'Y-axis acceleration from IMU',
                'color': '#F012BE',
                'decimals': 2,
                'threshold': {'low_crit': -20, 'low_warn': -10, 'high_warn': 10, 'high_crit': 20}
            },
            {
                'id': 'accel_z',
                'name': 'Acceleration Z',
                'array_index': 5,
                'sensor_group': 'IMU',
                'unit': 'm/s²',
                'description': 'Z-axis acceleration from IMU',
                'color': '#39CCCC',
                'decimals': 2,
                'threshold': {'low_crit': -20, 'low_warn': -10, 'high_warn': 10, 'high_crit': 20}
            },
            {
                'id': 'gps_lat',
                'name': 'GPS Latitude',
                'array_index': 6,
                'sensor_group': 'GPS',
                'unit': '°',
                'description': 'GPS latitude coordinate',
                'color': '#FF851B',
                'decimals': 6,
                'threshold': {'low_crit': -90, 'low_warn': -80, 'high_warn': 80, 'high_crit': 90}
            },
            {
                'id': 'gps_lon',
                'name': 'GPS Longitude',
                'array_index': 7,
                'sensor_group': 'GPS',
                'unit': '°',
                'description': 'GPS longitude coordinate',
                'color': '#FF851B',
                'decimals': 6,
                'threshold': {'low_crit': -180, 'low_warn': -170, 'high_warn': 170, 'high_crit': 180}
            }
        ]
        
        self.parameters.extend(default_params)

    def open_logging_config(self):
        """Open data logging configuration dialog"""
        dialog = DataLoggingDialog(self.parameters, self.logging_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.logging_settings = dialog.get_settings()
            
            # Get file path (empty means auto-generate in logs folder)
            file_path = self.logging_settings.get('file_path', '') or None  # Fixed: handle None case
            if file_path:
                file_path = file_path.strip()
                if not file_path:  # If empty after strip
                    file_path = None
            
            # Configure the data logger
            selected_params = [p for p in self.parameters if p['id'] in self.logging_settings['selected_params']]
            self.data_logger.configure(
                format_type=self.logging_settings['format'],
                file_path=file_path,
                parameters=selected_params,
                buffer_size=self.logging_settings['buffer_size']
            )
            self.mark_as_unsaved()
            
            # Show where the file will be saved
            log_location = self.data_logger.log_file_path
            QMessageBox.information(self, "Logging Configured", 
                                f"Data logging configured for {len(selected_params)} parameters.\n\n"
                                f"Log file will be saved to:\n{log_location}")

    def start_logging(self):
        """Start data logging"""
        if not self.logging_settings:
            QMessageBox.warning(self, "Not Configured", "Please configure data logging first.")
            return
        
        try:
            self.data_logger.start_logging()
            self.update_logging_button()
            
            # Show success notification
            filename = os.path.basename(self.data_logger.log_file_path)
            QMessageBox.information(self, "Logging Started", 
                                f"Data logging started to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Logging Error", f"Failed to start logging: {str(e)}")

    def stop_logging(self):
        """Stop data logging"""
        if self.data_logger.is_logging:
            self.data_logger.stop_logging()
            self.update_logging_button()
            QMessageBox.information(self, "Logging Stopped", "Data logging has been stopped.")
            
    def update_connection_status(self):
        """Update connection status display"""
        if not self.simulator:
            self.connection_status_label.setText("Not Connected")
            self.connection_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")
            return
        
        mode = self.connection_settings.get('mode', 'dummy')
        
        if mode == 'dummy':
            self.connection_status_label.setText("Connected (Dummy Data)")
            self.connection_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
        else:
            # Check if backend connection is active
            if hasattr(self.simulator, 'reader') and self.simulator.reader:
                if mode == 'serial':
                    if hasattr(self.simulator.reader, 'ser') and self.simulator.reader.ser:
                        self.connection_status_label.setText(f"Connected (Serial: {self.connection_settings.get('serial_port', 'N/A')})")
                        self.connection_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
                    else:
                        self.connection_status_label.setText("Disconnected (Serial)")
                        self.connection_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")
                elif mode == 'tcp':
                    if hasattr(self.simulator.reader, 'sock') and self.simulator.reader.sock:
                        self.connection_status_label.setText(f"Connected (TCP: {self.connection_settings.get('tcp_host', 'N/A')}:{self.connection_settings.get('tcp_port', 'N/A')})")
                        self.connection_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
                    else:
                        self.connection_status_label.setText("Disconnected (TCP)")
                        self.connection_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")
                elif mode == 'udp':
                    if hasattr(self.simulator.reader, 'sock') and self.simulator.reader.sock:
                        self.connection_status_label.setText(f"Connected (UDP: {self.connection_settings.get('udp_host', 'N/A')}:{self.connection_settings.get('udp_port', 'N/A')})")
                        self.connection_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
                    else:
                        self.connection_status_label.setText("Disconnected (UDP)")
                        self.connection_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")
            else:
                self.connection_status_label.setText("Not Connected")
                self.connection_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")

    def _build_dashboard_page(self):
        self.dashboard_page = QWidget(); layout = QVBoxLayout(self.dashboard_page)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.tab_widget)
        self.stack.addWidget(self.dashboard_page)
        # start with a default tab only when entering dashboard the first time

    def show_phase(self, which):
        # Hide dashboard-specific docks outside dashboard phase
        is_dashboard = (which == "dashboard")
        if hasattr(self, 'control_dock') and self.control_dock:
            self.control_dock.setVisible(is_dashboard)
        if hasattr(self, 'header_dock') and self.header_dock:
            self.header_dock.setVisible(is_dashboard)
        
        # Update status bar visibility
        self.update_status_bar_visibility(which)
        
        if which == "welcome":
            self.stack.setCurrentWidget(self.welcome_page)
        elif which == "setup":
            self.stack.setCurrentWidget(self.setup_page)
        elif which == "widgets":
            self.stack.setCurrentWidget(self.widgets_page)
        else:  # dashboard
            self.stack.setCurrentWidget(self.dashboard_page)
            if self.tab_widget.count() == 0:
                self.add_new_tab(name="Main View", is_closable=False)

    def open_connection_settings(self):
        dialog = ConnectionSettingsDialog(self.connection_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.connection_settings = dialog.get_settings()
            self.mark_as_unsaved()
            self.restart_simulator()
            self.update_status_bar()
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QDialog { background-color: #1e1e1e; color: #d4d4d4; }
            QWidget { font-size: 13px; }
            QDockWidget { background-color: #252526; }
            QDockWidget::title { background-color: #2c2c2c; padding: 6px; border-radius: 4px; font-weight: bold; }
            QGroupBox { border: 1px solid #3a3a3a; margin-top: 1em; padding: 0.75em; border-radius: 6px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; background-color: transparent; }
            QPushButton { background-color: #0a84ff; border: none; padding: 9px 14px; border-radius: 6px; color: #fff; }
            QPushButton:hover { background-color: #1a8fff; }
            QPushButton:pressed { background-color: #0969c3; }
            QPushButton#PrimaryCTA { background-color: #1c9c4f; }
            QPushButton#PrimaryCTA:hover { background-color: #21b35a; }
            QPushButton#SecondaryCTA { background-color: #3c3c3c; }
            QPushButton#SecondaryCTA:hover { background-color: #4a4a4a; }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox { background-color: #2b2b2b; border: 1px solid #4a4a4a; border-radius: 6px; padding: 6px; }
            QTableWidget { background-color: #202020; gridline-color: #444444; }
            QHeaderView::section { background-color: #2a2a2a; border: 1px solid #444444; padding: 6px; }
            QListWidget { background-color: #202020; border: 1px solid #333; border-radius: 6px; }
            QTabWidget::pane { border: 1px solid #333; }
            QTabBar::tab { background: #252526; border: 1px solid #333; padding: 8px 14px; border-bottom: none; }
            QTabBar::tab:selected { background: #343434; }
            QStatusBar QLabel#SBClock { color: #9cdcfe; padding-left: 10px; }
            QStatusBar QLabel#SBConn { color: #ce9178; padding-right: 10px; }
            QStatusBar QLabel#SBRx { color: #b5cea8; padding-right: 10px; }
        """)

    def closeEvent(self, event):
        """Handle application close with unsaved changes check"""
        # Check for unsaved changes
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
                if self.has_unsaved_changes:  # Still unsaved after save attempt
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Stop data logging if active
        if self.data_logger.is_logging:
            self.data_logger.stop_logging()
        
        # Stop simulator
        try:
            if self.simulator:
                self.simulator.stop()
                self.simulator._is_paused = True
                try:
                    if hasattr(self.simulator, 'reader') and self.simulator.reader:
                        self.simulator.reader.close()
                except Exception:
                    pass
                self.simulator.wait(1000)
        except Exception:
            pass
        
        super().closeEvent(event)

class ConnectionSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent); self.setWindowTitle("Connection Settings"); self._settings = dict(settings)
        form = QFormLayout(self)
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["dummy","serial","tcp","udp"])
        self.mode_combo.setCurrentText(self._settings.get('mode','dummy'))
        # Serial fields
        self.serial_port_edit = QComboBox(); self.serial_port_edit.setEditable(True)
        try:
            ports = []
            if _serial_list_ports: ports = [p.device for p in _serial_list_ports.comports()]
            if ports: self.serial_port_edit.addItems(ports)
        except Exception: pass
        self.serial_port_edit.setCurrentText(self._settings.get('serial_port','COM4'))

        # Refresh button for serial ports
        self.refresh_ports_btn = QPushButton("🔄 Refresh")
        self.refresh_ports_btn.setMaximumWidth(80)
        self.refresh_ports_btn.clicked.connect(self.refresh_serial_ports)

        self.baud_spin = QSpinBox(); self.baud_spin.setRange(300, 10000000); self.baud_spin.setValue(int(self._settings.get('baudrate',115200)))
        # TCP fields
        self.tcp_host_edit = QLineEdit(self._settings.get('tcp_host','127.0.0.1'))
        self.tcp_port_spin = QSpinBox(); self.tcp_port_spin.setRange(1, 65535); self.tcp_port_spin.setValue(int(self._settings.get('tcp_port',9000)))
        # UDP fields
        self.udp_host_edit = QLineEdit(self._settings.get('udp_host','0.0.0.0'))
        self.udp_port_spin = QSpinBox(); self.udp_port_spin.setRange(1, 65535); self.udp_port_spin.setValue(int(self._settings.get('udp_port',9000)))
        # Format options with dropdowns and Custom...
        self.format_combo = QComboBox(); self.format_combo.addItems(["json_array","csv","raw_bytes","bits","Custom..."])
        self.format_combo.setCurrentText(self._settings.get('data_format','json_array'))
        self.custom_format_edit = QLineEdit(self._settings.get('data_format',''))
        self.custom_format_edit.setPlaceholderText("Enter custom format key")
        self.channels_spin = QSpinBox(); self.channels_spin.setRange(1, 1024); self.channels_spin.setValue(int(self._settings.get('channel_count',32)))
        self.width_spin = QSpinBox(); self.width_spin.setRange(1, 8); self.width_spin.setValue(int(self._settings.get('sample_width_bytes',2)))
        self.endian_combo = QComboBox(); self.endian_combo.addItems(["little","big"])
        self.endian_combo.setCurrentText('little' if self._settings.get('little_endian',True) else 'big')
        self.csv_sep_combo = QComboBox(); self.csv_sep_combo.setEditable(True); self.csv_sep_combo.addItems([",",";","|","\t","Custom..."])
        self.csv_sep_combo.setCurrentText(self._settings.get('csv_separator',','))
        self.csv_sep_edit = QLineEdit(self._settings.get('csv_separator',','))
        # Build layout with placeholders for dynamic visibility
        form.addRow("Mode:", self.mode_combo)
        # Serial - Create horizontal layout for port + refresh button
        serial_port_layout = QHBoxLayout()
        serial_port_layout.addWidget(self.serial_port_edit)
        serial_port_layout.addWidget(self.refresh_ports_btn)
        self._row_serial_port = form.rowCount()
        form.addRow("Serial Port:", serial_port_layout)
        self._row_baud = form.rowCount()
        form.addRow("Baudrate:", self.baud_spin)
        # TCP
        self._row_tcp_host = form.rowCount(); form.addRow("TCP Host:", self.tcp_host_edit)
        self._row_tcp_port = form.rowCount(); form.addRow("TCP Port:", self.tcp_port_spin)
        # UDP
        self._row_udp_host = form.rowCount(); form.addRow("UDP Host:", self.udp_host_edit)
        self._row_udp_port = form.rowCount(); form.addRow("UDP Port:", self.udp_port_spin)
        form.addRow("Format:", self.format_combo)
        form.addRow("Custom Format:", self.custom_format_edit)
        form.addRow("Channels:", self.channels_spin)
        form.addRow("Sample Width (bytes):", self.width_spin)
        form.addRow("Endianness:", self.endian_combo)
        form.addRow("CSV Separator:", self.csv_sep_combo)
        form.addRow("Custom Separator:", self.csv_sep_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        form.addWidget(buttons)
        # Dynamic visibility by mode
        def _apply_mode(mode):
            is_dummy = (mode == 'dummy')
            is_serial = (mode == 'serial')
            is_tcp = (mode == 'tcp')
            is_udp = (mode == 'udp')
            # Serial
            lbl = form.labelForField(self.serial_port_edit)
            if lbl: lbl.setVisible(is_serial)
            self.serial_port_edit.setVisible(is_serial)
            self.refresh_ports_btn.setVisible(is_serial) 
            lbl = form.labelForField(self.baud_spin)
            if lbl: lbl.setVisible(is_serial)
            self.baud_spin.setVisible(is_serial)
            # TCP
            lbl = form.labelForField(self.tcp_host_edit)
            if lbl: lbl.setVisible(is_tcp)
            self.tcp_host_edit.setVisible(is_tcp)
            lbl = form.labelForField(self.tcp_port_spin)
            if lbl: lbl.setVisible(is_tcp)
            self.tcp_port_spin.setVisible(is_tcp)
            # UDP
            lbl = form.labelForField(self.udp_host_edit)
            if lbl: lbl.setVisible(is_udp)
            self.udp_host_edit.setVisible(is_udp)
            lbl = form.labelForField(self.udp_port_spin)
            if lbl: lbl.setVisible(is_udp)
            self.udp_port_spin.setVisible(is_udp)
        def _apply_format(fmt):
            is_custom = (fmt == 'Custom...')
            lbl = form.labelForField(self.custom_format_edit)
            if lbl: lbl.setVisible(is_custom)
            self.custom_format_edit.setVisible(is_custom)
        def _apply_csv_sep(val):
            is_custom = (val == 'Custom...')
            lbl = form.labelForField(self.csv_sep_edit)
            if lbl: lbl.setVisible(is_custom)
            self.csv_sep_edit.setVisible(is_custom)
        self.mode_combo.currentTextChanged.connect(_apply_mode)
        _apply_mode(self.mode_combo.currentText())
        self.format_combo.currentTextChanged.connect(_apply_format)
        _apply_format(self.format_combo.currentText())
        self.csv_sep_combo.currentTextChanged.connect(_apply_csv_sep)
        _apply_csv_sep(self.csv_sep_combo.currentText())

    def refresh_serial_ports(self):
        """Refresh the list of available serial ports"""
        current_text = self.serial_port_edit.currentText()
        self.serial_port_edit.clear()
        
        try:
            ports = []
            if _serial_list_ports:
                ports = [p.device for p in _serial_list_ports.comports()]
            if ports:
                self.serial_port_edit.addItems(ports)
            else:
                # Add common defaults if none found
                if sys.platform.startswith('linux'):
                    ports = ['/dev/ttyUSB0', '/dev/ttyACM0']
                elif sys.platform.startswith('win'):
                    ports = ['COM3','COM4','COM5']
                else:
                    ports = ['/dev/tty.usbserial', '/dev/tty.usbmodem']
                self.serial_port_edit.addItems(ports)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh ports: {e}")
        
        # Try to restore previous selection
        index = self.serial_port_edit.findText(current_text)
        if index >= 0:
            self.serial_port_edit.setCurrentIndex(index)
        else:
            self.serial_port_edit.setCurrentText(current_text)

    def get_settings(self):
        return {
            'mode': self.mode_combo.currentText(),
            'serial_port': (self.serial_port_edit.currentText().strip() if hasattr(self.serial_port_edit,'currentText') else self.serial_port_edit.text().strip()),
            'baudrate': int(self.baud_spin.value()),
            'tcp_host': self.tcp_host_edit.text().strip(),
            'tcp_port': int(self.tcp_port_spin.value()),
            'udp_host': self.udp_host_edit.text().strip(),
            'udp_port': int(self.udp_port_spin.value()),
            'timeout': 1.0,
            'data_format': (self.custom_format_edit.text().strip() if self.format_combo.currentText() == 'Custom...' else self.format_combo.currentText()),
            'channel_count': int(self.channels_spin.value()),
            'sample_width_bytes': int(self.width_spin.value()),
            'little_endian': (self.endian_combo.currentText() == 'little'),
            'csv_separator': (self.csv_sep_edit.text() if self.csv_sep_combo.currentText() == 'Custom...' else self.csv_sep_combo.currentText() or ','),
        }

# --- 4. APPLICATION EXECUTION ---
if __name__ == "__main__":
    from app.ui.main_window import MainWindow as AppMainWindow
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec())