from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QComboBox, QLineEdit, QSpinBox,
    QListWidget, QAbstractItemView, QPushButton, QVBoxLayout, QLabel
)


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
        super().__init__(parent); self.setWindowTitle("Add Display Widget")
        self.parameters = parameters
        layout = QFormLayout(self)
        self.sensor_group_combo = QComboBox()
        groups = sorted(list(set(p.get('sensor_group', 'Default') for p in self.parameters)))
        self.sensor_group_combo.addItems(["All"] + groups)
        self.param_list = QListWidget(); self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.type_combo = QComboBox(); self.type_combo.addItems(["Instant", "Graph", "Log Table"])
        self.priority_combo = QComboBox(); self.priority_combo.addItems(["High", "Medium", "Low"])
        layout.addRow("Sensor Group:", self.sensor_group_combo)
        layout.addRow("Parameter(s):", self.param_list)
        layout.addRow("Display Type:", self.type_combo); layout.addRow("Display Priority:", self.priority_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept); buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.sensor_group_combo.currentTextChanged.connect(self.filter_parameters)
        self.on_type_changed(self.type_combo.currentText()); self.filter_parameters()
    def filter_parameters(self):
        self.param_list.clear()
        group = self.sensor_group_combo.currentText()
        for p in sorted(self.parameters, key=lambda x: x['name']):
            if group == "All" or p.get('sensor_group', 'Default') == group:
                from PySide6.QtWidgets import QListWidgetItem
                self.param_list.addItem(QListWidgetItem(p['name']))
    def on_type_changed(self, text):
        if text == "Instant":
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(True)
        else:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.priority_combo.setEnabled(False)
    def validate_and_accept(self):
        if not self.param_list.selectedItems():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Selection Error", "You must select at least one parameter."); return
        if self.type_combo.currentText() == "Instant" and len(self.param_list.selectedItems()) > 1:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Selection Error", "'Instant' display supports only one parameter."); return
        self.accept()
    def get_selection(self):
        selected_names = [item.text() for item in self.param_list.selectedItems()]
        param_ids = [p['id'] for p in self.parameters if p['name'] in selected_names]
        return {'param_ids': param_ids, 'displayType': self.type_combo.currentText(), 'priority': self.priority_combo.currentText()}


