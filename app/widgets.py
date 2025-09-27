from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QTableWidget, QHeaderView, QAbstractItemView, QGroupBox, QHBoxLayout, QTableWidgetItem, QComboBox
from PySide6.QtGui import QFont, QColor, QBrush
from PySide6.QtCore import Qt
import time
import math
import numpy as np
import pyqtgraph as pg

# Optional: Map widget using QWebEngineView if available
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
except Exception:
    QWebEngineView = None


class ValueCard(QFrame):
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
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Data Point Selected", f"Parameter: {name}\nValue: {val:.3f}\nTimestamp: {time_str}")


class LogTable(QWidget):
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
        from PySide6.QtWidgets import QDoubleSpinBox
        self.search_value_spinbox = QDoubleSpinBox(); self.search_value_spinbox.setRange(-1e9, 1e9); self.search_value_spinbox.setDecimals(4)
        from PySide6.QtWidgets import QPushButton
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
            from PySide6.QtWidgets import QMessageBox
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
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Search", f"No value matching '{condition} {target_val}' found for '{target_p_name}'.")


class GaugeWidget(QFrame):
    def __init__(self, param_config):
        super().__init__()
        self.param = param_config
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Clean parameter name
        clean_name = param_config['name'].replace('GPS(', '').replace(')', '') if param_config['name'].startswith('GPS(') else param_config['name']
        
        # Title with icon
        title_layout = QHBoxLayout()
        icon_label = QLabel("Target")
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
        
        # Value display
        self.value_lbl = QLabel("--")
        value_font = QFont("Monospace", 32, QFont.Weight.Bold)
        value_font.setStyleStrategy(QFont.PreferAntialias)
        self.value_lbl.setFont(value_font)
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_lbl.setStyleSheet("color: #00ff88; padding: 8px;")
        
        # Gauge bar
        self.bar = pg.PlotWidget()
        self.bar.setFixedHeight(140)
        self.bar.setBackground(QColor(20, 20, 20))
        self.bar.hideAxis('left')
        self.bar.hideAxis('bottom')
        self.bar.setMenuEnabled(False)
        self.bar.setYRange(0, 100, padding=0)
        self.bar.setXRange(0, 100, padding=0)
        
        # Color regions
        self.low_region = pg.LinearRegionItem(values=(0, 25), brush=(255, 49, 49, 80))
        self.warn_region = pg.LinearRegionItem(values=(25, 75), brush=(255, 191, 0, 60))
        self.high_region = pg.LinearRegionItem(values=(75, 100), brush=(28, 156, 79, 80))
        
        for reg in [self.low_region, self.warn_region, self.high_region]:
            reg.setZValue(-10)
            reg.setMovable(False)
            self.bar.addItem(reg)
        
        # Indicator line
        self.indicator = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen('#00BFFF', width=4))
        self.bar.addItem(self.indicator)
        
        layout.addLayout(title_layout)
        layout.addWidget(self.value_lbl)
        layout.addWidget(self.bar)
        
        # Set frame style
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
            border: 2px solid #333;
        """)
    
    def update_value(self, value):
        try:
            self.value_lbl.setText(f"{float(value):.2f}")
        except Exception:
            self.value_lbl.setText("--")
        
        # Normalize gauge range based on thresholds
        t = self.param.get('threshold', {'low_crit': 0, 'low_warn': 25, 'high_warn': 75, 'high_crit': 100})
        lo = float(t.get('low_crit', 0))
        hi = float(t.get('high_crit', 100))
        val = float(value) if value is not None else lo
        span = max(1e-6, hi - lo)
        x = max(0.0, min(1.0, (val - lo) / span)) * 100.0
        self.indicator.setPos(x)


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
        bins = np.histogram(values, bins=20)
        self.bar_item.setOpts(x=bins[1][:-1], height=bins[0])


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


class MapWidget(QWidget):
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs
        if len(param_configs) != 2:
            lbl = QLabel("Map requires [Lat, Lon] parameters")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout = QVBoxLayout(self)
            layout.addWidget(lbl)
            return
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Title
        lat_name = param_configs[0]['name'].replace('GPS(', '').replace(')', '') if param_configs[0]['name'].startswith('GPS(') else param_configs[0]['name']
        lon_name = param_configs[1]['name'].replace('GPS(', '').replace(')', '') if param_configs[1]['name'].startswith('GPS(') else param_configs[1]['name']
        
        # Title with icon
        title_layout = QHBoxLayout()
        icon_label = QLabel("Map")
        icon_label.setFont(QFont("Arial", 14))
        self.title = QLabel(f"{lat_name} + {lon_name}")
        self.title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #ffffff;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        
        # Coordinates display
        self.coords_label = QLabel("Lat: -- | Lon: --")
        self.coords_label.setFont(QFont("Monospace", 10))
        self.coords_label.setStyleSheet("color: #aaaaaa;")
        self.coords_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(title_layout)
        layout.addWidget(self.coords_label)
        
        # Map view
        if QWebEngineView is not None:
            self.web_view = QWebEngineView()
            self.web_view.setFixedHeight(300)
            layout.addWidget(self.web_view)
            
            # Initial map
            self.update_map(0.0, 0.0)
        else:
            # Fallback: simple text display
            self.fallback = QLabel("WebEngine not available\nMap display disabled")
            self.fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fallback.setStyleSheet("color: #ff6666; font-size: 14px;")
            layout.addWidget(self.fallback)
        
        # Set frame style
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
            border: 2px solid #333;
        """)
    
    def update_position(self, history):
        lat_param = self.param_configs[0]['id']
        lon_param = self.param_configs[1]['id']
        
        if lat_param in history and lon_param in history:
            lat_hist = history[lat_param]
            lon_hist = history[lon_param]
            
            if lat_hist and lon_hist:
                lat = lat_hist[-1]['value']
                lon = lon_hist[-1]['value']
                self.coords_label.setText(f"Lat: {lat:.6f}° | Lon: {lon:.6f}°")
                
                if hasattr(self, 'web_view'):
                    self.update_map(lat, lon)
                elif hasattr(self, 'fallback'):
                    self.fallback.setText(f"Lat: {lat:.6f}°\nLon: {lon:.6f}°")
    
    def update_map(self, lat, lon):
        if not hasattr(self, 'web_view'):
            return
        
        # Simple OpenStreetMap embed
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ margin: 0; padding: 0; }}
                #map {{ width: 100%; height: 100%; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Simple map display using OpenStreetMap
                var mapDiv = document.getElementById('map');
                mapDiv.innerHTML = `
                    <iframe 
                        width="100%" 
                        height="100%" 
                        frameborder="0" 
                        scrolling="no" 
                        marginheight="0" 
                        marginwidth="0" 
                        src="https://www.openstreetmap.org/export/embed.html?bbox=${lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}&layer=mapnik&marker={lat},{lon}"
                    ></iframe>
                `;
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html)


