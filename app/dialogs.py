from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QComboBox, QLineEdit, QSpinBox,
    QListWidget, QAbstractItemView, QPushButton, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QDoubleSpinBox,
    QMessageBox, QGroupBox, QFileDialog
)
from PySide6.QtCore import Qt


class ConnectionSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent); self.setWindowTitle("Connection Settings"); self._settings = dict(settings)
        form = QFormLayout(self)
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["serial","tcp","udp"])
        self.mode_combo.setCurrentText(self._settings.get('mode','serial'))
        self.serial_port_edit = QLineEdit(self._settings.get('serial_port','COM4'))
        self.baud_spin = QSpinBox(); self.baud_spin.setRange(300, 10000000); self.baud_spin.setValue(int(self._settings.get('baudrate',115200)))
        self.tcp_host_edit = QLineEdit(self._settings.get('tcp_host','127.0.0.1'))
        self.tcp_port_spin = QSpinBox(); self.tcp_port_spin.setRange(1, 65535); self.tcp_port_spin.setValue(int(self._settings.get('tcp_port',9000)))
        self.udp_host_edit = QLineEdit(self._settings.get('udp_host','0.0.0.0'))
        self.udp_port_spin = QSpinBox(); self.udp_port_spin.setRange(1, 65535); self.udp_port_spin.setValue(int(self._settings.get('udp_port',9000)))
        self.format_combo = QComboBox(); self.format_combo.addItems(["json_array","csv","raw_bytes","bits"])
        self.format_combo.setCurrentText(self._settings.get('data_format','json_array'))
        self.channels_spin = QSpinBox(); self.channels_spin.setRange(1, 1024); self.channels_spin.setValue(int(self._settings.get('channel_count',32)))
        self.width_spin = QSpinBox(); self.width_spin.setRange(1, 8); self.width_spin.setValue(int(self._settings.get('sample_width_bytes',2)))
        self.endian_combo = QComboBox(); self.endian_combo.addItems(["little","big"])
        self.endian_combo.setCurrentText('little' if self._settings.get('little_endian',True) else 'big')
        self.csv_sep_edit = QLineEdit(self._settings.get('csv_separator',','))
        form.addRow("Mode:", self.mode_combo)
        form.addRow("Serial Port:", self.serial_port_edit)
        form.addRow("Baudrate:", self.baud_spin)
        form.addRow("TCP Host:", self.tcp_host_edit)
        form.addRow("TCP Port:", self.tcp_port_spin)
        form.addRow("UDP Host:", self.udp_host_edit)
        form.addRow("UDP Port:", self.udp_port_spin)
        form.addRow("Format:", self.format_combo)
        form.addRow("Channels:", self.channels_spin)
        form.addRow("Sample Width (bytes):", self.width_spin)
        form.addRow("Endianness:", self.endian_combo)
        form.addRow("CSV Separator:", self.csv_sep_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

    def get_settings(self):
        return {
            'mode': self.mode_combo.currentText(),
            'serial_port': self.serial_port_edit.text().strip(),
            'baudrate': int(self.baud_spin.value()),
            'tcp_host': self.tcp_host_edit.text().strip(),
            'tcp_port': int(self.tcp_port_spin.value()),
            'udp_host': self.udp_host_edit.text().strip(),
            'udp_port': int(self.udp_port_spin.value()),
            'timeout': 1.0,
            'data_format': self.format_combo.currentText(),
            'channel_count': int(self.channels_spin.value()),
            'sample_width_bytes': int(self.width_spin.value()),
            'little_endian': (self.endian_combo.currentText() == 'little'),
            'csv_separator': self.csv_sep_edit.text() or ',',
        }


class AddWidgetDialog(QDialog):
    def __init__(self, parameters, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Display Widget")
        self.parameters = parameters
        self.setMinimumSize(600, 500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        
        # Title
        title = QLabel("<h2 style='color: #ffffff; margin: 0 0 16px 0;'>Create New Widget</h2>")
        main_layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Sensor group selection
        self.sensor_group_combo = QComboBox()
        groups = sorted(list(set(p.get('sensor_group', 'Default') for p in self.parameters)))
        self.sensor_group_combo.addItems(["All"] + groups)
        form_layout.addRow("Sensor Group:", self.sensor_group_combo)
        
        # Parameter selection
        param_group = QGroupBox("Select Parameters")
        param_layout = QVBoxLayout(param_group)
        param_layout.setContentsMargins(8, 8, 8, 8)
        
        self.param_list = QListWidget()
        self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.param_list.setMinimumHeight(120)
        param_layout.addWidget(self.param_list)
        form_layout.addRow(param_group)
        
        # Display type selection
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Instant Value", 
            "Time Graph", 
            "Log Table", 
            "Gauge", 
            "Histogram", 
            "LED Indicator", 
            "Map (GPS)"
        ])
        form_layout.addRow("Display Type:", self.type_combo)
        
        # Priority selection (only for Instant)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        form_layout.addRow("Priority:", self.priority_combo)
        
        # Widget-specific options
        self.options_group = QGroupBox("Widget Options")
        self.options_layout = QFormLayout(self.options_group)
        self.options_layout.setContentsMargins(8, 8, 8, 8)
        
        # Graph options
        self.graph_time_range = QSpinBox()
        self.graph_time_range.setRange(10, 3600)
        self.graph_time_range.setValue(300)
        self.graph_time_range.setSuffix(" seconds")
        
        # Gauge options
        self.gauge_min = QDoubleSpinBox()
        self.gauge_min.setRange(-100000, 100000)
        self.gauge_min.setValue(0)
        self.gauge_max = QDoubleSpinBox()
        self.gauge_max.setRange(-100000, 100000)
        self.gauge_max.setValue(100)
        
        # LED options
        self.led_threshold = QDoubleSpinBox()
        self.led_threshold.setRange(-100000, 100000)
        self.led_threshold.setValue(50)
        self.led_condition = QComboBox()
        self.led_condition.addItems([">", "<", ">=", "<=", "=="])
        
        # Map options
        self.map_zoom = QSpinBox()
        self.map_zoom.setRange(1, 18)
        self.map_zoom.setValue(10)
        
        # Histogram options
        self.hist_bins = QSpinBox()
        self.hist_bins.setRange(5, 100)
        self.hist_bins.setValue(20)
        
        form_layout.addRow(self.options_group)
        main_layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Create Widget")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        main_layout.addWidget(buttons)
        
        # Connect signals
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.sensor_group_combo.currentTextChanged.connect(self.filter_parameters)
        
        # Initialize
        self.on_type_changed(self.type_combo.currentText())
        self.filter_parameters()
    
    def filter_parameters(self):
        self.param_list.clear()
        group = self.sensor_group_combo.currentText()
        for p in sorted(self.parameters, key=lambda x: x['name']):
            if group == "All" or p.get('sensor_group', 'Default') == group:
                from PySide6.QtWidgets import QListWidgetItem
                item = QListWidgetItem(f"{p['name']} ({p.get('unit', 'N/A')})")
                item.setData(Qt.ItemDataRole.UserRole, p['id'])
                item.setToolTip(f"ID: {p['id']}\nGroup: {p.get('sensor_group', 'Default')}\nDescription: {p.get('description', 'No description')}")
                self.param_list.addItem(item)
    
    def on_type_changed(self, text):
        # Clear all options first
        for i in reversed(range(self.options_layout.rowCount())):
            self.options_layout.removeRow(i)
        
        # Add options based on widget type
        if "Graph" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.priority_combo.setEnabled(False)
            self.options_layout.addRow("Time Range:", self.graph_time_range)
        elif "Instant" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(True)
        elif "Gauge" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(False)
            self.options_layout.addRow("Min Value:", self.gauge_min)
            self.options_layout.addRow("Max Value:", self.gauge_max)
        elif "LED" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(False)
            self.options_layout.addRow("Threshold:", self.led_threshold)
            self.options_layout.addRow("Condition:", self.led_condition)
        elif "Map" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
            self.priority_combo.setEnabled(False)
            self.options_layout.addRow("Initial Zoom:", self.map_zoom)
        elif "Histogram" in text:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(False)
            self.options_layout.addRow("Number of Bins:", self.hist_bins)
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
        if "Instant" in widget_type and selected_count > 1:
            QMessageBox.warning(self, "Selection Error", "Instant Value display supports only one parameter.")
            return
        elif "Gauge" in widget_type and selected_count > 1:
            QMessageBox.warning(self, "Selection Error", "Gauge display supports only one parameter.")
            return
        elif "LED" in widget_type and selected_count > 1:
            QMessageBox.warning(self, "Selection Error", "LED Indicator display supports only one parameter.")
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
        elif "Gauge" in widget_type:
            options['min_value'] = self.gauge_min.value()
            options['max_value'] = self.gauge_max.value()
        elif "LED" in widget_type:
            options['threshold'] = self.led_threshold.value()
            options['condition'] = self.led_condition.currentText()
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
        self.file_path_edit.setPlaceholderText("Leave empty for auto-generated filename")
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
        """Browse for log file location"""
        format_ext = "csv" if self.format_combo.currentText() == "CSV" else "json"
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Log File Location", 
            f"dashboard_data.{format_ext}",
            f"{format_ext.upper()} Files (*.{format_ext})"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
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
    def __init__(self, param=None, existing_ids=None, parent=None):
        super().__init__(parent)
        self.existing_ids = existing_ids or []
        self.is_edit_mode = param is not None
        self.setWindowTitle("Edit Parameter" if self.is_edit_mode else "Add New Parameter")
        self.setMinimumSize(500, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        
        # Title
        title = QLabel(f"<h2 style='color: #ffffff; margin: 0 0 16px 0;'>{'Edit Parameter' if self.is_edit_mode else 'Add New Parameter'}</h2>")
        main_layout.addWidget(title)
        
        # Form layout
        layout = QFormLayout()
        layout.setSpacing(12)
        
        # Basic information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.id_edit = QLineEdit(param['id'] if param else "")
        if self.is_edit_mode: 
            self.id_edit.setReadOnly(True)
            self.id_edit.setStyleSheet("background-color: #3a3a3a; color: #888888;")
        self.name_edit = QLineEdit(param['name'] if param else "")
        self.desc_edit = QLineEdit(param.get('description', '') if param else "")
        
        basic_layout.addRow("Parameter ID:", self.id_edit)
        basic_layout.addRow("Display Name:", self.name_edit)
        basic_layout.addRow("Description:", self.desc_edit)
        
        # Data mapping
        mapping_group = QGroupBox("Data Mapping")
        mapping_layout = QFormLayout(mapping_group)
        
        self.index_spin = QSpinBox()
        self.index_spin.setRange(0, 255)
        self.index_spin.setValue(param.get('array_index', 0) if param else 0)
        self.index_spin.setToolTip("Array index where this parameter's data is located in the incoming data packet")
        
        self.group_edit = QLineEdit(param.get('sensor_group', '') if param else "")
        self.group_edit.setPlaceholderText("e.g., MPU6050, GPS, Temperature")
        
        self.unit_edit = QLineEdit(param['unit'] if param else "")
        self.unit_edit.setPlaceholderText("e.g., °C, m/s², V, %")
        
        mapping_layout.addRow("Array Index:", self.index_spin)
        mapping_layout.addRow("Sensor Group:", self.group_edit)
        mapping_layout.addRow("Unit:", self.unit_edit)
        
        # Display preferences
        display_group = QGroupBox("Display Preferences")
        display_layout = QFormLayout(display_group)
        
        self.color_combo = QComboBox()
        colors = ["Auto", "Blue (#00BFFF)", "Red (#FF3131)", "Green (#21b35a)", "Yellow (#FFBF00)", "Purple (#F012BE)", "Cyan (#39CCCC)", "Orange (#FF851B)"]
        self.color_combo.addItems(colors)
        if param and 'color' in param:
            color_name = param['color']
            for i, color in enumerate(colors):
                if color_name in color:
                    self.color_combo.setCurrentIndex(i)
                    break
        
        self.decimals_spin = QSpinBox()
        self.decimals_spin.setRange(0, 6)
        self.decimals_spin.setValue(param.get('decimals', 2) if param else 2)
        self.decimals_spin.setToolTip("Number of decimal places to display")
        
        display_layout.addRow("Preferred Color:", self.color_combo)
        display_layout.addRow("Decimal Places:", self.decimals_spin)
        
        # Alarm thresholds
        alarm_group = QGroupBox("Alarm Thresholds")
        alarm_layout = QFormLayout(alarm_group)
        
        self.low_crit = QDoubleSpinBox()
        self.low_warn = QDoubleSpinBox()
        self.high_warn = QDoubleSpinBox()
        self.high_crit = QDoubleSpinBox()
        
        for spin in [self.low_crit, self.low_warn, self.high_warn, self.high_crit]:
            spin.setRange(-100000, 100000)
            spin.setDecimals(3)
            spin.setSuffix(" " + (param['unit'] if param else ''))
        
        if param:
            t = param.get('threshold', {})
            self.low_crit.setValue(t.get('low_crit', 0))
            self.low_warn.setValue(t.get('low_warn', 10))
            self.high_warn.setValue(t.get('high_warn', 80))
            self.high_crit.setValue(t.get('high_crit', 100))
        
        alarm_layout.addRow("Low Critical:", self.low_crit)
        alarm_layout.addRow("Low Warning:", self.low_warn)
        alarm_layout.addRow("High Warning:", self.high_warn)
        alarm_layout.addRow("High Critical:", self.high_crit)
        
        # Add groups to main layout
        main_layout.addWidget(basic_group)
        main_layout.addWidget(mapping_group)
        main_layout.addWidget(display_group)
        main_layout.addWidget(alarm_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Save Parameter")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        main_layout.addWidget(buttons)
        
        # Connect signals
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

    def validate_and_accept(self):
        new_id = self.id_edit.text().strip()
        if ' ' in new_id: QMessageBox.warning(self, "Validation Error", "ID cannot contain spaces."); return
        if not new_id or not self.name_edit.text().strip(): QMessageBox.warning(self, "Validation Error", "ID and Name are required."); return
        if not self.is_edit_mode and new_id in self.existing_ids: QMessageBox.warning(self, "Validation Error", f"ID '{new_id}' already exists."); return
        if not (self.low_crit.value() < self.low_warn.value() < self.high_warn.value() < self.high_crit.value()):
            QMessageBox.warning(self, "Validation Error", "Thresholds must be in increasing order."); return
        self.accept()

    def get_data(self):
        # Extract color from combo box selection
        color_text = self.color_combo.currentText()
        color = None
        if color_text != "Auto":
            # Extract hex color from text like "Blue (#00BFFF)"
            import re
            match = re.search(r'#([A-Fa-f0-9]{6})', color_text)
            if match:
                color = '#' + match.group(1)
        
        return {
            'id': self.id_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'array_index': self.index_spin.value(),
            'sensor_group': self.group_edit.text().strip(),
            'unit': self.unit_edit.text().strip(),
            'description': self.desc_edit.text().strip(),
            'color': color,
            'decimals': self.decimals_spin.value(),
            'threshold': {
                'low_crit': self.low_crit.value(),
                'low_warn': self.low_warn.value(),
                'high_warn': self.high_warn.value(),
                'high_crit': self.high_crit.value()
            }
        }


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
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get('array_index', 'N/A'))))
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


