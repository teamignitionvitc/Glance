
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
# File:        widgets.py
# Author:      Ramzy
# Created On:  <Date>
#
# @brief       Dashboard display widgets for telemetry visualization.
# @details     Provides reusable PySide6 widgets for displaying telemetry data, including value cards,
#              time graphs, log tables, gauges, histograms, LED indicators, and map views. Enables
#              interactive and real-time visualization of sensor and telemetry parameters.
###################################################################################################
# HISTORY:
#
#       +----- (NEW | MODify | ADD | DELete)
#       |
# No#   |       when       who                  what
######+*********+**********+********************+**************************************************
# 000  NEW      <Date>      Ramzy               Initial creation
####################################################################################################



from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QTableWidget, QHeaderView, QAbstractItemView, QGroupBox, QHBoxLayout, QTableWidgetItem, QComboBox, QPushButton, QApplication, QMessageBox, QDoubleSpinBox, QDockWidget
from PySide6.QtGui import QFont, QColor, QBrush
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import Qt, Signal, QUrl,QTimer
import time
import math
import numpy as np
import pyqtgraph as pg

# Optional: Map widget using QWebEngineView if available
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
except Exception:
    QWebEngineView = None

class ClosableDock(QDockWidget):
    """Custom QDockWidget that emits a signal only when the close button is clicked."""
    closed = Signal(str)# will emit the widget_id when closed

    def __init__(self, title, parent=None, widget_id=None):
        super().__init__(title, parent)
        self.widget_id = widget_id

    def closeEvent(self, event):
        #Emit the closed signal only when the dock's X button is clicked.
        if self.widget_id is not None:
            self.closed.emit(self.widget_id)
        event.accept()


class ValueCard(QFrame):
    def __init__(self, param_name, unit, priority):
        super().__init__()
        self.param_name = param_name
        self.unit = unit
        self.priority = priority
        
        # Clean, frameless container
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(4)
        
        # Parameter name - top
        self.name_label = QLabel(param_name)
        self.name_label.setFont(QFont("Arial", 11))
        self.name_label.setStyleSheet("color: #999999;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Main value - huge and centered
        self.value_label = QLabel("---")
        value_font = QFont("Arial", 70, QFont.Weight.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("color: #ffffff; padding: 20px 0px;")
        
        # Unit - small, right below value
        self.unit_label = QLabel(unit)
        self.unit_label.setFont(QFont("Arial", 14))
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setStyleSheet("color: #666666;")
        
        # Add to layout
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)
        layout.addStretch()
        
        # Set base style
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 8px;
            }
        """)
        
        # Minimum size
        self.setMinimumSize(240, 200)
        self.setMaximumHeight(280)
    
    def update_value(self, value, alarm_state):
        if value is not None:
            # Smart formatting
            if abs(value) >= 1000:
                display_value = f"{value:,.1f}"
            elif abs(value) >= 100:
                display_value = f"{value:.1f}"
            elif abs(value) >= 10:
                display_value = f"{value:.2f}"
            elif abs(value) >= 1:
                display_value = f"{value:.2f}"
            else:
                display_value = f"{value:.3f}"
            
            self.value_label.setText(display_value)
            
            # Color based on state
            if alarm_state == 'Critical':
                value_color = '#ff4757'
                bg_color = '#1e1e1e'
            elif alarm_state == 'Warning':
                value_color = '#ffa502'
                bg_color = '#1e1e1e'
            else:
                value_color = '#ffffff'
                bg_color = '#1e1e1e'

            self.value_label.setStyleSheet(f"color: {value_color}; padding: 20px 0px;")
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border-radius: 8px;
                }}
            """)
        else:
            self.value_label.setText("--")
            self.value_label.setStyleSheet("color: #555555; padding: 20px 0px;")
        
        self.set_alarm_state(alarm_state)
    
    def set_alarm_state(self, state):
        # Just update the internal state, visual already handled in update_value
        pass

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
                """)
            elif v >= t.get('high_warn', 75):
                # Warning - yellow
                self.led.setStyleSheet("""
                    border-radius: 20px; 
                    background: #ffbf00; 
                    border: 3px solid #ffcc33;
                """)
            elif v >= t.get('low_warn', 25):
                # Normal - green
                self.led.setStyleSheet("""
                    border-radius: 20px; 
                    background: #21b35a; 
                    border: 3px solid #4ade80;
                """)
            else:
                # Low - blue
                self.led.setStyleSheet("""
                    border-radius: 20px; 
                    background: #0078ff; 
                    border: 3px solid #3b82f6;
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

        # Clean parameter names (kept if you want to show them somewhere)
        lat_name = param_configs[0]['name'].replace('GPS(', '').replace(')', '') \
            if param_configs[0]['name'].startswith('GPS(') else param_configs[0]['name']
        lon_name = param_configs[1]['name'].replace('GPS(', '').replace(')', '') \
            if param_configs[1]['name'].startswith('GPS(') else param_configs[1]['name']

        # Coordinates display (hidden when web map is available)
        self.coords_label = QLabel("No GPS data")
        self.coords_label.setFont(QFont("Monospace", 10))
        self.coords_label.setStyleSheet("color: #aaaaaa; padding: 4px;")
        self.coords_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coords_label.hide() 

        self._last_lat = None
        self._last_lon = None
        self._last_sent_lat = None
        self._last_sent_lon = None

        # --- NEW: online state + network manager for periodic checks ---
        self._online = None  # None = unknown, True/False once determined
        self._nam = QNetworkAccessManager(self)
        self._net_reply = None

        if QWebEngineView:
            self.web = QWebEngineView()
            self.web.setMinimumHeight(200)
            layout.addWidget(self.web)

            # Factor the HTML into a method so we can reload it on reconnect
            self._offline_html = """
            <html>
            <body style='background:#1e1e1e;color:#ff6666;
            font-family:sans-serif;text-align:center;padding:50px;'>
            Unable to load map.<br>
            Please check your internet connection.
            </body>
            </html>
            """

            self._map_html = """
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
                  .leaflet-control-attribution {
                    font-size: 10px; opacity: 0.35; background: rgba(0,0,0,0.25); color: #ddd;
                  }
                  .leaflet-control-attribution:hover { opacity: 0.85; }
                  .leaflet-bar a.magnifier-btn {
                    font-size: 16px; line-height: 26px; text-align: center; width: 26px; height: 26px;
                    display: block; text-decoration: none; background: #fff; color: #000;
                  }
                  .leaflet-bar a.magnifier-btn:hover { background: #f4f4f4; }
                  #coordsOverlay {
                    position: absolute; bottom: 8px; left: 8px; z-index: 1000;
                    background: rgba(0, 0, 0, 0.55); color: #eee; padding: 4px 8px; border-radius: 6px;
                    font-family: monospace; font-size: 12px; pointer-events: none;
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

                    const tiles = L.tileLayer(
                      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                        maxZoom: 19, maxNativeZoom: 19,
                        attribution: 'Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community'
                      }
                    );
                    tiles.addTo(map);

                    const maxAvailableZoom = tiles.options.maxNativeZoom || tiles.options.maxZoom || 19;
                    const MAX_SAFE_ZOOM = Math.min(maxAvailableZoom, 17);

                    const rocketIcon = L.divIcon({ className: 'rocket-icon', html: '<span>🚀</span>', iconSize: [28,28], iconAnchor: [14,14] });
                    const marker = L.marker([initialLat, initialLon], { icon: rocketIcon }).addTo(map);
                    const pathLine = L.polyline([], { color: 'red', weight: 3, opacity: 0.9 }).addTo(map);

                    function setOverlay(lat, lon) {
                      const el = document.getElementById('coordsOverlay');
                      if (el) { el.textContent = `Lat: ${lat.toFixed(6)}, Lon: ${lon.toFixed(6)}`; }
                    }

                    const focusControl = L.control({ position: 'topleft' });
                    focusControl.onAdd = function(map) {
                      const container = L.DomUtil.create('div', 'leaflet-bar');
                      const btn = L.DomUtil.create('a', 'magnifier-btn', container);
                      btn.href = '#'; btn.title = 'Zoom to rocket'; btn.innerHTML = '🔍';
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
                      pathLine.addLatLng(ll);
                      setOverlay(lat, lon);
                      const desiredZoom = Math.max(map.getZoom(), 16);
                      const targetZoom = Math.min(desiredZoom, MAX_SAFE_ZOOM);
                      map.setView(ll, targetZoom, { animate: true });
                    };
                  </script>
                </body>
                </html>
            """

            # Methods to load/show content ------------------------------------
            def _verify_leaflet_loaded():
                if not self.web:
                    return
                try:
                    self.web.page().runJavaScript(
                        "typeof L !== 'undefined' && typeof updatePosition === 'function';",
                        _handle_leaflet_check
                    )
                except Exception:
                    _show_offline_message()

            def _handle_leaflet_check(result):
                if result is True:
                    self._online = True
                    # map is good; hide top label
                    self.coords_label.setVisible(False)
                else:
                    _show_offline_message()

            def _load_map_html():
                # Reset "sent" latch so we push fresh coords after reload
                self._last_sent_lat = None
                self._last_sent_lon = None
                self.web.setHtml(self._map_html, baseUrl=QUrl("https://local/"))
                QTimer.singleShot(3000, _verify_leaflet_loaded)

            def _show_offline_message():
                self._online = False
                if not self.web:
                    return
                self.web.setHtml(self._offline_html)
                # If you want, you can also show coords_label when offline:
                self.coords_label.setVisible(False)

            # Expose helpers on self so we can call them from other methods
            self._load_map_html = _load_map_html
            self._show_offline_message = _show_offline_message
            self._verify_leaflet_loaded = _verify_leaflet_loaded

            # Initial attempt: we'll let the connectivity timer decide what to show
            # (so we don't flash map then error immediately)
            self._show_offline_message()

            # Prepare throttled updates every 10 seconds (fixed from 20s)
            self._update_timer = QTimer(self)
            self._update_timer.setInterval(10000)   # 10 seconds
            self._update_timer.timeout.connect(self._push_position)
            self._update_timer.start()

            # --- NEW: periodic connectivity checker (every 10s) ---------------
            self._net_timer = QTimer(self)
            self._net_timer.setInterval(10000)
            self._net_timer.timeout.connect(self._check_connectivity)
            self._net_timer.start()
            self._check_connectivity()  # kick off immediately

        else:
            self.web = None
            self.fallback = QLabel("WebEngine not available.\nShowing coordinates only.")
            self.fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fallback.setStyleSheet("color: #ffaa00; padding: 20px;")
            layout.addWidget(self.fallback)

        # Frame style
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
            border: 2px solid #333;
        """)

    # --- NEW: connectivity probing with QNetworkAccessManager -----------------
    def _check_connectivity(self):
        # Cancel any in-flight probe to avoid piling up
        if self._net_reply is not None:
            try:
                if not self._net_reply.isFinished():
                    self._net_reply.abort()
            except Exception:
                pass
            self._net_reply.deleteLater()
            self._net_reply = None

        # Use a tiny endpoint designed for connectivity checks (returns 204)
        req = QNetworkRequest(QUrl("https://www.gstatic.com/generate_204"))
        # Follow redirects if any  (Not supported on all PySide6)
        # req.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)

        self._net_reply = self._nam.get(req)
        self._net_reply.finished.connect(self._on_connectivity_reply)

    def _on_connectivity_reply(self):
        ok = False
        try:
            if self._net_reply.error() == QNetworkReply.NetworkError.NoError:
                status = self._net_reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
                if status is None:
                    ok = True
                else:
                    code = int(status)
                    ok = (200 <= code < 400) or (code == 204)
        except Exception:
            ok = False
        finally:
            self._net_reply.deleteLater()
            self._net_reply = None

        # Transition handling
        if ok:
            if not self._online:
                # came online -> load the map html and verify
                if self.web:
                    self._load_map_html()
            else:
                # already online -> optionally re-verify Leaflet (cheap)
                if self.web:
                    self._verify_leaflet_loaded()
        else:
            if self._online or self._online is None:
                # went offline (or unknown -> offline)
                if self.web:
                    self._show_offline_message()

    # -------------------------------------------------------------------------
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
        if not self.web:
            return
        if self._last_lat is None or self._last_lon is None:
            return
        if self._last_sent_lat == self._last_lat and self._last_sent_lon == self._last_lon:
            return
        # Only try to talk to the page if we believe we're online
        if self._online:
            try:
                self.web.page().runJavaScript(f"updatePosition({self._last_lat}, {self._last_lon});")
                self._last_sent_lat = self._last_lat
                self._last_sent_lon = self._last_lon
            except Exception:
                # If this fails (e.g., page not ready), force a re-verify soon
                QTimer.singleShot(1500, self._verify_leaflet_loaded)
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

