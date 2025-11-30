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
    QWidget, QStackedWidget
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
    @details Allows user to select parameters, widget type, and configure specific options.
             Uses QStackedWidget to manage option panels safely.
    """
    def __init__(self, parameters, parent=None, edit_mode=False, existing_config=None):
        super().__init__(parent)
        self.parameters = parameters
        self.edit_mode = edit_mode
        self.existing_config = existing_config or {}
        self.setWindowTitle("Edit Widget" if edit_mode else "Add Widget")
        self.setMinimumSize(900, 600)
        
        # Main layout - Side by Side
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Left Panel: Parameters ---
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #252525; border-right: 1px solid #333;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        
        left_layout.addWidget(QLabel("<b>1. Select Parameters</b>"))
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Group:"))
        self.sensor_group_combo = QComboBox()
        groups = sorted(list(set([p.get('sensor_group', 'Default') for p in parameters])))
        self.sensor_group_combo.addItem("All")
        self.sensor_group_combo.addItems(groups)
        filter_layout.addWidget(self.sensor_group_combo)
        left_layout.addLayout(filter_layout)
        
        # Parameter List
        self.param_list = QListWidget()
        self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.param_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.param_list)
        
        main_layout.addWidget(left_panel, stretch=1)
        
        # --- Right Panel: Configuration ---
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #1e1e1e;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(20)
        
        right_layout.addWidget(QLabel("<b>2. Configure Widget</b>"))
        
        # Widget Type
        type_layout = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Time Graph", 
            "Log Table", 
            "Instant Value", 
            "Gauge", 
            "Histogram", 
            "LED Indicator", 
            "Map (GPS)"
        ])
        type_layout.addRow("Widget Type:", self.type_combo)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Normal", "High", "Critical"])
        type_layout.addRow("Priority:", self.priority_combo)
        
        right_layout.addLayout(type_layout)
        
        # Options Group with StackedWidget
        self.options_group = QGroupBox("Widget Options")
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_stack = QStackedWidget()
        self.options_layout.addWidget(self.options_stack)
        right_layout.addWidget(self.options_group)
        
        # --- Create Pages for Stack ---
        self.pages = {}
        
        # 1. Graph Page
        graph_page = QWidget()
        graph_layout = QFormLayout(graph_page)
        
        self.graph_time_range = QSpinBox()
        self.graph_time_range.setRange(10, 3600)
        self.graph_time_range.setValue(300)
        self.graph_time_range.setSuffix(" seconds")
        graph_layout.addRow("Time Range:", self.graph_time_range)
        
        # Line styling
        graph_layout.addRow(QLabel(""))  # Spacer
        graph_layout.addRow(QLabel("<b>Line Styling:</b>"))
        
        self.graph_line_width = QDoubleSpinBox()
        self.graph_line_width.setRange(0.5, 5.0)
        self.graph_line_width.setValue(2.0)
        self.graph_line_width.setSingleStep(0.5)
        graph_layout.addRow("Line Width:", self.graph_line_width)
        
        self.graph_line_style = QComboBox()
        self.graph_line_style.addItems(["Solid", "Dashed", "Dotted"])
        graph_layout.addRow("Line Style:", self.graph_line_style)
        
        # Y-axis
        graph_layout.addRow(QLabel(""))  # Spacer
        graph_layout.addRow(QLabel("<b>Y-Axis:</b>"))
        
        self.graph_y_auto = QComboBox()
        self.graph_y_auto.addItems(["Auto Range", "Fixed Range"])
        graph_layout.addRow("Y-Axis Mode:", self.graph_y_auto)
        
        self.pages["Time Graph"] = graph_page
        self.options_stack.addWidget(graph_page)
        
        # 2. Log Table Page (Empty options)
        log_page = QWidget()
        QVBoxLayout(log_page) # Just to have a layout
        self.pages["Log Table"] = log_page
        self.options_stack.addWidget(log_page)
        
        # 3. Instant Value Page (Empty options, uses priority)
        instant_page = QWidget()
        QVBoxLayout(instant_page)
        self.pages["Instant Value"] = instant_page
        self.options_stack.addWidget(instant_page)
        
        # 4. Gauge Page
        gauge_page = QWidget()
        gauge_layout = QFormLayout(gauge_page)
        
        self.gauge_min = QDoubleSpinBox()
        self.gauge_min.setRange(-100000, 100000)
        self.gauge_min.setValue(0)
        
        self.gauge_max = QDoubleSpinBox()
        self.gauge_max.setRange(-100000, 100000)
        self.gauge_max.setValue(100)
        
        gauge_layout.addRow("Minimum Value:", self.gauge_min)
        gauge_layout.addRow("Maximum Value:", self.gauge_max)
        
        # Color zones
        gauge_layout.addRow(QLabel(""))  # Spacer
        gauge_layout.addRow(QLabel("<b>Color Zones:</b>"))
        
        self.gauge_use_zones = QComboBox()
        self.gauge_use_zones.addItems(["No Zones", "3 Zones (Safe/Warning/Critical)"])
        gauge_layout.addRow("Zone Mode:", self.gauge_use_zones)
        
        self.pages["Gauge"] = gauge_page
        self.options_stack.addWidget(gauge_page)
        
        # 5. Histogram Page
        hist_page = QWidget()
        hist_layout = QFormLayout(hist_page)
        self.hist_bins = QSpinBox()
        self.hist_bins.setRange(5, 100)
        self.hist_bins.setValue(20)
        hist_layout.addRow("Number of Bins:", self.hist_bins)
        self.pages["Histogram"] = hist_page
        self.options_stack.addWidget(hist_page)
        
        # 6. LED Page
        led_page = QWidget()
        led_layout = QVBoxLayout(led_page)
        
        # Instructions
        instructions = QLabel("Configure LED thresholds and colors for each parameter:")
        instructions.setStyleSheet("color: #aaa; font-style: italic;")
        led_layout.addWidget(instructions)
        
        # LED configuration table with color support
        self.led_table = QTableWidget()
        self.led_table.setColumnCount(5)
        self.led_table.setHorizontalHeaderLabels(["Parameter", "Threshold", "Condition", "Color", "Actions"])
        self.led_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.led_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.led_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.led_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.led_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.led_table.verticalHeader().setVisible(False)
        self.led_table.setMinimumHeight(200)
        
        led_layout.addWidget(self.led_table)
        
        # Add threshold button
        add_threshold_btn = QPushButton("+ Add Threshold")
        add_threshold_btn.setObjectName("SecondaryCTA")
        add_threshold_btn.clicked.connect(self.add_led_threshold_row)
        led_layout.addWidget(add_threshold_btn)
        
        self.pages["LED Indicator"] = led_page
        self.options_stack.addWidget(led_page)
        
        # 7. Map Page
        map_page = QWidget()
        map_layout = QFormLayout(map_page)
        self.map_zoom = QSpinBox()
        self.map_zoom.setRange(1, 18)
        self.map_zoom.setValue(10)
        map_layout.addRow("Initial Zoom:", self.map_zoom)
        self.pages["Map (GPS)"] = map_page
        self.options_stack.addWidget(map_page)
        
        right_layout.addStretch()
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Create Widget")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        right_layout.addWidget(buttons)
        
        main_layout.addWidget(right_panel, stretch=2)
        
        # Connect signals
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.sensor_group_combo.currentTextChanged.connect(self.filter_parameters)
        self.param_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Initialize
        self.filter_parameters()
        self.on_type_changed(self.type_combo.currentText())
        
        # If in edit mode, pre-fill values
        if self.edit_mode and self.existing_config:
            self._populate_from_config()
    
    def _populate_from_config(self):
        """Pre-fill dialog with existing widget configuration"""
        config = self.existing_config
        
        # Set widget type
        widget_type = config.get('displayType', '')
        index = self.type_combo.findText(widget_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Select parameters
        param_ids = config.get('param_ids', [])
        for i in range(self.param_list.count()):
            item = self.param_list.item(i)
            pid = item.data(Qt.ItemDataRole.UserRole)
            if pid in param_ids:
                item.setSelected(True)
        
        # Populate LED thresholds if LED widget
        if "LED" in widget_type:
            led_configs = config.get('options', {}).get('led_configs', {})
            for pid, led_config in led_configs.items():
                thresholds = led_config.get('thresholds', [])
                for threshold in thresholds:
                    # Find parameter name
                    param_name = next((p['name'] for p in self.parameters if p['id'] == pid), str(pid))
                    
                    # Add row
                    from app.ui.color_picker import ColorPickerButton
                    row = self.led_table.rowCount()
                    self.led_table.insertRow(row)
                    
                    # Parameter name
                    name_item = QTableWidgetItem(param_name)
                    name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    name_item.setData(Qt.ItemDataRole.UserRole, pid)
                    self.led_table.setItem(row, 0, name_item)
                    
                    # Threshold value
                    threshold_spin = QDoubleSpinBox()
                    threshold_spin.setRange(-100000, 100000)
                    threshold_spin.setValue(threshold.get('value', 50))
                    threshold_spin.setDecimals(2)
                    self.led_table.setCellWidget(row, 1, threshold_spin)
                    
                    # Condition
                    condition_combo = QComboBox()
                    condition_combo.addItems(["≥", "≤", ">", "<", "=="])
                    condition_combo.setCurrentText(threshold.get('condition', '≥'))
                    self.led_table.setCellWidget(row, 2, condition_combo)
                    
                    # Color picker
                    color_btn = ColorPickerButton(threshold.get('color', '#00ff00'))
                    self.led_table.setCellWidget(row, 3, color_btn)
                    
                    # Remove button
                    remove_btn = QPushButton("Remove")
                    remove_btn.setObjectName("SecondaryCTA")
                    remove_btn.clicked.connect(lambda checked, r=row: self.led_table.removeRow(r))
                    self.led_table.setCellWidget(row, 4, remove_btn)
    
    def filter_parameters(self):
        self.param_list.clear()
        group = self.sensor_group_combo.currentText()
        for p in sorted(self.parameters, key=lambda x: x['name']):
            if group == "All" or p.get('sensor_group', 'Default') == group:
                item = QListWidgetItem(f"{p['name']} ({p.get('unit', 'N/A')})")
                item.setData(Qt.ItemDataRole.UserRole, p['id'])
                item.setToolTip(f"ID: {p['id']}\nGroup: {p.get('sensor_group', 'Default')}\nDescription: {p.get('description', 'No description')}")
                self.param_list.addItem(item)
    
    def on_selection_changed(self):
        # No longer need to update LED table automatically
        pass
    
    def add_led_threshold_row(self):
        """Add a new threshold row to LED configuration table"""
        from app.ui.color_picker import ColorPickerButton
        
        selected_items = self.param_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Parameter Selected", "Please select at least one parameter first.")
            return
        
        # Use first selected parameter
        item = selected_items[0]
        param_name = item.text()
        param_id = item.data(Qt.ItemDataRole.UserRole)
        
        row = self.led_table.rowCount()
        self.led_table.insertRow(row)
        
        # Parameter name (read-only)
        name_item = QTableWidgetItem(param_name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        name_item.setData(Qt.ItemDataRole.UserRole, param_id)
        self.led_table.setItem(row, 0, name_item)
        
        # Threshold value
        threshold_spin = QDoubleSpinBox()
        threshold_spin.setRange(-100000, 100000)
        threshold_spin.setValue(50)
        threshold_spin.setDecimals(2)
        self.led_table.setCellWidget(row, 1, threshold_spin)
        
        # Condition
        condition_combo = QComboBox()
        condition_combo.addItems(["≥", "≤", ">", "<", "=="])
        self.led_table.setCellWidget(row, 2, condition_combo)
        
        # Color picker
        color_btn = ColorPickerButton('#00ff00')
        self.led_table.setCellWidget(row, 3, color_btn)
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("SecondaryCTA")
        remove_btn.clicked.connect(lambda: self.led_table.removeRow(row))
        self.led_table.setCellWidget(row, 4, remove_btn)

    def on_type_changed(self, text):
        # Switch stack page
        if text in self.pages:
            self.options_stack.setCurrentWidget(self.pages[text])
            
        # Update selection mode and priority
        if "Graph" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.priority_combo.setEnabled(False)
        elif "Instant" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.priority_combo.setEnabled(True)
        elif "Gauge" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(False)
        elif "LED" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.priority_combo.setEnabled(False)
        elif "Map" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
            self.priority_combo.setEnabled(False)
        elif "Histogram" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(False)
        else:  # Log Table
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.priority_combo.setEnabled(False)
    
    def validate_and_accept(self):
        if not self.param_list.selectedItems():
            QMessageBox.warning(self, "Selection Error", "You must select at least one parameter.")
            return
        
        widget_type = self.type_combo.currentText()
        selected_count = len(self.param_list.selectedItems())
        
        # Validate parameter count based on widget type
        if "Instant" in widget_type and selected_count < 1:
            QMessageBox.warning(self, "Selection Error", "Instant Value display requires at least one parameter.")
            return
        elif "Gauge" in widget_type and selected_count > 1:
            QMessageBox.warning(self, "Selection Error", "Gauge display supports only one parameter.")
            return
        elif "LED" in widget_type and selected_count < 1:
            QMessageBox.warning(self, "Selection Error", "LED Indicator display requires at least one parameter.")
            return
        elif "Histogram" in widget_type and selected_count > 1:
            QMessageBox.warning(self, "Selection Error", "Histogram display supports only one parameter.")
            return
        elif "Map" in widget_type and selected_count != 2:
            QMessageBox.warning(self, "Selection Error", "Map display requires exactly two parameters (Latitude and Longitude).")
            return
        
        self.accept()
    
    def get_selection(self):
        selected_items = self.param_list.selectedItems()
        param_ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        
        # Get widget options
        options = {}
        widget_type = self.type_combo.currentText()
        
        if "Graph" in widget_type:
            options['time_range'] = self.graph_time_range.value()
            options['line_width'] = self.graph_line_width.value()
            options['line_style'] = self.graph_line_style.currentText()
            options['y_axis_mode'] = self.graph_y_auto.currentText()
        elif "Gauge" in widget_type:
            options['min_value'] = self.gauge_min.value()
            options['max_value'] = self.gauge_max.value()
            options['use_zones'] = self.gauge_use_zones.currentText() != "No Zones"
        elif "LED" in widget_type:
            # Gather multi-threshold configurations with colors
            led_configs = {}
            for row in range(self.led_table.rowCount()):
                item = self.led_table.item(row, 0)
                if not item:
                    continue
                    
                pid = item.data(Qt.ItemDataRole.UserRole)
                threshold_widget = self.led_table.cellWidget(row, 1)
                condition_widget = self.led_table.cellWidget(row, 2)
                color_widget = self.led_table.cellWidget(row, 3)
                
                if not all([threshold_widget, condition_widget, color_widget]):
                    continue
                
                # Initialize threshold list for this parameter if needed
                if pid not in led_configs:
                    led_configs[pid] = {'thresholds': []}
                
                # Add threshold configuration
                led_configs[pid]['thresholds'].append({
                    'value': threshold_widget.value(),
                    'condition': condition_widget.currentText(),
                    'color': color_widget.get_color()
                })
            
            options['led_configs'] = led_configs
            
        elif "Map" in widget_type:
            options['zoom'] = self.map_zoom.value()
        elif "Histogram" in widget_type:
            options['bins'] = self.hist_bins.value()
        
        return {
            'param_ids': param_ids, 
            'displayType': widget_type, 
            'priority': self.priority_combo.currentText(),
            'options': options
        }


class DataLoggingDialog(QDialog):
    """
    @brief Dialog for configuring data logging.
    @details Allows user to select format (CSV/JSON), file path, buffer size, and parameters to log.
    """
    def __init__(self, parameters, current_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Data Logging")
        self.parameters = parameters
        self.setMinimumSize(500, 400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        
        # Title
        title = QLabel("<h2 style='color: #ffffff; margin: 0 0 16px 0;'>Data Logging Configuration</h2>")
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
            # Show default location hint
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
        
        # Parameter selection
        param_group = QGroupBox("Parameters to Log")
        param_layout = QVBoxLayout(param_group)
        
        self.param_list = QListWidget()
        self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.param_list.setMinimumHeight(150)
        
        for param in self.parameters:
            item = QListWidgetItem(f"{param['name']} ({param.get('unit', 'N/A')}) - {param['id']}")
            item.setData(Qt.ItemDataRole.UserRole, param['id'])
            item.setCheckState(Qt.CheckState.Checked)  # All selected by default
            self.param_list.addItem(item)
        
        param_layout.addWidget(self.param_list)
        
        # Buttons for parameter selection
        param_btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_none_btn = QPushButton("Select None")
        select_all_btn.clicked.connect(self.select_all_params)
        select_none_btn.clicked.connect(self.select_none_params)
        param_btn_layout.addWidget(select_all_btn)
        param_btn_layout.addWidget(select_none_btn)
        param_btn_layout.addStretch()
        param_layout.addLayout(param_btn_layout)
        
        main_layout.addWidget(settings_group)
        main_layout.addWidget(param_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Configure Logging")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        main_layout.addWidget(buttons)
        
        # Connect signals
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        # Load current settings if provided
        if current_settings:
            self.load_settings(current_settings)
    
    def browse_file(self):
        # Ensure logs directory exists
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Start file dialog in logs directory
        default_name = f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if self.format_combo.currentText().lower() == 'csv':
            default_name += ".csv"
            file_filter = "CSV Files (*.csv);;All Files (*)"
        else:
            default_name += ".json"
            file_filter = "JSON Files (*.json);;All Files (*)"
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File Location",
            os.path.join(logs_dir, default_name),
            file_filter
        )
        if path:
            self.file_path_edit.setText(path)
    
    def select_all_params(self):
        """Select all parameters"""
        for i in range(self.param_list.count()):
            self.param_list.item(i).setCheckState(Qt.CheckState.Checked)
    
    def select_none_params(self):
        """Deselect all parameters"""
        for i in range(self.param_list.count()):
            self.param_list.item(i).setCheckState(Qt.CheckState.Unchecked)
    
    def load_settings(self, settings):
        """Load existing settings"""
        if 'format' in settings:
            format_map = {'csv': 'CSV', 'json': 'JSON'}
            self.format_combo.setCurrentText(format_map.get(settings['format'], 'CSV'))
        if 'file_path' in settings:
            self.file_path_edit.setText(settings['file_path'])
        if 'buffer_size' in settings:
            self.buffer_spin.setValue(settings['buffer_size'])
        if 'selected_params' in settings:
            for i in range(self.param_list.count()):
                item = self.param_list.item(i)
                param_id = item.data(Qt.ItemDataRole.UserRole)
                if param_id in settings['selected_params']:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
    
    def validate_and_accept(self):
        """Validate settings and accept"""
        # Check if at least one parameter is selected
        selected_params = []
        for i in range(self.param_list.count()):
            item = self.param_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_params.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not selected_params:
            QMessageBox.warning(self, "No Parameters Selected", "Please select at least one parameter to log.")
            return
        
        self.accept()
    
    def get_settings(self):
        """Get the logging configuration"""
        selected_params = []
        for i in range(self.param_list.count()):
            item = self.param_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_params.append(item.data(Qt.ItemDataRole.UserRole))
        
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
        self.undo_btn.setIcon(QIcon.fromTheme("edit-undo"))
        self.undo_btn.clicked.connect(self.undo)
        
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.setIcon(QIcon.fromTheme("edit-redo"))
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
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        edit_btn = QPushButton("Edit Parameter")
        edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        remove_btn = QPushButton("Remove Parameter")
        remove_btn.setIcon(QIcon.fromTheme("list-remove"))
        
        up_btn = QPushButton("Move Up")
        up_btn.setIcon(QIcon.fromTheme("go-up"))
        down_btn = QPushButton("Move Down")
        down_btn.setIcon(QIcon.fromTheme("go-down"))
        
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
