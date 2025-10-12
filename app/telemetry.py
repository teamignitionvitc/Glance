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
# @brief       Main entry point for the Glance Telemetry Dashboard application.
# @details     This module initializes and runs the Glance dashboard, providing real-time telemetry
#              data visualization, signal filtering, data logging, and advanced widget management.
#              It supports multiple data sources (dummy, serial, TCP, UDP), interactive dashboards,
#              and a professional user interface for aerospace and industrial monitoring.
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
# Standard library
import time
from datetime import datetime

# Application-specific modules
from app.dialogs import ConnectionSettingsDialog
from app.simulator import DataSimulator  # Used in StandaloneTelemetryViewer
from backend import DataReader
# PySide6 widgets, core, gui
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QWidget, QLineEdit, QComboBox, QCheckBox, QGroupBox, QFileDialog, QMessageBox, QMainWindow
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer

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
