import sys
import random
import time
import json
import base64
import math
import uuid
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QComboBox, QLineEdit,
    QLabel, QFrame, QPushButton, QFileDialog, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QTabWidget,
    QDialog, QFormLayout, QDialogButtonBox, QDoubleSpinBox, QDockWidget,
    QSizePolicy, QInputDialog, QMessageBox, QTabBar, QAbstractItemView,
    QSpinBox # --- NEW ---
)
from PySide6.QtCore import QThread, Signal, Qt, QTimer, QByteArray
from PySide6.QtGui import QFont, QColor, QBrush
import pyqtgraph as pg
import numpy as np

# --- 1. DATA SIMULATOR & WIDGETS ---

# --- MODIFIED: Now works with an array/list of data ---
class DataSimulator(QThread):
    newData = Signal(list) # Emits a list of values

    def __init__(self, num_channels=32):
        super().__init__()
        self.num_channels = num_channels
        self._is_running = True
        self._is_paused = False
        self.mode = "dummy" # "dummy" or "backend"

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
                    # Placeholder for real backend connection (e.g., socket, serial)
                    # For now, it does nothing.
                    pass
            time.sleep(0.1)

    def toggle_pause(self):
        self._is_paused = not self._is_paused
        return self._is_paused

    def stop(self):
        self._is_running = False

class ValueCard(QFrame):
    # (Unchanged)
    def __init__(self, param_name, unit, priority):
        super().__init__(); self.setFrameShape(QFrame.Shape.StyledPanel); layout = QVBoxLayout(self)
        self.name_label = QLabel(f"{param_name} ({unit})"); self.name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.value_label = QLabel("---"); self.value_label.setFont(QFont("Monospace", 24, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label); layout.addWidget(self.value_label)
        self.priority = priority; self.set_alarm_state('Nominal')
    def update_value(self, value, alarm_state): self.value_label.setText(f"{value:.2f}" if value is not None else "NO DATA"); self.set_alarm_state(alarm_state)
    def set_alarm_state(self, state):
        alarm_colors = {'Critical': '#FF3131', 'Warning': '#FFBF00', 'Nominal': '#2a2a2a'}
        priority_colors = {'High': '#FF3131', 'Medium': '#0078FF', 'Low': 'transparent'}
        bg_color = alarm_colors.get(state, '#2a2a2a'); border_color = priority_colors.get(self.priority, 'transparent')
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px; border: 3px solid {border_color};")

class TimeGraph(QWidget):
    # (Unchanged)
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs; self.curves = {}; self.last_known_values = {}
        self.plot_widget = pg.PlotWidget(); self.plot_widget.setBackground(QColor(10, 10, 10))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Time (s)', color='#FFFFFF')
        self.plot_widget.addLegend()
        title = ", ".join([p['name'] for p in self.param_configs])
        units = list(set([p['unit'] for p in self.param_configs]))
        unit_label = units[0] if len(units) == 1 else "Multiple Units"
        self.plot_widget.setTitle(title, color='w', size='12pt'); self.plot_widget.setLabel('left', unit_label, color='#FFFFFF')
        axis_pen = pg.mkPen(color='#FFFFFF', width=1)
        self.plot_widget.getAxis('left').setPen(axis_pen); self.plot_widget.getAxis('bottom').setPen(axis_pen)
        for p_config in self.param_configs:
            pen = pg.mkPen(p_config['color'], width=2)
            curve = self.plot_widget.plot(pen=pen, name=p_config['name']); self.curves[p_config['id']] = curve
        layout = QVBoxLayout(self); layout.addWidget(self.plot_widget); self.setLayout(layout)
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
        pos = evt[0]
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_widget.getPlotItem().vb.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x()); self.hLine.setPos(mousePoint.y())
            text = f"Time: {mousePoint.x():.2f}s\n"
            for pid, curve in self.curves.items():
                x_data, y_data = curve.getData()
                if x_data is not None and len(x_data) > 0:
                    idx = np.searchsorted(x_data, mousePoint.x())
                    if 0 < idx < len(x_data):
                        y_val = y_data[idx]
                        p_name = next(p['name'] for p in self.param_configs if p['id'] == pid)
                        text += f"{p_name}: {y_val:.2f}\n"
            self.label.setText(text.strip()); self.label.setPos(mousePoint)
    def mouse_clicked(self, evt):
        if evt.double(): return
        pos = self.plot_widget.getPlotItem().vb.mapSceneToView(evt.scenePos())
        min_dist = float('inf'); nearest_point = None
        for pid, curve in self.curves.items():
            x_data, y_data = curve.getData()
            if x_data is None or len(x_data) == 0: continue
            for i, (x, y) in enumerate(zip(x_data, y_data)):
                dist = (x - pos.x())**2 + (y - pos.y())**2
                if dist < min_dist:
                    min_dist = dist
                    p_name = next(p['name'] for p in self.param_configs if p['id'] == pid)
                    nearest_point = (p_name, self.start_time + x, y)
        if nearest_point:
            name, ts, val = nearest_point
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
            QMessageBox.information(self, "Data Point Selected", f"Parameter: {name}\nValue: {val:.3f}\nTimestamp: {time_str}")

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

class AddWidgetDialog(QDialog):
    # (Unchanged)
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
                self.param_list.addItem(p['name'])
    def on_type_changed(self, text):
        if text == "Instant":
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.priority_combo.setEnabled(True)
        else:
            self.param_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.priority_combo.setEnabled(False)
    def validate_and_accept(self):
        if not self.param_list.selectedItems():
            QMessageBox.warning(self, "Selection Error", "You must select at least one parameter."); return
        if self.type_combo.currentText() == "Instant" and len(self.param_list.selectedItems()) > 1:
            QMessageBox.warning(self, "Selection Error", "'Instant' display supports only one parameter."); return
        self.accept()
    def get_selection(self):
        selected_names = [item.text() for item in self.param_list.selectedItems()]
        param_ids = [p['id'] for p in self.parameters if p['name'] in selected_names]
        return {'param_ids': param_ids, 'displayType': self.type_combo.currentText(), 'priority': self.priority_combo.currentText()}

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
        super().__init__(); self.setWindowTitle("Ignition Dashboard (PySide6)"); self.setGeometry(100, 100, 1800, 1000)
        self.graph_color_palette = ['#00BFFF', '#FF3131', '#39CCCC', '#F012BE', '#FFDC00', '#7FDBFF', '#01FF70', '#FF851B']
        self.next_graph_color_index = 0
        self.parameters = []; self.data_history = {}; self.tab_data = {}
        self.create_control_dock()
        self.tab_widget = QTabWidget(); self.tab_widget.setTabsClosable(True); self.setCentralWidget(self.tab_widget)
        self.tab_widget.currentChanged.connect(self.on_tab_changed); self.tab_widget.tabCloseRequested.connect(self.close_tab)
        header_widget = QWidget(); header_layout = QHBoxLayout(header_widget)
        self.stream_status_label = QLabel("● Awaiting Parameters")
        self.pause_button = QPushButton("Pause Stream"); self.pause_button.setCheckable(True)
        header_layout.addWidget(QLabel("<h2>Dashboard</h2>")); header_layout.addStretch()
        header_layout.addWidget(self.stream_status_label); header_layout.addWidget(self.pause_button)
        header_dock = QDockWidget(); header_dock.setTitleBarWidget(QWidget())
        header_dock.setWidget(header_widget); header_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, header_dock)
        self.health_timer = QTimer(self); self.health_timer.timeout.connect(self.check_data_stream); self.health_timer.start(1000)
        self.pause_button.clicked.connect(self.toggle_pause_stream); self.simulator = None
        self.apply_stylesheet()
        self.add_new_tab(name="Main View", is_closable=False)
        self.restart_simulator()
        self.update_control_states()

    def create_control_dock(self):
        control_dock = QDockWidget("CONTROLS"); control_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        main_control_widget = QWidget(); layout = QVBoxLayout(main_control_widget)
        # --- NEW: Data Source Selection ---
        source_group = QGroupBox("DATA SOURCE")
        source_layout = QFormLayout(source_group)
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Dummy Data", "Backend (Not Implemented)"])
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        source_layout.addRow("Source:", self.source_combo)
        # ---
        setup_group = QGroupBox("SYSTEM SETUP"); setup_layout = QVBoxLayout(setup_group)
        manage_params_btn = QPushButton("Manage Parameters..."); setup_layout.addWidget(manage_params_btn)
        project_group = QGroupBox("PROJECT"); project_layout = QGridLayout(project_group)
        save_btn, load_btn = QPushButton("Save Project"), QPushButton("Load Project")
        project_layout.addWidget(load_btn, 0, 0); project_layout.addWidget(save_btn, 0, 1)
        tab_group = QGroupBox("TABS"); tab_layout = QGridLayout(tab_group)
        add_tab_btn, rename_tab_btn = QPushButton("Add Tab"), QPushButton("Rename Current Tab")
        tab_layout.addWidget(add_tab_btn, 0, 0); tab_layout.addWidget(rename_tab_btn, 0, 1)
        widget_group = QGroupBox("WIDGETS"); widget_layout = QVBoxLayout(widget_group)
        self.add_widget_btn = QPushButton("Add Widget to Current Tab..."); self.add_widget_btn.setObjectName("AddWidgetButton")
        self.active_displays_list = QListWidget(); remove_display_btn = QPushButton("Remove Selected Widget")
        widget_layout.addWidget(self.add_widget_btn); widget_layout.addWidget(self.active_displays_list); widget_layout.addWidget(remove_display_btn)
        layout.addWidget(source_group); layout.addWidget(setup_group); layout.addWidget(project_group); layout.addWidget(tab_group); layout.addWidget(widget_group); layout.addStretch()
        control_dock.setWidget(main_control_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, control_dock)
        self.add_widget_btn.clicked.connect(self.open_add_widget_dialog); remove_display_btn.clicked.connect(self.remove_selected_display)
        add_tab_btn.clicked.connect(lambda: self.add_new_tab()); rename_tab_btn.clicked.connect(self.rename_current_tab)
        manage_params_btn.clicked.connect(self.open_manage_parameters_dialog)
        save_btn.clicked.connect(self.save_project); load_btn.clicked.connect(self.load_project)

    # --- MODIFIED: Handles new data source selection ---
    def on_source_changed(self, source_text):
        if not self.simulator: return
        if "Dummy" in source_text:
            self.simulator.mode = "dummy"
            if self.simulator._is_paused: self.toggle_pause_stream()
        else: # Backend
            self.simulator.mode = "backend"
            # In a real app, you would initiate the backend connection here
            if not self.simulator._is_paused: self.toggle_pause_stream()
            QMessageBox.information(self, "Backend", "Backend connection is not implemented in this demo.")

    def add_widget_to_dashboard(self, config, tab_index, widget_id=None):
        # (Unchanged)
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        if widget_id is None: widget_id = str(uuid.uuid4())
        param_ids = config['param_ids']
        param_configs = [p for p in self.parameters if p['id'] in param_ids]
        if not param_configs: return
        widget_title = ", ".join([p['name'] for p in param_configs])
        widget = None
        if config['displayType'] == 'Graph':
            for p_config in param_configs:
                p_config['color'] = self.graph_color_palette[self.next_graph_color_index % len(self.graph_color_palette)]
                self.next_graph_color_index += 1
            widget = TimeGraph(param_configs)
        elif config['displayType'] == 'Log Table':
            widget = LogTable(param_configs)
        elif config['displayType'] == 'Instant' and len(param_configs) == 1:
            p_config = param_configs[0]
            widget = ValueCard(p_config['name'], p_config['unit'], config['priority'])
        if widget:
            dock = QDockWidget(f"{widget_title} ({config['displayType']})", self); dock.setWidget(widget)
            tab_mainwindow = tab_info['mainwindow']
            num_docks = len(tab_info['docks']); docks_list = list(tab_info['docks'].values())
            if num_docks == 0: tab_mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            elif num_docks == 1: tab_mainwindow.splitDockWidget(docks_list[0], dock, Qt.Orientation.Horizontal)
            else: tab_mainwindow.tabifyDockWidget(docks_list[-1], dock)
            dock.raise_()
            tab_info['widgets'][widget_id] = widget; tab_info['docks'][widget_id] = dock; tab_info['configs'][widget_id] = config
            self.refresh_active_displays_list()

    # --- HEAVILY MODIFIED: Core logic now processes an array, not a dict ---
    def update_data(self, packet: list):
        timestamp = time.time()

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

    def restart_simulator(self):
        # (Unchanged logic, just passes different args to simulator)
        if self.simulator: self.simulator.stop(); self.simulator.wait()
        self.simulator = DataSimulator(num_channels=32) # Assume 32 channels from backend/dummy
        self.simulator.newData.connect(self.update_data)
        self.simulator.start()

    # --- All other MainWindow methods are unchanged ---
    def open_add_widget_dialog(self):
        index = self.tab_widget.currentIndex()
        if index < 0: QMessageBox.warning(self, "No Tab", "No active tab to add a widget to."); return
        dialog = AddWidgetDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selection = dialog.get_selection()
            if selection: self.add_widget_to_dashboard(selection, index)
    def remove_selected_display(self):
        index = self.tab_widget.currentIndex();
        if index < 0: return
        selected_items = self.active_displays_list.selectedItems()
        if not selected_items: return
        widget_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        tab_info = self.tab_data[index]
        if widget_id in tab_info['docks']: tab_info['docks'][widget_id].deleteLater(); del tab_info['docks'][widget_id]
        if widget_id in tab_info['widgets']: del tab_info['widgets'][widget_id]
        if widget_id in tab_info['configs']: del tab_info['configs'][widget_id]
        self.refresh_active_displays_list()
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
             QMessageBox.information(self, "Update", "Parameter definitions have been updated.")
    def update_control_states(self):
        has_params = bool(self.parameters)
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
            self.stream_status_label.setText("● Awaiting Parameters")
            self.stream_status_label.setStyleSheet("color: #FFBF00;")
        elif self.simulator and not self.simulator._is_paused:
            self.stream_status_label.setText("● STREAMING")
            self.stream_status_label.setStyleSheet("color: #01FF70;")
        else:
            self.stream_status_label.setText("● PAUSED")
            self.stream_status_label.setStyleSheet("color: #FF3131;")
    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
        if not path: return
        try:
            layout_data = {}
            for index, tab_info in self.tab_data.items():
                tab_name = self.tab_widget.tabText(index)
                state = tab_info['mainwindow'].saveState()
                layout_data[tab_name] = {
                    'state': base64.b64encode(state.data()).decode('utf-8'),
                    'configs': tab_info['configs']
                }
            project_data = {'parameters': self.parameters, 'layout': layout_data}
            with open(path, 'w') as f: json.dump(project_data, f, indent=4)
            QMessageBox.information(self, "Success", "Project saved successfully.")
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "JSON Files (*.json)")
        if not path: return
        try:
            with open(path, 'r') as f: project_data = json.load(f)
            self.parameters = project_data.get('parameters', [])
            self.data_history.clear()
            while self.tab_widget.count() > 0: self.close_tab(0)
            layout_data = project_data.get('layout', {})
            for tab_name, tab_layout_data in layout_data.items():
                index = self.add_new_tab(name=tab_name)
                for widget_id, config in tab_layout_data.get('configs', {}).items():
                    self.add_widget_to_dashboard(config, index, widget_id)
                state_data = base64.b64decode(tab_layout_data['state'])
                self.tab_data[index]['mainwindow'].restoreState(QByteArray(state_data))
            QMessageBox.information(self, "Success", "Project loaded successfully.")
            self.restart_simulator()
            self.update_control_states()
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QDialog { background-color: #1e1e1e; color: #d4d4d4; }
            QDockWidget { background-color: #252526; titlebar-close-icon: url(close.png); titlebar-normal-icon: url(float.png); }
            QDockWidget::title { background-color: #333333; padding: 4px; border-radius: 4px; }
            QGroupBox { border: 1px solid #444444; margin-top: 1em; padding: 0.5em; border-radius: 5px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; background-color: #1e1e1e; }
            QPushButton { background-color: #0078D7; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #0088F7; } QPushButton:pressed { background-color: #006AC7; }
            QPushButton#AddWidgetButton { background-color: #1c9c4f; }
            QPushButton#AddWidgetButton:hover { background-color: #21b35a; }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox { background-color: #3c3c3c; border: 1px solid #555555; border-radius: 4px; padding: 4px; }
            QTableWidget { background-color: #2a2a2a; gridline-color: #444444; }
            QHeaderView::section { background-color: #333333; border: 1px solid #444444; padding: 4px; }
            QListWidget { background-color: #2a2a2a; border-radius: 4px; }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { background: #252526; border: 1px solid #444; padding: 6px; border-bottom: none; }
            QTabBar::tab:selected { background: #333333; }
        """)

# --- 4. APPLICATION EXECUTION ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())