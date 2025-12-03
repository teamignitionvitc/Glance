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
# File:        dialogs.py
# Author:      MuhammadRamzy
# Created On:  26-09-2025
#
# @brief       Application dialogs for configuration and user interaction.
# @details     Contains dialog classes for connection settings, widget creation, parameter management,
#              and data logging configuration.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      26-09-2025  MuhammadRamzy        First commit with the ui/ux and flow changes
# 001  MOD      27-09-2025  MuhammadRamzy        Stream Fix
# 002  MOD      28-09-2025  MuhammadRamzy        Logging Fixed
# 003  MOD      02-10-2025  MuhammadRamzy        UI Fix, Bottom bar fix, Default Logging location fix
# 004  MOD      09-10-2025  MuhammadRamzy        Formatting
# 005  MOD      11-10-2025  oslowtech            Fixed Dialogs.py logging os and datetime import error
# 006  MOD      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side layout and QStackedWidget
# 007  MOD      04-12-2025  MuhammadRamzy        feat: Professional widget-specific parameter selection
####################################################################################################

####################################################################################################
# Imports

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QComboBox, QLineEdit, QSpinBox,
    QListWidget, QAbstractItemView, QPushButton, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QDoubleSpinBox,
    QMessageBox, QGroupBox, QFileDialog, QListWidgetItem, QToolBar, QGridLayout,
    QWidget, QStackedWidget, QScrollArea
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize
from app.core.commands import UpdateParametersCommand
from app.core.history import CommandHistory

try:
    from serial.tools import list_ports as _serial_list_ports
except ImportError:
    _serial_list_ports = None

class ConnectionSettingsDialog(QDialog):
    """
    @brief Dialog for configuring data connection settings.
    @details Allows user to select connection mode (Dummy, Serial, TCP, UDP) and configure related parameters.
    """
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connection Settings")
        self._settings = dict(settings)
        self.setMinimumSize(500, 450)
        
        main_layout = QVBoxLayout(self)
        
        # --- Connection Mode ---
        mode_group = QGroupBox("Connection Mode")
        mode_layout = QFormLayout(mode_group)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["dummy", "serial", "tcp", "udp"])
        self.mode_combo.setCurrentText(self._settings.get('mode', 'dummy'))
        mode_layout.addRow("Mode:", self.mode_combo)
        main_layout.addWidget(mode_group)
        
        # --- Serial Settings ---
        self.serial_group = QGroupBox("Serial Settings")
        serial_layout = QGridLayout(self.serial_group)
        
        self.serial_port_edit = QComboBox()
        self.serial_port_edit.setEditable(True)
        try:
            ports = []
            if _serial_list_ports: ports = [p.device for p in _serial_list_ports.comports()]
            if ports: self.serial_port_edit.addItems(ports)
        except Exception: pass
        self.serial_port_edit.setCurrentText(self._settings.get('serial_port', 'COM4'))
        
        self.refresh_ports_btn = QPushButton("Refresh")
        self.refresh_ports_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_ports_btn.clicked.connect(self.refresh_serial_ports)
        
        self.baud_spin = QSpinBox()
        self.baud_spin.setRange(300, 10000000)
        self.baud_spin.setValue(int(self._settings.get('baudrate', 115200)))
        
        serial_layout.addWidget(QLabel("Port:"), 0, 0)
        serial_layout.addWidget(self.serial_port_edit, 0, 1)
        serial_layout.addWidget(self.refresh_ports_btn, 0, 2)
        serial_layout.addWidget(QLabel("Baudrate:"), 1, 0)
        serial_layout.addWidget(self.baud_spin, 1, 1)
        main_layout.addWidget(self.serial_group)
        
        # --- Network Settings (TCP/UDP) ---
        self.network_group = QGroupBox("Network Settings")
        net_layout = QGridLayout(self.network_group)
        
        self.tcp_host_edit = QLineEdit(self._settings.get('tcp_host', '127.0.0.1'))
        self.tcp_port_spin = QSpinBox()
        self.tcp_port_spin.setRange(1, 65535)
        self.tcp_port_spin.setValue(int(self._settings.get('tcp_port', 9000)))
        
        self.udp_host_edit = QLineEdit(self._settings.get('udp_host', '0.0.0.0'))
        self.udp_port_spin = QSpinBox()
        self.udp_port_spin.setRange(1, 65535)
        self.udp_port_spin.setValue(int(self._settings.get('udp_port', 9000)))
        
        # Labels will be updated dynamically based on mode, but we add all widgets here
        self.net_host_label = QLabel("Host:")
        self.net_port_label = QLabel("Port:")
        
        net_layout.addWidget(self.net_host_label, 0, 0)
        net_layout.addWidget(self.tcp_host_edit, 0, 1) # Shared slot for host
        net_layout.addWidget(self.udp_host_edit, 0, 1) # Shared slot for host
        net_layout.addWidget(self.net_port_label, 1, 0)
        net_layout.addWidget(self.tcp_port_spin, 1, 1) # Shared slot for port
        net_layout.addWidget(self.udp_port_spin, 1, 1) # Shared slot for port
        
        main_layout.addWidget(self.network_group)
        
        # --- Data Format ---
        format_group = QGroupBox("Data Format")
        fmt_layout = QFormLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["json_array", "csv", "raw_bytes", "binary_struct", "bits", "Custom..."])
        self.format_combo.setCurrentText(self._settings.get('data_format', 'json_array'))
        
        self.custom_format_edit = QLineEdit(self._settings.get('data_format', ''))
        self.custom_format_edit.setPlaceholderText("Enter custom format key")
        
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 1024)
        self.channels_spin.setValue(int(self._settings.get('channel_count', 32)))
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 8)
        self.width_spin.setValue(int(self._settings.get('sample_width_bytes', 2)))
        
        self.endian_combo = QComboBox()
        self.endian_combo.addItems(["little", "big"])
        self.endian_combo.setCurrentText('little' if self._settings.get('little_endian', True) else 'big')
        
        self.csv_sep_combo = QComboBox()
        self.csv_sep_combo.setEditable(True)
        self.csv_sep_combo.addItems([",", ";", "|", "\t", "Custom..."])
        self.csv_sep_combo.setCurrentText(self._settings.get('csv_separator', ','))
        
        self.csv_sep_edit = QLineEdit(self._settings.get('csv_separator', ','))
        
        fmt_layout.addRow("Format:", self.format_combo)
        fmt_layout.addRow("Custom Format:", self.custom_format_edit)
        fmt_layout.addRow("Channels:", self.channels_spin)
        fmt_layout.addRow("Sample Width:", self.width_spin)
        fmt_layout.addRow("Endianness:", self.endian_combo)
        fmt_layout.addRow("CSV Separator:", self.csv_sep_combo)
        fmt_layout.addRow("Custom Separator:", self.csv_sep_edit)
        
        main_layout.addWidget(format_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        # Dynamic visibility
        def _apply_mode(mode):
            is_serial = (mode == 'serial')
            is_tcp = (mode == 'tcp')
            is_udp = (mode == 'udp')
            
            self.serial_group.setVisible(is_serial)
            self.network_group.setVisible(is_tcp or is_udp)
            
            self.tcp_host_edit.setVisible(is_tcp)
            self.tcp_port_spin.setVisible(is_tcp)
            self.udp_host_edit.setVisible(is_udp)
            self.udp_port_spin.setVisible(is_udp)
            
            if is_tcp:
                self.net_host_label.setText("TCP Host:")
                self.net_port_label.setText("TCP Port:")
            elif is_udp:
                self.net_host_label.setText("UDP Host:")
                self.net_port_label.setText("UDP Port:")

        def _apply_format(fmt):
            is_custom = (fmt == 'Custom...')
            lbl = fmt_layout.labelForField(self.custom_format_edit)
            if lbl: lbl.setVisible(is_custom)
            self.custom_format_edit.setVisible(is_custom)
            
        def _apply_csv_sep(val):
            is_custom = (val == 'Custom...')
            lbl = fmt_layout.labelForField(self.csv_sep_edit)
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


class AddWidgetDialog(QDialog):
    """
    @brief Dialog for adding a new widget to the dashboard.
    @details Implements a 2-step workflow:
             1. Select Widget Type (Grid of cards)
             2. Configure Parameters & Options (Widget-specific)
    """
    def __init__(self, parameters, parent=None, edit_mode=False, existing_config=None):
        super().__init__(parent)
        self.parameters = sorted(parameters, key=lambda x: x['name'])
        self.edit_mode = edit_mode
        self.existing_config = existing_config or {}
        self.setWindowTitle("Edit Widget" if edit_mode else "Add Widget")
        self.setMinimumSize(900, 650)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Stacked Widget for 2-step flow
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # Step 1: Widget Type Selection
        self.type_page = QWidget()
        self._build_type_selection_page()
        self.stack.addWidget(self.type_page)
        
        # Step 2: Configuration (Parameters + Options)
        self.config_page = QWidget()
        self._build_configuration_page()
        self.stack.addWidget(self.config_page)
        
        # Initialize
        if self.edit_mode and self.existing_config:
            self._populate_from_config()
            self.stack.setCurrentWidget(self.config_page)
        else:
            self.stack.setCurrentWidget(self.type_page)

    def _build_type_selection_page(self):
        layout = QVBoxLayout(self.type_page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header
        header = QLabel("Select Widget Type")
        header.setStyleSheet("font-size: 24px; font-weight: 600; margin-bottom: 20px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Grid of Widget Types
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(20)
        
        self.widget_types = [
            ("Time Graph", "Plot values over time with history."),
            ("Log Table", "Tabular log of data points."),
            ("Instant Value", "Large display of current value."),
            ("Gauge", "Linear or circular gauge display."),
            ("Histogram", "Distribution of values."),
            ("LED Indicator", "Status indicator with thresholds."),
            ("Map (GPS)", "GPS position on map.")
        ]
        
        self.type_buttons = {}
        
        for i, (name, desc) in enumerate(self.widget_types):
            row = i // 3
            col = i % 3
            
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(240, 140)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Button Layout
            btn_layout = QVBoxLayout(btn)
            btn_layout.setContentsMargins(20, 20, 20, 20)
            btn_layout.setSpacing(8)
            
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-size: 16px; font-weight: 600; color: #fff; background: transparent;")
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("font-size: 13px; color: #8e8e93; background: transparent;")
            desc_lbl.setWordWrap(True)
            desc_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            
            btn_layout.addWidget(name_lbl)
            btn_layout.addWidget(desc_lbl)
            btn_layout.addStretch()
            
            # Styling - Apple-like Card
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(28, 28, 30, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    text-align: left;
                }
                QPushButton:checked {
                    background-color: rgba(10, 132, 255, 0.15);
                    border: 1px solid #0a84ff;
                }
                QPushButton:hover {
                    background-color: rgba(44, 44, 46, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
            """)
            
            btn.clicked.connect(lambda checked, n=name: self._on_type_selected(n))
            self.type_buttons[name] = btn
            grid.addWidget(btn, row, col)
            
        layout.addWidget(grid_widget)
        layout.addStretch()
        
        # Next Button
        # Next Button
        self.next_btn = QPushButton("Next")
        self.next_btn.setIcon(QIcon.fromTheme("go-next-symbolic"))
        self.next_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft) # Icon on right
        self.next_btn.setObjectName("PrimaryCTA")
        self.next_btn.setFixedSize(120, 40)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.go_to_config)
        
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(self.next_btn)
        layout.addLayout(btn_container)

    def _on_type_selected(self, selected_name):
        # Uncheck others
        for name, btn in self.type_buttons.items():
            if name != selected_name:
                btn.setChecked(False)
        
        self.selected_type = selected_name
        self.next_btn.setEnabled(True)

    def _build_configuration_page(self):
        layout = QVBoxLayout(self.config_page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with Back Button
        header_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setIcon(QIcon.fromTheme("go-previous-symbolic"))
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setObjectName("SecondaryCTA") # Use global style
        back_btn.setFixedWidth(80)
        back_btn.clicked.connect(self.go_back)
        
        self.config_title = QLabel("Configure Widget")
        self.config_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.config_title)
        header_layout.addStretch()
        # Dummy widget to balance layout
        dummy = QWidget()
        dummy.setFixedWidth(back_btn.sizeHint().width())
        header_layout.addWidget(dummy)
        
        layout.addLayout(header_layout)
        
        # Options Stack
        self.options_stack = QStackedWidget()
        layout.addWidget(self.options_stack)
        
        # --- Create Option Pages ---
        self.pages = {}
        self._create_option_pages()
        
        # Footer Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        self.create_btn = QPushButton("Create Widget")
        self.create_btn.setObjectName("PrimaryCTA")
        self.create_btn.clicked.connect(self.validate_and_accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

    def _create_param_combo(self):
        """Helper to create a populated parameter combobox"""
        combo = QComboBox()
        for p in self.parameters:
            combo.addItem(f"{p['name']} ({p.get('unit', '')})", p['id'])
        return combo

    def _create_option_pages(self):
        # 1. Graph Page
        graph_page = QWidget()
        graph_layout = QVBoxLayout(graph_page)
        
        # Graph Settings
        settings_group = QGroupBox("Graph Settings")
        settings_form = QFormLayout(settings_group)
        self.graph_time_range = QSpinBox(); self.graph_time_range.setRange(10, 3600); self.graph_time_range.setValue(300); self.graph_time_range.setSuffix(" seconds")
        self.graph_line_width = QDoubleSpinBox(); self.graph_line_width.setRange(0.5, 5.0); self.graph_line_width.setValue(2.0); self.graph_line_width.setSingleStep(0.5)
        self.graph_line_style = QComboBox(); self.graph_line_style.addItems(["Solid", "Dashed", "Dotted"])
        self.graph_y_auto = QComboBox(); self.graph_y_auto.addItems(["Auto Range", "Fixed Range"])
        
        settings_form.addRow("Time Range:", self.graph_time_range)
        settings_form.addRow("Line Width:", self.graph_line_width)
        settings_form.addRow("Line Style:", self.graph_line_style)
        settings_form.addRow("Y-Axis Mode:", self.graph_y_auto)
        graph_layout.addWidget(settings_group)
        
        # Data Series
        series_group = QGroupBox("Data Series")
        series_layout = QVBoxLayout(series_group)
        self.graph_series_list = QListWidget()
        self.graph_series_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        series_layout.addWidget(self.graph_series_list)
        
        add_series_btn = QPushButton("+ Add Data Series")
        add_series_btn.clicked.connect(lambda: self._add_series_row(self.graph_series_list))
        series_layout.addWidget(add_series_btn)
        graph_layout.addWidget(series_group)
        
        self.pages["Time Graph"] = graph_page; self.options_stack.addWidget(graph_page)
        
        # 2. Log Table Page
        log_page = QWidget()
        log_layout = QVBoxLayout(log_page)
        log_series_group = QGroupBox("Columns")
        log_series_layout = QVBoxLayout(log_series_group)
        self.log_series_list = QListWidget()
        self.log_series_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        log_series_layout.addWidget(self.log_series_list)
        add_log_btn = QPushButton("+ Add Column")
        add_log_btn.clicked.connect(lambda: self._add_series_row(self.log_series_list))
        log_series_layout.addWidget(add_log_btn)
        log_layout.addWidget(log_series_group)
        self.pages["Log Table"] = log_page; self.options_stack.addWidget(log_page)
        
        # 3. Instant Value Page
        instant_page = QWidget()
        instant_layout = QVBoxLayout(instant_page)
        
        inst_settings = QGroupBox("Display Settings")
        inst_form = QFormLayout(inst_settings)
        self.priority_combo = QComboBox(); self.priority_combo.addItems(["Normal", "High", "Critical"])
        inst_form.addRow("Priority:", self.priority_combo)
        instant_layout.addWidget(inst_settings)
        
        inst_series_group = QGroupBox("Values to Display")
        inst_series_layout = QVBoxLayout(inst_series_group)
        self.instant_series_list = QListWidget()
        self.instant_series_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        inst_series_layout.addWidget(self.instant_series_list)
        add_inst_btn = QPushButton("+ Add Value")
        add_inst_btn.clicked.connect(lambda: self._add_series_row(self.instant_series_list))
        inst_series_layout.addWidget(add_inst_btn)
        instant_layout.addWidget(inst_series_group)
        
        self.pages["Instant Value"] = instant_page; self.options_stack.addWidget(instant_page)
        
        # 4. Gauge Page
        gauge_page = QWidget()
        gauge_layout = QVBoxLayout(gauge_page)
        
        gauge_settings = QGroupBox("Gauge Settings")
        gauge_form = QFormLayout(gauge_settings)
        
        self.gauge_source = self._create_param_combo()
        gauge_form.addRow("Data Source:", self.gauge_source)
        
        self.gauge_min = QDoubleSpinBox(); self.gauge_min.setRange(-1e5, 1e5); self.gauge_min.setValue(0)
        self.gauge_max = QDoubleSpinBox(); self.gauge_max.setRange(-1e5, 1e5); self.gauge_max.setValue(100)
        gauge_form.addRow("Min Value:", self.gauge_min); gauge_form.addRow("Max Value:", self.gauge_max)
        
        self.gauge_style = QComboBox(); self.gauge_style.addItems(["Linear", "Circular"])
        gauge_form.addRow("Style:", self.gauge_style)
        
        self.gauge_use_zones = QComboBox(); self.gauge_use_zones.addItems(["No Zones", "3 Zones (Safe/Warning/Critical)"])
        gauge_form.addRow("Zones:", self.gauge_use_zones)
        
        # Zone Limits
        self.zone_limits_widget = QWidget()
        zone_layout = QFormLayout(self.zone_limits_widget)
        zone_layout.setContentsMargins(0, 0, 0, 0)
        self.gauge_safe_limit = QDoubleSpinBox(); self.gauge_safe_limit.setRange(-1e5, 1e5); self.gauge_safe_limit.setValue(70)
        self.gauge_warning_limit = QDoubleSpinBox(); self.gauge_warning_limit.setRange(-1e5, 1e5); self.gauge_warning_limit.setValue(90)
        zone_layout.addRow("Safe Limit (Green <):", self.gauge_safe_limit)
        zone_layout.addRow("Warning Limit (Yellow <):", self.gauge_warning_limit)
        gauge_form.addRow(self.zone_limits_widget)
        self.zone_limits_widget.setVisible(False)
        self.gauge_use_zones.currentTextChanged.connect(lambda t: self.zone_limits_widget.setVisible(t != "No Zones"))
        
        gauge_layout.addWidget(gauge_settings)
        gauge_layout.addStretch()
        self.pages["Gauge"] = gauge_page; self.options_stack.addWidget(gauge_page)
        
        # 5. Histogram Page
        hist_page = QWidget(); hist_layout = QVBoxLayout(hist_page)
        hist_group = QGroupBox("Histogram Settings")
        hist_form = QFormLayout(hist_group)
        self.hist_source = self._create_param_combo()
        hist_form.addRow("Data Source:", self.hist_source)
        self.hist_bins = QSpinBox(); self.hist_bins.setRange(5, 100); self.hist_bins.setValue(20)
        hist_form.addRow("Bins:", self.hist_bins)
        hist_layout.addWidget(hist_group)
        hist_layout.addStretch()
        self.pages["Histogram"] = hist_page; self.options_stack.addWidget(hist_page)
        
        # 6. LED Page
        led_page = QWidget(); led_layout = QVBoxLayout(led_page)
        led_group = QGroupBox("Indicators")
        led_group_layout = QVBoxLayout(led_group)
        
        self.led_table = QTableWidget(); self.led_table.setColumnCount(5)
        self.led_table.setHorizontalHeaderLabels(["Parameter", "Threshold", "Condition", "Color", "Actions"])
        self.led_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.led_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.led_table.verticalHeader().setVisible(False)
        led_group_layout.addWidget(self.led_table)
        
        add_led_btn = QPushButton("+ Add Indicator")
        add_led_btn.clicked.connect(self.add_led_threshold_row)
        led_group_layout.addWidget(add_led_btn)
        
        led_layout.addWidget(led_group)
        self.pages["LED Indicator"] = led_page; self.options_stack.addWidget(led_page)
        
        # 7. Map Page
        map_page = QWidget(); map_layout = QVBoxLayout(map_page)
        map_group = QGroupBox("Map Settings")
        map_form = QFormLayout(map_group)
        
        self.map_lat = self._create_param_combo()
        self.map_lon = self._create_param_combo()
        map_form.addRow("Latitude Source:", self.map_lat)
        map_form.addRow("Longitude Source:", self.map_lon)
        
        self.map_zoom = QSpinBox(); self.map_zoom.setRange(1, 18); self.map_zoom.setValue(10)
        map_form.addRow("Initial Zoom:", self.map_zoom)
        
        map_layout.addWidget(map_group)
        map_layout.addStretch()
        self.pages["Map (GPS)"] = map_page; self.options_stack.addWidget(map_page)

    def _add_series_row(self, list_widget, param_id=None):
        """Adds a row with a combobox and remove button to a list widget"""
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 50))
        list_widget.addItem(item)
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        combo = self._create_param_combo()
        if param_id:
            index = combo.findData(param_id)
            if index >= 0: combo.setCurrentIndex(index)
            
        remove_btn = QPushButton()
        remove_btn.setIcon(QIcon.fromTheme("list-remove"))
        remove_btn.setFixedSize(30, 30)
        remove_btn.clicked.connect(lambda: list_widget.takeItem(list_widget.row(item)))
        
        layout.addWidget(combo)
        layout.addWidget(remove_btn)
        
        list_widget.setItemWidget(item, widget)

    def go_to_config(self):
        if not hasattr(self, 'selected_type'):
            return
            
        text = self.selected_type
        self.config_title.setText(f"Configure {text}")
        
        if text in self.pages:
            self.options_stack.setCurrentWidget(self.pages[text])
            
        self.stack.setCurrentWidget(self.config_page)

    def go_back(self):
        self.stack.setCurrentWidget(self.type_page)

    def add_led_threshold_row(self, param_id=None, threshold_data=None):
        from app.ui.color_picker import ColorPickerButton
        row = self.led_table.rowCount(); self.led_table.insertRow(row)
        
        # Parameter Combo
        param_combo = self._create_param_combo()
        if param_id:
            idx = param_combo.findData(param_id)
            if idx >= 0: param_combo.setCurrentIndex(idx)
        self.led_table.setCellWidget(row, 0, param_combo)
        
        # Threshold
        spin = QDoubleSpinBox(); spin.setRange(-1e5, 1e5); spin.setValue(threshold_data.get('value', 50) if threshold_data else 50)
        self.led_table.setCellWidget(row, 1, spin)
        
        # Condition
        combo = QComboBox(); combo.addItems([">=", "<=", ">", "<", "=="])
        if threshold_data: combo.setCurrentText(threshold_data.get('condition', '>='))
        self.led_table.setCellWidget(row, 2, combo)
        
        # Color
        color = ColorPickerButton(threshold_data.get('color', '#00ff00') if threshold_data else '#00ff00')
        self.led_table.setCellWidget(row, 3, color)
        
        # Remove
        rem = QPushButton("Remove"); rem.clicked.connect(lambda: self.led_table.removeRow(row))
        self.led_table.setCellWidget(row, 4, rem)

    def validate_and_accept(self):
        widget_type = self.selected_type
        
        if widget_type in ["Time Graph", "Log Table", "Instant Value"]:
            # Check if at least one series added
            list_widget = {
                "Time Graph": self.graph_series_list,
                "Log Table": self.log_series_list,
                "Instant Value": self.instant_series_list
            }[widget_type]
            if list_widget.count() == 0:
                QMessageBox.warning(self, "Error", "Please add at least one data series.")
                return
                
        elif widget_type == "LED Indicator":
             if self.led_table.rowCount() == 0:
                QMessageBox.warning(self, "Error", "Please add at least one indicator.")
                return
        
        self.accept()

    def get_selection(self):
        widget_type = self.selected_type
        param_ids = []
        options = {}
        
        if widget_type in ["Time Graph", "Log Table", "Instant Value"]:
            list_widget = {
                "Time Graph": self.graph_series_list,
                "Log Table": self.log_series_list,
                "Instant Value": self.instant_series_list
            }[widget_type]
            
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                widget = list_widget.itemWidget(item)
                combo = widget.findChild(QComboBox)
                if combo: param_ids.append(combo.currentData())
                
            if widget_type == "Time Graph":
                options.update({'time_range': self.graph_time_range.value(), 'line_width': self.graph_line_width.value(), 'line_style': self.graph_line_style.currentText(), 'y_axis_mode': self.graph_y_auto.currentText()})
            elif widget_type == "Instant Value":
                options['priority'] = self.priority_combo.currentText()
                
        elif widget_type == "Gauge":
            param_ids.append(self.gauge_source.currentData())
            options.update({
                'min_value': self.gauge_min.value(), 
                'max_value': self.gauge_max.value(), 
                'style': self.gauge_style.currentText(), 
                'use_zones': self.gauge_use_zones.currentText() != "No Zones",
                'safe_limit': self.gauge_safe_limit.value(),
                'warning_limit': self.gauge_warning_limit.value()
            })
            
        elif widget_type == "Histogram":
            param_ids.append(self.hist_source.currentData())
            options['bins'] = self.hist_bins.value()
            
        elif widget_type == "Map (GPS)":
            param_ids = [self.map_lat.currentData(), self.map_lon.currentData()]
            options['zoom'] = self.map_zoom.value()
            
        elif widget_type == "LED Indicator":
            led_configs = {}
            for r in range(self.led_table.rowCount()):
                param_combo = self.led_table.cellWidget(r, 0)
                if not param_combo: continue
                pid = param_combo.currentData()
                if pid not in param_ids: param_ids.append(pid)
                
                if pid not in led_configs: led_configs[pid] = {'thresholds': []}
                led_configs[pid]['thresholds'].append({
                    'value': self.led_table.cellWidget(r, 1).value(),
                    'condition': self.led_table.cellWidget(r, 2).currentText(),
                    'color': self.led_table.cellWidget(r, 3).get_color()
                })
            options['led_configs'] = led_configs
            
        return {
            'param_ids': param_ids,
            'displayType': widget_type,
            'priority': options.get('priority', "Normal"),
            'options': options
        }

    def _populate_from_config(self):
        if not self.existing_config: return
        w_type = self.existing_config.get('displayType')
        if not w_type: return
        
        self._on_type_selected(w_type)
        p_ids = self.existing_config.get('param_ids', [])
        
        if w_type in ["Time Graph", "Log Table", "Instant Value"]:
            list_widget = {
                "Time Graph": self.graph_series_list,
                "Log Table": self.log_series_list,
                "Instant Value": self.instant_series_list
            }[w_type]
            for pid in p_ids:
                self._add_series_row(list_widget, pid)
                
        elif w_type == "Gauge" and p_ids:
            idx = self.gauge_source.findData(p_ids[0])
            if idx >= 0: self.gauge_source.setCurrentIndex(idx)
            
        elif w_type == "Histogram" and p_ids:
            idx = self.hist_source.findData(p_ids[0])
            if idx >= 0: self.hist_source.setCurrentIndex(idx)
            
        elif w_type == "Map (GPS)" and len(p_ids) >= 2:
            idx1 = self.map_lat.findData(p_ids[0])
            if idx1 >= 0: self.map_lat.setCurrentIndex(idx1)
            idx2 = self.map_lon.findData(p_ids[1])
            if idx2 >= 0: self.map_lon.setCurrentIndex(idx2)
            
        elif w_type == "LED Indicator":
            led_configs = self.existing_config.get('options', {}).get('led_configs', {})
            for pid, config in led_configs.items():
                for thresh in config.get('thresholds', []):
                    self.add_led_threshold_row(pid, thresh)


class DataLoggingDialog(QDialog):
    """
    @brief Dialog for configuring data logging.
    @details Allows user to select format (CSV/JSON), file path, buffer size, and parameters to log.
             Features a searchable table for parameter selection.
    """
    def __init__(self, parameters, current_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Data Logging")
        self.parameters = parameters
        self.setMinimumSize(700, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        
        # Title
        title = QLabel("Data Logging Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: 600; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Logging settings
        settings_group = QGroupBox("Logging Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "JSON"])
        settings_layout.addRow("Log Format:", self.format_combo)
        
        # File path
        path_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        if current_settings and current_settings.get('file_path'):
            self.file_path_edit.setText(current_settings['file_path'])
        else:
            self.file_path_edit.setPlaceholderText("Leave empty for auto-generated file in logs/ folder")

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.file_path_edit)
        path_layout.addWidget(browse_btn)
        settings_layout.addRow("Log File Path:", path_layout)
        
        # Buffer size
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(1, 10000)
        self.buffer_spin.setValue(100)
        self.buffer_spin.setToolTip("Number of entries to buffer before writing to file")
        settings_layout.addRow("Buffer Size:", self.buffer_spin)
        
        main_layout.addWidget(settings_group)
        
        # Parameter selection
        param_group = QGroupBox("Parameters to Log")
        param_layout = QVBoxLayout(param_group)
        
        # Search Bar
        search_layout = QHBoxLayout()
        search_icon = QLabel()
        search_icon.setPixmap(QIcon.fromTheme("system-search-symbolic").pixmap(16, 16))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search parameters...")
        self.search_input.textChanged.connect(self.filter_parameters)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        param_layout.addLayout(search_layout)
        
        # Table
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(4)
        self.param_table.setHorizontalHeaderLabels(["", "ID", "Name", "Unit"])
        self.param_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.param_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.param_table.verticalHeader().setVisible(False)
        self.param_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.param_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.param_table.setAlternatingRowColors(True)
        
        self.populate_table()
        param_layout.addWidget(self.param_table)
        
        # Buttons for parameter selection
        param_btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_none_btn = QPushButton("Select None")
        select_all_btn.clicked.connect(self.select_all_params)
        select_none_btn.clicked.connect(self.select_none_params)
        param_btn_layout.addWidget(select_all_btn)
        param_btn_layout.addWidget(select_none_btn)
        param_btn_layout.addStretch()
        
        # Summary Label
        self.summary_label = QLabel("0 parameters selected")
        self.summary_label.setStyleSheet("color: #8e8e93;")
        param_btn_layout.addWidget(self.summary_label)
        
        param_layout.addLayout(param_btn_layout)
        main_layout.addWidget(param_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Configure Logging")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setObjectName("PrimaryCTA")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        main_layout.addWidget(buttons)
        
        # Connect signals
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        self.param_table.itemChanged.connect(self.update_summary)
        
        # Load current settings if provided
        if current_settings:
            self.load_settings(current_settings)
        else:
            self.update_summary() # Initial update
    
    def populate_table(self):
        self.param_table.setRowCount(len(self.parameters))
        for i, param in enumerate(self.parameters):
            # Checkbox item
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_item.setCheckState(Qt.CheckState.Checked) # Default checked
            check_item.setData(Qt.ItemDataRole.UserRole, param['id']) # Store ID
            
            self.param_table.setItem(i, 0, check_item)
            self.param_table.setItem(i, 1, QTableWidgetItem(param['id']))
            self.param_table.setItem(i, 2, QTableWidgetItem(param['name']))
            self.param_table.setItem(i, 3, QTableWidgetItem(param.get('unit', '')))

    def filter_parameters(self, text):
        text = text.lower()
        for i in range(self.param_table.rowCount()):
            match = False
            if text in self.param_table.item(i, 1).text().lower(): match = True # ID
            if text in self.param_table.item(i, 2).text().lower(): match = True # Name
            self.param_table.setRowHidden(i, not match)

    def browse_file(self):
        logs_dir = "logs"
        if not os.path.exists(logs_dir): os.makedirs(logs_dir)
        
        default_name = f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if self.format_combo.currentText().lower() == 'csv':
            default_name += ".csv"
            file_filter = "CSV Files (*.csv);;All Files (*)"
        else:
            default_name += ".json"
            file_filter = "JSON Files (*.json);;All Files (*)"
        
        path, _ = QFileDialog.getSaveFileName(self, "Select Log File Location", os.path.join(logs_dir, default_name), file_filter)
        if path: self.file_path_edit.setText(path)
    
    def select_all_params(self):
        for i in range(self.param_table.rowCount()):
            if not self.param_table.isRowHidden(i):
                self.param_table.item(i, 0).setCheckState(Qt.CheckState.Checked)
    
    def select_none_params(self):
        for i in range(self.param_table.rowCount()):
            if not self.param_table.isRowHidden(i):
                self.param_table.item(i, 0).setCheckState(Qt.CheckState.Unchecked)
    
    def update_summary(self):
        count = 0
        for i in range(self.param_table.rowCount()):
            if self.param_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                count += 1
        self.summary_label.setText(f"{count} parameters selected")

    def load_settings(self, settings):
        if 'format' in settings:
            format_map = {'csv': 'CSV', 'json': 'JSON'}
            self.format_combo.setCurrentText(format_map.get(settings['format'], 'CSV'))
        if 'file_path' in settings:
            self.file_path_edit.setText(settings['file_path'])
        if 'buffer_size' in settings:
            self.buffer_spin.setValue(settings['buffer_size'])
        if 'selected_params' in settings:
            selected = set(settings['selected_params'])
            for i in range(self.param_table.rowCount()):
                pid = self.param_table.item(i, 0).data(Qt.ItemDataRole.UserRole)
                state = Qt.CheckState.Checked if pid in selected else Qt.CheckState.Unchecked
                self.param_table.item(i, 0).setCheckState(state)
        self.update_summary()
    
    def validate_and_accept(self):
        count = 0
        for i in range(self.param_table.rowCount()):
            if self.param_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                count += 1
        
        if count == 0:
            QMessageBox.warning(self, "No Parameters Selected", "Please select at least one parameter to log.")
            return
        self.accept()
    
    def get_settings(self):
        selected_params = []
        for i in range(self.param_table.rowCount()):
            if self.param_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                selected_params.append(self.param_table.item(i, 0).data(Qt.ItemDataRole.UserRole))
        
        return {
            'format': self.format_combo.currentText().lower(),
            'file_path': self.file_path_edit.text().strip() or None,
            'buffer_size': self.buffer_spin.value(),
            'selected_params': selected_params
        }


class ParameterEntryDialog(QDialog):
    """
    @brief Dialog for adding or editing a single telemetry parameter.
    @details Collects parameter ID, name, unit, thresholds, etc.
    """
    def __init__(self, param=None, existing_ids=None, parent=None):
        super().__init__(parent)
        self.existing_ids = existing_ids or []
        self.is_edit_mode = param is not None
        self.setWindowTitle("Edit Parameter" if self.is_edit_mode else "Add New Parameter")
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        
        # --- Basic Information Group ---
        basic_group = QGroupBox("Basic Information")
        basic_layout = QGridLayout(basic_group)
        
        self.id_edit = QLineEdit(param['id'] if param else "")
        if self.is_edit_mode: self.id_edit.setReadOnly(True)
        self.id_edit.setPlaceholderText("Unique ID (e.g., acc_x)")
        
        self.name_edit = QLineEdit(param['name'] if param else "")
        self.name_edit.setPlaceholderText("Display Name (e.g., Acceleration X)")
        
        self.desc_edit = QLineEdit(param.get('description', '') if param else "")
        self.desc_edit.setPlaceholderText("Optional description")
        
        basic_layout.addWidget(QLabel("ID:"), 0, 0)
        basic_layout.addWidget(self.id_edit, 0, 1)
        basic_layout.addWidget(QLabel("Name:"), 1, 0)
        basic_layout.addWidget(self.name_edit, 1, 1)
        basic_layout.addWidget(QLabel("Description:"), 2, 0)
        basic_layout.addWidget(self.desc_edit, 2, 1)
        
        main_layout.addWidget(basic_group)
        
        # --- Data Configuration Group ---
        data_group = QGroupBox("Data Configuration")
        data_layout = QGridLayout(data_group)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["float32", "float64", "int8", "uint8", "int16", "uint16", "int32", "uint32", "Bitfield"])
        self.type_combo.setCurrentText(param.get('type', 'float32') if param else 'float32')
        
        self.bit_len_spin = QSpinBox()
        self.bit_len_spin.setRange(1, 64)
        self.bit_len_spin.setValue(param.get('bit_length', 32) if param else 32)
        
        self.index_spin = QSpinBox()
        self.index_spin.setRange(0, 255)
        self.index_spin.setValue(param.get('array_index', 0) if param else 0)
        
        self.unit_edit = QLineEdit(param['unit'] if param else "")
        self.unit_edit.setPlaceholderText("e.g., m/s^2")
        
        self.group_edit = QLineEdit(param.get('sensor_group', '') if param else "")
        self.group_edit.setPlaceholderText("e.g., IMU")
        
        data_layout.addWidget(QLabel("Data Type:"), 0, 0)
        data_layout.addWidget(self.type_combo, 0, 1)
        data_layout.addWidget(QLabel("Bit Length:"), 0, 2)
        data_layout.addWidget(self.bit_len_spin, 0, 3)
        
        data_layout.addWidget(QLabel("Array Index:"), 1, 0)
        data_layout.addWidget(self.index_spin, 1, 1)
        data_layout.addWidget(QLabel("Unit:"), 1, 2)
        data_layout.addWidget(self.unit_edit, 1, 3)
        
        data_layout.addWidget(QLabel("Sensor Group:"), 2, 0)
        data_layout.addWidget(self.group_edit, 2, 1, 1, 3) # Span 3 columns
        
        main_layout.addWidget(data_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        self.type_combo.currentTextChanged.connect(self._update_bit_len_visibility)
        self._update_bit_len_visibility(self.type_combo.currentText())

    def _update_bit_len_visibility(self, text):
        # Bit length is primarily relevant for Bitfield or custom integer packing
        # For standard types, we can auto-set it but let user override if needed for packed structs
        if "8" in text: self.bit_len_spin.setValue(8)
        elif "16" in text: self.bit_len_spin.setValue(16)
        elif "32" in text: self.bit_len_spin.setValue(32)
        elif "64" in text: self.bit_len_spin.setValue(64)

    def validate_and_accept(self):
        new_id = self.id_edit.text().strip()
        if ' ' in new_id: QMessageBox.warning(self, "Validation Error", "ID cannot contain spaces."); return
        if not new_id or not self.name_edit.text().strip(): QMessageBox.warning(self, "Validation Error", "ID and Name are required."); return
        if not self.is_edit_mode and new_id in self.existing_ids: QMessageBox.warning(self, "Validation Error", f"ID '{new_id}' already exists."); return
        self.accept()

    def get_data(self):
        return {
            'id': self.id_edit.text().strip(), 
            'name': self.name_edit.text().strip(),
            'array_index': self.index_spin.value(),
            'type': self.type_combo.currentText(),
            'bit_length': self.bit_len_spin.value(),
            'sensor_group': self.group_edit.text().strip(), 
            'unit': self.unit_edit.text().strip(),
            'description': self.desc_edit.text().strip()
        }


class ManageParametersDialog(QDialog):
    """
    @brief Dialog for managing the list of telemetry parameters.
    @details Provides a table view of parameters with Add, Edit, and Remove capabilities.
    """
    def __init__(self, parameters, main_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Telemetry Parameters")
        self.parameters = parameters
        self.main_window = main_window
        self.history = CommandHistory()  # Dialog-specific history (isolated from dashboard)
        self.setMinimumSize(900, 500)
        
        layout = QVBoxLayout(self)
        
        # Toolbar for actions
        toolbar = QHBoxLayout()
        
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setIcon(QIcon.fromTheme("edit-undo-symbolic"))
        self.undo_btn.clicked.connect(self.undo)
        
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.setIcon(QIcon.fromTheme("edit-redo-symbolic"))
        self.redo_btn.clicked.connect(self.redo)
        
        toolbar.addWidget(self.undo_btn)
        toolbar.addWidget(self.redo_btn)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Idx', 'Type', 'Bits', 'Group', 'Unit'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.refresh_table()
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Parameter")
        add_btn.setIcon(QIcon.fromTheme("list-add-symbolic"))
        edit_btn = QPushButton("Edit Parameter")
        edit_btn.setIcon(QIcon.fromTheme("document-edit-symbolic"))
        remove_btn = QPushButton("Remove Parameter")
        remove_btn.setIcon(QIcon.fromTheme("list-remove-symbolic"))
        
        up_btn = QPushButton("Move Up")
        up_btn.setIcon(QIcon.fromTheme("go-up-symbolic"))
        down_btn = QPushButton("Move Down")
        down_btn.setIcon(QIcon.fromTheme("go-down-symbolic"))
        
        add_btn.clicked.connect(self.add_parameter)
        edit_btn.clicked.connect(self.edit_parameter)
        remove_btn.clicked.connect(self.remove_parameter)
        up_btn.clicked.connect(self.move_up)
        down_btn.clicked.connect(self.move_down)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.clicked.connect(self.accept)
        
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        layout.addWidget(buttons)
        
        self.update_undo_redo_buttons()

    def refresh_table(self):
        self.table.setRowCount(0)
        for p in self.parameters:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p['id']))
            self.table.setItem(row, 1, QTableWidgetItem(p['name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get('array_index', 'N/A'))))
            self.table.setItem(row, 3, QTableWidgetItem(p.get('type', 'float32')))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.get('bit_length', 32))))
            self.table.setItem(row, 5, QTableWidgetItem(p.get('sensor_group', '')))
            self.table.setItem(row, 6, QTableWidgetItem(p['unit']))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def update_undo_redo_buttons(self):
        self.undo_btn.setEnabled(self.history.can_undo())
        self.redo_btn.setEnabled(self.history.can_redo())

    def undo(self):
        self.history.undo()
        self.parameters = self.main_window.parameters # Sync local reference
        self.refresh_table()
        self.update_undo_redo_buttons()

    def redo(self):
        self.history.redo()
        self.parameters = self.main_window.parameters # Sync local reference
        self.refresh_table()
        self.update_undo_redo_buttons()

    def _push_update(self, new_params):
        command = UpdateParametersCommand(self.main_window, self.parameters, new_params)
        self.history.push(command)
        self.parameters = self.main_window.parameters # Sync
        self.refresh_table()
        self.update_undo_redo_buttons()

    def add_parameter(self):
        dialog = ParameterEntryDialog(existing_ids=[p['id'] for p in self.parameters], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_params = list(self.parameters)
            new_params.append(dialog.get_data())
            self._push_update(new_params)

    def edit_parameter(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        param_id = self.table.item(selected_rows[0].row(), 0).text()
        param_to_edit = next((p for p in self.parameters if p['id'] == param_id), None)
        if param_to_edit:
            dialog = ParameterEntryDialog(param=param_to_edit, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_data()
                new_params = list(self.parameters)
                for i, p in enumerate(new_params):
                    if p['id'] == param_id:
                        new_params[i] = updated_data
                        break
                self._push_update(new_params)

    def remove_parameter(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        param_id = self.table.item(selected_rows[0].row(), 0).text()
        new_params = [p for p in self.parameters if p['id'] != param_id]
        self._push_update(new_params)
    
    def move_up(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        row = selected_rows[0].row()
        if row > 0:
            new_params = list(self.parameters)
            new_params[row], new_params[row-1] = new_params[row-1], new_params[row]
            self._push_update(new_params)
            self.table.selectRow(row-1)

    def move_down(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        row = selected_rows[0].row()
        if row < len(self.parameters) - 1:
            new_params = list(self.parameters)
            new_params[row], new_params[row+1] = new_params[row+1], new_params[row]
            self._push_update(new_params)
            self.table.selectRow(row+1)
