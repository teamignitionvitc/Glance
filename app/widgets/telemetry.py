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
# File:        telemetry.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Telemetry monitoring widgets.
# @details     Provides widgets for viewing raw telemetry streams in various formats (decimal, hex, ASCII).
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

import time
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QFileDialog, QMessageBox, QWidget, QComboBox, QLineEdit, QCheckBox, 
    QGroupBox, QMainWindow
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer, Qt

from app.core.simulator import DataSimulator
from app.dialogs import ConnectionSettingsDialog

####################################################################################################

class RawTelemetryMonitor(QDialog):
    """
    @brief Serial monitor-style window for viewing raw incoming data packets.
    @details Displays a scrolling log of received packets with basic statistics (count, rate, bytes).
    """
    
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
        """
        @brief Append a new packet to the display.
        @param packet_data The data packet to display (list or raw value).
        """
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
        """
        @brief Toggle pause state.
        @details Pauses or resumes the display updates.
        """
        self.is_paused = self.pause_btn.isChecked()
        if self.is_paused:
            self.pause_btn.setText("Resume")
            self.text_display.append("<span style='color: #ffbf00;'>[PAUSED]</span>")
        else:
            self.pause_btn.setText("Pause")
            self.text_display.append("<span style='color: #00ff88;'>[RESUMED]</span>")
    
    def clear_display(self):
        """
        @brief Clear the display.
        @details Resets the text area and statistics.
        """
        self.text_display.clear()
        self.packet_count = 0
        self.byte_count = 0
        self.packet_timestamps.clear()
        self.packet_count_label.setText("Packets: 0")
        self.byte_count_label.setText("Bytes: 0")
        self.rate_label.setText("Rate: 0.0/s")

    def save_to_file(self):
        """
        @brief Save the current display to a file.
        @details Opens a file dialog to save the log content to a text file.
        """
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
    """
    @brief Advanced standalone telemetry viewer - feature-rich serial monitor.
    @details Provides advanced controls for connection, display formatting (hex, ascii, etc.), and data sending.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Raw Telemetry Monitor")
        self.setMinimumSize(1200, 800)
        
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
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar (Controls)
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar, 1)
        
        # Main Content Area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top Toolbar (Connection & Actions)
        toolbar = self._build_top_toolbar()
        content_layout.addWidget(toolbar)
        
        # Text Display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Consolas", 10))
        self.text_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #0c0c0c;
                border: none;
                color: #00ff88;
                padding: 12px;
                selection-background-color: #0a84ff;
            }
        """)
        content_layout.addWidget(self.text_display)
        
        # Send Panel
        send_panel = self._build_send_panel()
        content_layout.addWidget(send_panel)
        
        # Status Bar
        status_bar = self._build_status_bar()
        content_layout.addWidget(status_bar)
        
        main_layout.addWidget(content_area, 4)
        
        # Apply global styling
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                color: #ffffff;
                background-color: #252525;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e0e0e0;
            }
            QPushButton:hover { background-color: #333333; border-color: #66b3ff; }
            QPushButton:checked { background-color: #0a84ff; border-color: #0a84ff; }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #2b2b2b;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px;
                color: #e0e0e0;
            }
            QCheckBox { spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 1px solid #555; background: #2b2b2b; }
            QCheckBox::indicator:checked { background: #0a84ff; border-color: #0a84ff; }
        """)
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(1000)

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setStyleSheet("background-color: #222222; border-right: 1px solid #333;")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("CONTROLS")
        title.setStyleSheet("color: #888; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(title)
        
        # Display Mode
        mode_group = QGroupBox("Display Format")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_decimal = QPushButton("Decimal")
        self.mode_decimal.setCheckable(True); self.mode_decimal.setChecked(True)
        self.mode_hex = QPushButton("Hexadecimal")
        self.mode_hex.setCheckable(True)
        self.mode_ascii = QPushButton("ASCII")
        self.mode_ascii.setCheckable(True)
        self.mode_binary = QPushButton("Binary")
        self.mode_binary.setCheckable(True)
        self.mode_mixed = QPushButton("Mixed")
        self.mode_mixed.setCheckable(True)
        
        for btn in [self.mode_decimal, self.mode_hex, self.mode_ascii, self.mode_binary, self.mode_mixed]:
            mode_layout.addWidget(btn)
            btn.clicked.connect(lambda c, b=btn: self.set_display_mode(b.text().lower().split()[0]))
            
        layout.addWidget(mode_group)
        
        # Options
        opt_group = QGroupBox("View Options")
        opt_layout = QVBoxLayout(opt_group)
        
        self.show_timestamp = QCheckBox("Show Timestamps")
        self.show_timestamp.setChecked(True)
        self.show_packet_num = QCheckBox("Show Packet #")
        self.show_packet_num.setChecked(True)
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)
        self.autoscroll_check.toggled.connect(lambda c: setattr(self, 'autoscroll_enabled', c))
        self.highlight_errors = QCheckBox("Highlight Errors")
        
        opt_layout.addWidget(self.show_timestamp)
        opt_layout.addWidget(self.show_packet_num)
        opt_layout.addWidget(self.autoscroll_check)
        opt_layout.addWidget(self.highlight_errors)
        layout.addWidget(opt_group)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Highlight text...")
        filter_layout.addWidget(QLabel("Search / Highlight:"))
        filter_layout.addWidget(self.search_input)
        layout.addWidget(filter_group)
        
        layout.addStretch()
        
        # Quick Actions
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout(action_group)
        
        copy_btn = QPushButton("Copy All")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        save_btn = QPushButton("Save Log")
        save_btn.clicked.connect(self.save_to_file)
        clear_btn = QPushButton("Clear Display")
        clear_btn.clicked.connect(self.clear_display)
        
        action_layout.addWidget(copy_btn)
        action_layout.addWidget(save_btn)
        action_layout.addWidget(clear_btn)
        layout.addWidget(action_group)
        
        return sidebar

    def _build_top_toolbar(self):
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #252525; border-bottom: 1px solid #333;")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(16, 8, 16, 8)
        
        # Connection Status
        self.conn_status_label = QLabel("● Disconnected")
        self.conn_status_label.setStyleSheet("color: #ff3131; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.conn_status_label)
        
        layout.addStretch()
        
        # Controls
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_connection_settings)
        layout.addWidget(self.settings_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("background-color: #1c9c4f; border-color: #1c9c4f;")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn)

        return toolbar

    def _build_send_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #222; border-top: 1px solid #333;")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        
        layout.addWidget(QLabel("Send:"))
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("Data to transmit...")
        self.send_input.returnPressed.connect(self.send_data)
        layout.addWidget(self.send_input)
        
        self.line_ending_combo = QComboBox()
        self.line_ending_combo.addItems(["None", "LF", "CR", "CRLF"])
        self.line_ending_combo.setCurrentText("LF")
        layout.addWidget(self.line_ending_combo)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_data)
        layout.addWidget(send_btn)
        
        return panel

    def _build_status_bar(self):
        bar = QWidget()
        bar.setStyleSheet("background-color: #1a1a1a; color: #888; font-size: 11px;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 4, 12, 4)
        
        self.packets_stat = QLabel("Pkts: 0")
        self.bytes_stat = QLabel("Bytes: 0")
        self.rate_stat = QLabel("Rate: 0.0/s")
        self.uptime_stat = QLabel("Time: 00:00")
        
        layout.addWidget(self.packets_stat)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.bytes_stat)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.rate_stat)
        layout.addStretch()
        layout.addWidget(self.uptime_stat)
        
        return bar

    def set_display_mode(self, mode):
        self.display_mode = mode
        self.mode_decimal.setChecked(mode == 'decimal')
        self.mode_hex.setChecked(mode == 'hex')
        self.mode_ascii.setChecked(mode == 'ascii')
        self.mode_binary.setChecked(mode == 'binary')
        self.mode_mixed.setChecked(mode == 'mixed')

    def open_connection_settings(self):
        dialog = ConnectionSettingsDialog(self.connection_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.connection_settings = dialog.get_settings()

    def toggle_connection(self):
        if self.simulator and self.simulator.isRunning():
            self.disconnect_source()
        else:
            self.connect_source()

    def connect_source(self):
        try:
            self.simulator = DataSimulator(
                num_channels=int(self.connection_settings.get('channel_count', 32)),
                connection_settings=self.connection_settings
            )
            self.simulator.mode = self.connection_settings['mode']
            self.simulator.newData.connect(self.on_data_received)
            self.simulator.start()
            self.start_time = time.time()
            
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("background-color: #ff3b30; border-color: #ff3b30;")
            self.conn_status_label.setText(f"● Connected ({self.connection_settings['mode'].upper()})")
            self.conn_status_label.setStyleSheet("color: #21b35a; font-weight: bold; font-size: 14px;")
            self.settings_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def disconnect_source(self):
        if self.simulator:
            self.simulator.stop()
            self.simulator = None
        self.connect_btn.setText("Connect")
        self.connect_btn.setStyleSheet("background-color: #1c9c4f; border-color: #1c9c4f;")
        self.conn_status_label.setText("● Disconnected")
        self.conn_status_label.setStyleSheet("color: #ff3131; font-weight: bold; font-size: 14px;")
        self.settings_btn.setEnabled(True)

    def toggle_pause(self):
        self.is_paused = self.pause_btn.isChecked()
        self.pause_btn.setText("Resume" if self.is_paused else "Pause")
        self.text_display.append(f"<span style='color: #ffbf00;'>[{'PAUSED' if self.is_paused else 'RESUMED'}]</span>")

    def clear_display(self):
        self.text_display.clear()
        self.packet_count = 0
        self.byte_count = 0

    def append_packet(self, packet_data):
        self.on_data_received(packet_data)

    def on_data_received(self, packet_data):
        if self.is_paused: return
        
        self.packet_count += 1
        
        # Formatting
        if self.display_mode == 'hex':
            data_str = " ".join([f"{int(x):02X}" for x in packet_data]) if isinstance(packet_data, list) else f"{packet_data}"
        elif self.display_mode == 'ascii':
            data_str = "".join([chr(int(x)) if 32 <= int(x) <= 126 else "." for x in packet_data]) if isinstance(packet_data, list) else str(packet_data)
        elif self.display_mode == 'binary':
            data_str = " ".join([f"{int(x):08b}" for x in packet_data]) if isinstance(packet_data, list) else str(packet_data)
        elif self.display_mode == 'mixed':
             data_str = f"{packet_data}" # Simplified for brevity
        else: # decimal
            data_str = str(packet_data)
            
        # Build line
        ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        line = ""
        if self.show_timestamp.isChecked(): line += f"<span style='color:#666;'>{ts}</span> "
        if self.show_packet_num.isChecked(): line += f"<span style='color:#00bfff;'>[{self.packet_count}]</span> "
        line += f"<span style='color:#00ff88;'>{data_str}</span>"
        
        self.text_display.append(line)
        
        if self.autoscroll_enabled:
            sb = self.text_display.verticalScrollBar()
            sb.setValue(sb.maximum())
            
        # Update byte count approximation
        self.byte_count += len(str(packet_data))

    def update_statistics(self):
        self.packets_stat.setText(f"Pkts: {self.packet_count}")
        self.bytes_stat.setText(f"Bytes: {self.byte_count}")
        
        # Rate calc
        current_time = time.time()
        self.packet_timestamps.append(current_time)
        self.packet_timestamps = [t for t in self.packet_timestamps if current_time - t < 1.0]
        self.rate_stat.setText(f"Rate: {len(self.packet_timestamps)}/s")
        
        elapsed = int(current_time - self.start_time)
        self.uptime_stat.setText(f"Time: {elapsed//60:02d}:{elapsed%60:02d}")

    def copy_to_clipboard(self):
        self.text_display.selectAll()
        self.text_display.copy()
        self.text_display.moveCursor(self.text_display.textCursor().End)

    def save_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Log", f"log_{int(time.time())}.txt")
        if path:
            with open(path, 'w') as f: f.write(self.text_display.toPlainText())

    def send_data(self):
        if not self.simulator: return
        text = self.send_input.text()
        end = self.line_ending_combo.currentText()
        if end == "LF": text += "\n"
        elif end == "CR": text += "\r"
        elif end == "CRLF": text += "\r\n"
        self.text_display.append(f"<span style='color:#ffbf00;'>[SENT] {text.strip()}</span>")
        self.send_input.clear()

    def closeEvent(self, event):
        self.disconnect_source()
        super().closeEvent(event)
