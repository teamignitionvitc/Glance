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
    QSizePolicy, QInputDialog, QMessageBox, QTabBar, QAbstractItemView
)
from PySide6.QtCore import QThread, Signal, Qt, QTimer, QByteArray
from PySide6.QtGui import QFont, QColor, QBrush
import pyqtgraph as pg
import numpy as np

# --- 1. DATA SIMULATOR & WIDGETS ---

class DataSimulator(QThread):
    # (Unchanged)
    newData = Signal(dict)
    def __init__(self, parameters): super().__init__(); self.parameters = parameters; self._is_running = True; self._is_paused = False
    def run(self):
        param_indices = {param['id']: i for i, param in enumerate(self.parameters)}
        while self._is_running:
            if not self._is_paused:
                packet = {}; timestamp = time.time()
                for param in self.parameters:
                    if random.random() > 0.02:
                        idx = param_indices.get(param['id'], 0); value = 50 + 40 * math.sin(timestamp / (10 + idx % 5) + idx)
                        if random.random() > 0.95: value = random.uniform(-10, 120)
                        packet[param['id']] = value
                if packet: self.newData.emit(packet)
            time.sleep(0.1)
    def toggle_pause(self): self._is_paused = not self._is_paused; return self._is_paused
    def stop(self): self._is_running = False

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

# --- MODIFIED & ENHANCED WIDGET ---
class TimeGraph(QWidget):
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
        # --- NEW: Interactivity Features ---
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
                self.last_known_values[param_id] = param_history[-1] # Store last value
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
        if evt.double(): return # Ignore double clicks
        pos = self.plot_widget.getPlotItem().vb.mapSceneToView(evt.scenePos())
        min_dist = float('inf'); nearest_point = None
        for pid, curve in self.curves.items():
            x_data, y_data = curve.getData()
            if x_data is None or len(x_data) == 0: continue
            # Simple distance check, could be more sophisticated
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

# --- NEW & ENHANCED WIDGET ---
class LogTable(QWidget):
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs
        self.param_map = {p['id']: {'name': p['name'], 'col': i + 1} for i, p in enumerate(self.param_configs)}
        self.last_known_values = {}
        self.highlight_brush = QBrush(QColor("#0078FF").lighter(150))
        # Main Layout
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0)
        # Table Widget
        self.table = QTableWidget()
        headers = ["Timestamp"] + [f"{p['name']} ({p['unit']})" for p in self.param_configs]
        self.table.setColumnCount(len(headers)); self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Search Controls
        search_group = QGroupBox("Search and Highlight")
        search_layout = QHBoxLayout(search_group)
        self.search_param_combo = QComboBox(); self.search_param_combo.addItems([p['name'] for p in self.param_configs])
        self.search_cond_combo = QComboBox(); self.search_cond_combo.addItems(["=", ">", "<", ">=", "<="])
        self.search_value_spinbox = QDoubleSpinBox(); self.search_value_spinbox.setRange(-1e9, 1e9); self.search_value_spinbox.setDecimals(4)
        search_btn = QPushButton("Search Last"); clear_btn = QPushButton("Clear")
        search_layout.addWidget(QLabel("Find in:")); search_layout.addWidget(self.search_param_combo)
        search_layout.addWidget(self.search_cond_combo); search_layout.addWidget(self.search_value_spinbox)
        search_layout.addWidget(search_btn); search_layout.addWidget(clear_btn)
        # Add to main layout
        layout.addWidget(self.table); layout.addWidget(search_group)
        search_btn.clicked.connect(self.search_and_highlight)
        clear_btn.clicked.connect(self.clear_highlights)

    def update_data(self, updated_param_id, history):
        if self.table.rowCount() > 500: self.table.removeRow(500) # Limit table size
        self.table.insertRow(0)
        # Update last known values for all tracked parameters
        for pid in self.param_map.keys():
            if pid in history and history[pid]: self.last_known_values[pid] = history[pid][-1]
        # Set timestamp from the parameter that triggered this update
        ts_str = time.strftime('%H:%M:%S', time.localtime(self.last_known_values[updated_param_id]['timestamp']))
        self.table.setItem(0, 0, QTableWidgetItem(ts_str))
        # Populate all columns with the most recent data
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
        # Iterate backwards to find the LAST instance
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
                    break # Stop after finding the last one
            except ValueError:
                continue # Ignore non-numeric cells
        if found_item:
            self.table.scrollToItem(found_item, QAbstractItemView.ScrollHint.PositionAtCenter)
        else:
            QMessageBox.information(self, "Search", f"No value matching '{condition} {target_val}' found for '{target_p_name}'.")

# --- 2. DIALOGS ---

# --- MODIFIED & ENHANCED DIALOG ---
class AddWidgetDialog(QDialog):
    def __init__(self, parameters, parent=None):
        super().__init__(parent); self.setWindowTitle("Add Display Widget")
        self.parameters = parameters
        layout = QFormLayout(self)
        # --- NEW: Sensor Grouping ---
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
            self.priority_combo.setEnabled(False) # Priority border only makes sense for single-value cards

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

# --- MODIFIED & ENHANCED DIALOG ---
class ParameterEntryDialog(QDialog):
    def __init__(self, param=None, existing_ids=None, parent=None):
        super().__init__(parent); self.existing_ids = existing_ids or []; self.is_edit_mode = param is not None
        self.setWindowTitle("Edit Parameter" if self.is_edit_mode else "Add New Parameter"); layout = QFormLayout(self)
        self.id_edit = QLineEdit(param['id'] if param else "");
        if self.is_edit_mode: self.id_edit.setReadOnly(True)
        self.name_edit = QLineEdit(param['name'] if param else "")
        # --- NEW: Sensor Group field ---
        self.group_edit = QLineEdit(param.get('sensor_group', '') if param else "")
        self.unit_edit = QLineEdit(param['unit'] if param else ""); self.desc_edit = QLineEdit(param.get('description', '') if param else "")
        self.low_crit, self.low_warn, self.high_warn, self.high_crit = QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox()
        for spin in [self.low_crit, self.low_warn, self.high_warn, self.high_crit]: spin.setRange(-100000, 100000); spin.setDecimals(3)
        if param:
            t = param.get('threshold', {}); self.low_crit.setValue(t.get('low_crit', 0)); self.low_warn.setValue(t.get('low_warn', 10))
            self.high_warn.setValue(t.get('high_warn', 80)); self.high_crit.setValue(t.get('high_crit', 100))
        layout.addRow("ID (unique, no spaces):", self.id_edit); layout.addRow("Display Name:", self.name_edit)
        layout.addRow("Sensor Group (e.g. MPU6050):", self.group_edit) # New field
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
                'sensor_group': self.group_edit.text().strip(), 'unit': self.unit_edit.text().strip(),
                'description': self.desc_edit.text().strip(), 'threshold': {'low_crit': self.low_crit.value(), 'low_warn': self.low_warn.value(),
                'high_warn': self.high_warn.value(), 'high_crit': self.high_crit.value()}}

# --- MODIFIED & ENHANCED DIALOG ---
class ManageParametersDialog(QDialog):
    def __init__(self, parameters, parent=None):
        super().__init__(parent); self.setWindowTitle("Manage Telemetry Parameters"); self.parameters = parameters; self.setMinimumSize(700, 400)
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        # --- NEW: Added Sensor Group column ---
        self.table.setColumnCount(5); self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Sensor Group', 'Unit', 'Description'])
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
            self.table.setItem(row, 0, QTableWidgetItem(p['id'])); self.table.setItem(row, 1, QTableWidgetItem(p['name']))
            self.table.setItem(row, 2, QTableWidgetItem(p.get('sensor_group', '')))
            self.table.setItem(row, 3, QTableWidgetItem(p['unit'])); self.table.setItem(row, 4, QTableWidgetItem(p.get('description', '')))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    def add_parameter(self): # (Unchanged logic)
        dialog = ParameterEntryDialog(existing_ids=[p['id'] for p in self.parameters], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted: self.parameters.append(dialog.get_data()); self.refresh_table()
    def edit_parameter(self): # (Unchanged logic)
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
    def remove_parameter(self): # (Unchanged logic)
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        param_id = self.table.item(selected_rows[0].row(), 0).text()
        self.parameters[:] = [p for p in self.parameters if p['id'] != param_id]
        self.refresh_table()

# --- 3. MAIN APPLICATION WINDOW ---
class MainWindow(QMainWindow):
    # (Init and Control Dock are mostly the same, changes are in the logic methods)
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
        layout.addWidget(setup_group); layout.addWidget(project_group); layout.addWidget(tab_group); layout.addWidget(widget_group); layout.addStretch()
        control_dock.setWidget(main_control_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, control_dock)
        self.add_widget_btn.clicked.connect(self.open_add_widget_dialog); remove_display_btn.clicked.connect(self.remove_selected_display)
        add_tab_btn.clicked.connect(lambda: self.add_new_tab()); rename_tab_btn.clicked.connect(self.rename_current_tab)
        manage_params_btn.clicked.connect(self.open_manage_parameters_dialog)
        save_btn.clicked.connect(self.save_project); load_btn.clicked.connect(self.load_project)
    
    # --- MODIFIED METHOD: Added Log Table creation ---
    def add_widget_to_dashboard(self, config, tab_index, widget_id=None):
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
        elif config['displayType'] == 'Log Table': # MODIFIED
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
            else: tab_mainwindow.tabifyDockWidget(docks_list[-1], dock) # Simplified docking logic
            dock.raise_()
            tab_info['widgets'][widget_id] = widget; tab_info['docks'][widget_id] = dock; tab_info['configs'][widget_id] = config
            self.refresh_active_displays_list()

    # --- MODIFIED METHOD: New update logic for LogTable ---
    def update_data(self, packet):
        timestamp = time.time()
        for param_id, value in packet.items():
            if param_id not in self.data_history: self.data_history[param_id] = []
            self.data_history[param_id].append({'value': value, 'timestamp': timestamp})
            self.data_history[param_id] = self.data_history[param_id][-500:] # Limit history
            # Update relevant widgets
            for tab_info in self.tab_data.values():
                for widget_id, widget in tab_info['widgets'].items():
                    config = tab_info['configs'][widget_id]
                    if param_id in config['param_ids']:
                        if isinstance(widget, ValueCard):
                            param_meta = next((p for p in self.parameters if p['id'] == param_id), None)
                            if param_meta:
                                alarm_state = self.get_alarm_state(value, param_meta['threshold'])
                                widget.update_value(value, alarm_state)
                        elif isinstance(widget, TimeGraph):
                            widget.update_data(self.data_history)
                        elif isinstance(widget, LogTable):
                            # Pass the ID of the param that just updated
                            widget.update_data(param_id, self.data_history)

    # --- All other MainWindow methods are largely unchanged logic ---
    def open_add_widget_dialog(self): # (Unchanged)
        index = self.tab_widget.currentIndex()
        if index < 0: QMessageBox.warning(self, "No Tab", "No active tab to add a widget to."); return
        dialog = AddWidgetDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selection = dialog.get_selection()
            if selection: self.add_widget_to_dashboard(selection, index)
    def remove_selected_display(self): # (Unchanged)
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
    def refresh_active_displays_list(self): # (Unchanged)
        self.active_displays_list.clear(); index = self.tab_widget.currentIndex()
        if index < 0 or index not in self.tab_data: return
        tab_info = self.tab_data.get(index)
        for widget_id, config in tab_info['configs'].items():
            param_names = [p['name'] for p in self.parameters if p['id'] in config['param_ids']]
            display_name = f"{', '.join(param_names)} ({config['displayType']})"
            item = QListWidgetItem(display_name); item.setData(Qt.ItemDataRole.UserRole, widget_id)
            self.active_displays_list.addItem(item)
    def open_manage_parameters_dialog(self): # (Unchanged)
        dialog = ManageParametersDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Update", "Parameter definitions updated. Restarting data stream.")
            self.restart_simulator(); self.update_control_states()
    def restart_simulator(self): # (Unchanged)
        if self.simulator: self.simulator.stop(); self.simulator.wait()
        if self.parameters: self.simulator = DataSimulator(self.parameters); self.simulator.newData.connect(self.update_data); self.simulator.start()
    def update_control_states(self): # (Unchanged)
        has_params = bool(self.parameters)
        self.add_widget_btn.setEnabled(has_params)
        if not has_params: self.add_widget_btn.setToolTip("Define parameters in 'SYSTEM SETUP' first.")
        else: self.add_widget_btn.setToolTip("Add a new display widget to the current tab.")
    def add_new_tab(self, name=None, layout_state=None, configs=None, is_closable=True): # (Unchanged)
        if name is None:
            name, ok = QInputDialog.getText(self, "New Tab", "Enter a name for the new tab:")
            if not ok or not name: return
        tab_content = QMainWindow(); tab_content.setDockNestingEnabled(True); tab_content.setCentralWidget(QWidget())
        index = self.tab_widget.addTab(tab_content, name)
        if not is_closable: self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, None)
        self.tab_data[index] = {'mainwindow': tab_content, 'configs': {}, 'docks': {}, 'widgets': {}}
        if configs:
            for widget_id, cfg in configs.items(): self.add_widget_to_dashboard(cfg, index, widget_id)
        if layout_state: tab_content.restoreState(QByteArray(base64.b64decode(layout_state)))
        self.tab_widget.setCurrentIndex(index); self.remap_tab_data_keys()
    def save_project(self): # (Unchanged)
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Project Files (*.json)")
        if not filepath: return
        project_data = {"parameters": self.parameters, "tabs": [], "active_tab_index": self.tab_widget.currentIndex()}
        for i in range(self.tab_widget.count()):
            tab_info = self.tab_data[i]; mw = tab_info['mainwindow']
            layout_state_b64 = base64.b64encode(mw.saveState()).decode('utf-8')
            project_data["tabs"].append({"name": self.tab_widget.tabText(i), "configs": tab_info['configs'], "layout_state": layout_state_b64})
        with open(filepath, 'w') as f: json.dump(project_data, f, indent=4)
        QMessageBox.information(self, "Success", "Project saved successfully.")
    def load_project(self): # (Unchanged)
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "JSON Project Files (*.json)")
        if not filepath: return
        with open(filepath, 'r') as f: project_data = json.load(f)
        while self.tab_widget.count() > 0: self.tab_widget.removeTab(0)
        self.tab_data.clear(); self.parameters = project_data.get("parameters", [])
        for i, tab_dict in enumerate(project_data.get("tabs", [])):
            self.add_new_tab(name=tab_dict.get("name", f"Tab {i+1}"), layout_state=tab_dict.get("layout_state"), configs=tab_dict.get("configs"))
        self.tab_widget.setCurrentIndex(project_data.get("active_tab_index", 0))
        self.restart_simulator(); self.update_control_states()
    def close_tab(self, index): # (Unchanged)
        reply = QMessageBox.question(self, "Confirm Close", f"Close tab '{self.tab_widget.tabText(index)}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.tab_widget.widget(index).deleteLater(); self.tab_widget.removeTab(index)
            if index in self.tab_data: del self.tab_data[index]
            self.remap_tab_data_keys()
    def rename_current_tab(self): # (Unchanged)
        index = self.tab_widget.currentIndex();
        if index < 0: return
        old_name = self.tab_widget.tabText(index)
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new name:", QLineEdit.EchoMode.Normal, old_name)
        if ok and new_name: self.tab_widget.setTabText(index, new_name)
    def on_tab_changed(self, index): self.refresh_active_displays_list() # (Unchanged)
    def remap_tab_data_keys(self): # (Unchanged)
        new_tab_data = {}
        for i in range(self.tab_widget.count()):
            mw = self.tab_widget.widget(i)
            for old_idx, data in self.tab_data.items():
                if data['mainwindow'] is mw: new_tab_data[i] = data; break
        self.tab_data = new_tab_data; self.on_tab_changed(self.tab_widget.currentIndex())
    def toggle_pause_stream(self): # (Unchanged)
        if self.simulator: self.simulator.toggle_pause()
    def check_data_stream(self): pass # (Unchanged)
    def closeEvent(self, event): # (Unchanged)
        if self.simulator: self.simulator.stop(); self.simulator.wait()
        event.accept()
    @staticmethod
    def get_alarm_state(value, thresholds): # (Unchanged)
        if value is None or not thresholds: return 'Nominal'
        if value >= thresholds['high_crit'] or value <= thresholds['low_crit']: return 'Critical'
        if value >= thresholds['high_warn'] or value <= thresholds['low_warn']: return 'Warning'
        return 'Nominal'
    def apply_stylesheet(self): # (Unchanged)
        self.setStyleSheet("""
            QMainWindow, QDialog { background-color: #000000; } QWidget { background-color: #1a1a1a; color: #FFFFFF; font-family: Arial; }
            QLabel { background-color: transparent; } QDockWidget { color: #FFFFFF; font-weight: bold; }
            QDockWidget::title { background-color: #2a2a2a; padding: 5px; border-radius: 4px; }
            QGroupBox { font-weight: bold; border: 1px solid #555555; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; background-color: #1a1a1a; }
            QListWidget, QLineEdit, QComboBox, QDoubleSpinBox, QTableWidget { background-color: #2a2a2a; border: 1px solid #555555; border-radius: 4px; padding: 4px; }
            QListWidget::item:hover, QTableWidget::item:hover { background-color: #3a3a3a; }
            QListWidget::item:selected, QTableWidget::item:selected { background-color: #0078FF; color: white; }
            QComboBox::drop-down { border: none; } QComboBox QAbstractItemView { background-color: #2a2a2a; border: 1px solid #555555; selection-background-color: #0078FF; }
            QPushButton { background-color: #2a2a2a; border: 1px solid #0078FF; border-radius: 4px; padding: 8px 16px; color: #FFFFFF; }
            QPushButton:hover { background-color: #3c3c3c; } QPushButton:pressed { background-color: #005ECC; }
            QPushButton:disabled { background-color: #2c2c2c; border-color: #444444; color: #777777; }
            QPushButton#AddWidgetButton { background-color: #0078FF; color: white; font-weight: bold; border: none; }
            QPushButton#AddWidgetButton:hover { background-color: #005ECC; }
            QHeaderView::section { background-color: #2a2a2a; border: 1px solid #555555; padding: 4px; font-weight: bold; }
            QTableWidget { gridline-color: #555555; } QTabWidget::pane { border: none; }
            QTabBar::tab { background: #1a1a1a; color: #FFFFFF; padding: 10px 20px; border: 1px solid #555555; border-bottom: none; }
            QTabBar::tab:selected { background: #2a2a2a; border-color: #0078FF; }
            QTabBar::tab:!selected:hover { background: #3a3a3a; }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())