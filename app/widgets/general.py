
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
under the terms of the GNU General Public License as published by
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
# File:        general.py
# Author:      MuhammadRamzy
# Created On:  26-09-2025
#
# @brief       Dashboard display widgets for telemetry visualization.
# @details     Provides reusable PySide6 widgets for displaying telemetry data, including value cards,
#              time graphs, log tables, gauges, histograms, LED indicators, and map views. Enables
#              interactive and real-time visualization of sensor and telemetry parameters.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      26-09-2025  MuhammadRamzy        First commit with the ui/ux and flow changes
# 001  MOD      27-09-2025  MuhammadRamzy        Stream Fix
# 002  MOD      09-10-2025  MuhammadRamzy        Formatting
# 003  MOD      12-10-2025  MuhammadRamzy        modularized main.py into widget.py
# 004  MOD      13-10-2025  oslowtech            Fixed Dashboard creation failed.
# 005  MOD      30-10-2025  Shawn                Fixed issue where close button hides widget instead of actually closing it, changed comment type
# 006  MOD      06-11-2025  Shawn                Fixed map issue on no wifi, fixed minor bugs with the map
# 007  MOD      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side layout and QStackedWidget
# 008  MOD      29-11-2025  NeilBaranwal9        feat: Fixed TimeGraph crash on high-frequency data
####################################################################################################



from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QTableWidget, QHeaderView, QAbstractItemView, QGroupBox, QHBoxLayout, QTableWidgetItem, QComboBox, QPushButton, QApplication, QMessageBox, QDoubleSpinBox, QDockWidget, QGridLayout, QGraphicsDropShadowEffect, QLayout, QSizePolicy, QStyle
from PySide6.QtGui import QFont, QColor, QBrush, QLinearGradient, QConicalGradient, QPainter, QPen, QPainterPath, QIcon
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import Qt, Signal, QUrl, QTimer, QRectF, QPoint, QSize, QRect

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, hSpacing=-1, vSpacing=-1):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._hSpace = hSpacing
        self._vSpace = vSpacing
        self._itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._itemList.append(item)

    def horizontalSpacing(self):
        if self._hSpace >= 0:
            return self._hSpace
        else:
            return self.smartSpacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vSpace >= 0:
            return self._vSpace
        else:
            return self.smartSpacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._itemList)

    def itemAt(self, index):
        if 0 <= index < len(self._itemList):
            return self._itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._itemList):
            return self._itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().left(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(+left, +top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        
        # Pass 1: Group items into lines
        lines = []
        current_line = []
        current_line_width = 0
        
        for item in self._itemList:
            wid = item.widget()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and current_line:
                # Finish current line
                lines.append((current_line, current_line_width, lineHeight))
                
                # Start new line
                x = effectiveRect.x()
                lineHeight = 0
                current_line = []
                current_line_width = 0
                nextX = x + item.sizeHint().width() + spaceX

            current_line.append(item)
            current_line_width += item.sizeHint().width() + spaceX
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
            
        # Append last line
        if current_line:
            lines.append((current_line, current_line_width, lineHeight))

        # Pass 2: Place items (Centered)
        y = effectiveRect.y()
        for line_items, line_width, line_height in lines:
            # Calculate starting X to center the line
            # Remove trailing spacing from line_width for accurate centering
            actual_width = line_width - self.horizontalSpacing()
            start_x = effectiveRect.x() + (effectiveRect.width() - actual_width) / 2
            
            x = start_x
            for item in line_items:
                if not testOnly:
                    item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
                
                x += item.sizeHint().width() + self.horizontalSpacing()
            
            y += line_height + self.verticalSpacing()

        return y - rect.y() + bottom
    
    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
import time
import math
import numpy as np
import pyqtgraph as pg

# Optional: Map widget using QWebEngineView if available
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
except Exception:
    QWebEngineView = None

class CustomTitleBar(QWidget):
    """
    @brief Custom title bar for ClosableDock.
    """
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.dock = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("SF Pro Text", 10, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #cccccc;")
        
        # Close Button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #aaaaaa;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 48, 0.8); /* Apple Red */
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self._on_close_clicked)
        
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.close_btn)
        
        # Transparent background initially
        self.setStyleSheet("background: transparent;")
        self.setFixedHeight(32) # Ensure it has height to be grabbed
        
        # Initial state: hidden content
        self.title_label.hide()
        self.close_btn.hide()
        
    def set_active(self, active):
        """Toggle visibility of title bar content"""
        if active:
            self.title_label.show()
            self.close_btn.show()
            self.setStyleSheet("background-color: rgba(30, 30, 30, 0.9); border-bottom: 1px solid rgba(255,255,255,0.1);")
        else:
            self.title_label.hide()
            self.close_btn.hide()
            self.setStyleSheet("background: transparent;")
        
    def _on_close_clicked(self):
        if self.dock:
            self.dock.closeEvent(None) # Trigger close logic

class ClosableDock(QDockWidget):
    """
    @brief Custom QDockWidget that emits a signal only when the close button is clicked.
    @details Used for widgets that can be closed/hidden from the dashboard layout.
             Implements hover-only header visibility.
    """
    closed = Signal(str)  # will emit the widget_id when closed
    edit_requested = Signal(str)  # will emit the widget_id when edit is requested

    def __init__(self, title, parent=None, widget_id=None):
        super().__init__(title, parent)
        self.widget_id = widget_id
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Custom Title Bar
        self.custom_title_bar = CustomTitleBar(title, self)
        self.setTitleBarWidget(self.custom_title_bar)
        
        # Enable mouse tracking for hover
        self.setMouseTracking(True)
        
    def enterEvent(self, event):
        """Show title bar content on hover"""
        self.custom_title_bar.set_active(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Hide title bar content when mouse leaves"""
        # Only hide if not interacting with the title bar (optional refinement)
        self.custom_title_bar.set_active(False)
        super().leaveEvent(event)

    def show_context_menu(self, pos):
        """Show context menu for widget"""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        
        edit_action = QAction("Edit Widget", self)
        edit_action.triggered.connect(lambda: self._emit_edit_signal())
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        remove_action = QAction("Remove Widget", self)
        remove_action.triggered.connect(lambda: self.closed.emit(self.widget_id))
        menu.addAction(remove_action)
        
        menu.exec(self.mapToGlobal(pos))
    
    def _emit_edit_signal(self):
        """Emit edit signal"""
        self.edit_requested.emit(self.widget_id)

    def closeEvent(self, event):
        #Emit the closed signal only when the dock's X button is clicked.
        if self.widget_id is not None:
            self.closed.emit(self.widget_id)
        if event:
            event.accept()


class ValueCard(QFrame):
    """
    @brief Widget for displaying multiple scalar values in a grid (Value Panel).
    @details Shows parameter names, values, and units for a list of parameters.
    """
    def __init__(self, param_configs, priority=None):
        super().__init__()
        self.param_configs = param_configs
        self.priority = priority
        
        # Clean, frameless container
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Main layout - Responsive Flow
        self.main_layout = FlowLayout(self, margin=16, hSpacing=16, vSpacing=16)
        
        self.value_labels = {}
        
        for p_config in param_configs:
            # Container for each value - Clean, Minimalist
            container = QFrame()
            # Fixed size to ensure consistent flow
            container.setFixedSize(180, 120)
            # Remove the inner box background/border for a cleaner look
            container.setStyleSheet("background: transparent; border: none;")
            
            v_layout = QVBoxLayout(container)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(4)
            v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Top: Label (Small, Uppercase)
            name_label = QLabel(p_config['name'].upper())
            name_label.setFont(QFont("SF Pro Text", 9, QFont.Weight.Medium))
            name_label.setStyleSheet("color: rgba(255, 255, 255, 0.4); letter-spacing: 0.5px;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Center: Value (Large, Bold)
            value_label = QLabel("--")
            value_label.setFont(QFont("SF Pro Display", 56, QFont.Weight.Bold)) 
            value_label.setStyleSheet("color: #ffffff;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.value_labels[p_config['id']] = value_label
            
            # Bottom: Unit (Medium)
            unit_label = QLabel(p_config.get('unit', ''))
            unit_label.setFont(QFont("SF Pro Text", 11, QFont.Weight.Normal))
            unit_label.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
            unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            v_layout.addWidget(name_label)
            v_layout.addSpacing(4)
            v_layout.addWidget(value_label)
            v_layout.addWidget(unit_label)
            
            self.main_layout.addWidget(container)
        
        # Set base style for the widget itself
        self.setStyleSheet("background: transparent;")
        
        # Minimum size
        self.setMinimumSize(240, 200)
    
    def update_values(self, values_dict):
        for pid, val in values_dict.items():
            if pid in self.value_labels:
                lbl = self.value_labels[pid]
                if val is not None:
                    # Smart formatting
                    if abs(val) >= 1000:
                        display_value = f"{val:,.1f}"
                    elif abs(val) >= 100:
                        display_value = f"{val:.1f}"
                    elif abs(val) >= 10:
                        display_value = f"{val:.2f}"
                    elif abs(val) >= 1:
                        display_value = f"{val:.2f}"
                    else:
                        display_value = f"{val:.3f}"
                    lbl.setText(display_value)
                    # Dynamic color based on value? For now keep white.
                    lbl.setStyleSheet("color: #ffffff; border: none; background: transparent;")
                else:
                    lbl.setText("--")
                    lbl.setStyleSheet("color: rgba(255, 255, 255, 0.3); border: none; background: transparent;")

class CircularGauge(QWidget):
    def __init__(self, min_val, max_val, safe_limit=None, warning_limit=None, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.safe_limit = safe_limit
        self.warning_limit = warning_limit
        self.value = min_val
        self.setMinimumSize(100, 100)
        
    def set_value(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        side = min(width, height)
        # Add padding to prevent clipping
        rect = QRectF((width - side) / 2 + 10, (height - side) / 2 + 10, side - 20, side - 20)
        
        # 1. Draw Track (Background)
        track_pen = QPen(QColor(255, 255, 255, 20), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 135 * 16, 270 * 16)
        
        # Calculate angle
        span = 270
        pct = (self.value - self.min_val) / (self.max_val - self.min_val) if (self.max_val - self.min_val) > 0 else 0
        pct = max(0, min(1, pct)) # Clamp
        angle = -pct * span
        
        # Dynamic color logic
        if self.warning_limit is not None and self.value >= self.warning_limit:
            color = QColor('#ff453a') # Red
        elif self.safe_limit is not None and self.value >= self.safe_limit:
            color = QColor('#ff9f0a') # Yellow
        else:
            # Fallback to percentage based if no limits set, or Green if safe
            if self.safe_limit is None and self.warning_limit is None:
                if pct > 0.9: color = QColor('#ff453a')
                elif pct > 0.7: color = QColor('#ff9f0a')
                else: color = QColor('#30d158')
            else:
                color = QColor('#30d158') # Green
        
        # 2. Draw Active Arc with Gradient
        # Create a conical gradient for a premium look
        grad = QConicalGradient(rect.center(), 225)
        grad.setColorAt(0, color.darker(150))
        grad.setColorAt(0.5, color)
        grad.setColorAt(1, color.lighter(130))
        
        pen = QPen(QBrush(grad), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 135 * 16, int(angle * 16))
        
        # 3. Draw Value Text
        painter.setPen(QColor(255, 255, 255))
        # Reduced font size to prevent overlap
        font = QFont("SF Pro Display", 20, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self.value:.2f}")


class LinearGauge(QWidget):
    def __init__(self, min_val, max_val, safe_limit=None, warning_limit=None, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.safe_limit = safe_limit
        self.warning_limit = warning_limit
        self.value = min_val
        self.setFixedHeight(32) # Fixed height for the bar
        
    def set_value(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        # Padding
        bar_rect = QRectF(rect.left(), rect.top() + 8, rect.width(), rect.height() - 16)
        
        # 1. Draw Track
        path = QPainterPath()
        path.addRoundedRect(bar_rect, bar_rect.height()/2, bar_rect.height()/2)
        painter.fillPath(path, QColor(255, 255, 255, 20))
        
        # 2. Draw Active Bar
        if self.max_val > self.min_val:
            pct = (self.value - self.min_val) / (self.max_val - self.min_val)
            pct = max(0, min(1, pct))
            
            active_width = bar_rect.width() * pct
            if active_width > 0:
                active_rect = QRectF(bar_rect.left(), bar_rect.top(), active_width, bar_rect.height())
                
                # Dynamic Color
                if self.warning_limit is not None and self.value >= self.warning_limit:
                    color = QColor('#ff453a')
                elif self.safe_limit is not None and self.value >= self.safe_limit:
                    color = QColor('#ff9f0a')
                else:
                    if self.safe_limit is None and self.warning_limit is None:
                        if pct > 0.9: color = QColor('#ff453a')
                        elif pct > 0.7: color = QColor('#ff9f0a')
                        else: color = QColor('#30d158')
                    else:
                        color = QColor('#30d158')
                
                # Gradient
                grad = QLinearGradient(active_rect.topLeft(), active_rect.bottomRight())
                grad.setColorAt(0, color.lighter(120))
                grad.setColorAt(1, color)
                
                active_path = QPainterPath()
                active_path.addRoundedRect(active_rect, bar_rect.height()/2, bar_rect.height()/2)
                painter.fillPath(active_path, QBrush(grad))


class LEDWidget(QFrame):
    def __init__(self, param_configs, options=None):
        super().__init__()
        self.param_configs = param_configs
        self.options = options or {}
        self.led_configs = self.options.get('led_configs', {})
        
        # Main layout - Responsive Flow
        # Reduced margins and spacing for tighter packing
        self.main_layout = FlowLayout(self, margin=8, hSpacing=8, vSpacing=8)
        
        self.leds = {}
        self.value_labels = {}
        
        for p_config in param_configs:
            # Container
            container = QFrame()
            # Reduced fixed size to allow narrower width
            container.setFixedSize(80, 90) 
            # Remove border/background
            container.setStyleSheet("background: transparent; border: none;")
            
            v_layout = QVBoxLayout(container)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(2)
            v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Clean parameter name
            clean_name = p_config['name'].replace('GPS(', '').replace(')', '') if p_config['name'].startswith('GPS(') else p_config['name']
            
            # Title
            title = QLabel(f"{clean_name}")
            title.setFont(QFont("SF Pro Text", 9, QFont.Weight.Medium))
            title.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # LED indicator (now contains value)
            led = QLabel("--")
            led.setFixedSize(40, 40) # Smaller LED
            led.setAlignment(Qt.AlignmentFlag.AlignCenter)
            led.setFont(QFont("SF Pro Display", 10, QFont.Weight.Bold))
            
            # Default inactive style
            led.setStyleSheet("""
                border-radius: 20px; 
                background: #2a2a2a; 
                border: 2px solid #444;
                color: #666;
            """)
            
            self.leds[p_config['id']] = led
            
            v_layout.addWidget(title)
            v_layout.addWidget(led, alignment=Qt.AlignmentFlag.AlignCenter)
            
            self.main_layout.addWidget(container)
        
        # Set frame style
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            
    def update_values(self, values_dict):
        for pid, val in values_dict.items():
            if pid in self.leds:
                led = self.leds[pid]
                led_conf = self.led_configs.get(pid, {})
                
                # Default colors
                active_color = led_conf.get('active_color', '#30d158') # Green
                inactive_color = led_conf.get('inactive_color', '#ff453a') # Red
                
                # Thresholds
                threshold = led_conf.get('threshold', 0.5)
                
                if val is not None:
                    led.setText(str(val)) # Display the actual value
                    if val >= threshold:
                        led.setStyleSheet(f"""
                            border-radius: 20px; 
                            background: {active_color}; 
                            border: 2px solid {QColor(active_color).lighter(150).name()};
                            color: #fff;
                        """)
                    else:
                        led.setStyleSheet(f"""
                            border-radius: 20px; 
                            background: {inactive_color}; 
                            border: 2px solid {QColor(inactive_color).lighter(150).name()};
                            color: #fff;
                        """)
                else:
                    led.setText("--")
                    led.setStyleSheet("""
                        border-radius: 20px; 
                        background: #2a2a2a; 
                        border: 2px solid #444;
                        color: #666;
                    """)

class GaugeWidget(QFrame):
    """
    @brief Gauge widget (Linear or Circular) with Cluster Support.
    """
    def __init__(self, param_configs, options=None):
        super().__init__()
        # Ensure param_configs is a list
        if isinstance(param_configs, dict):
            param_configs = [param_configs]
            
        self.options = options or {}
        self.param_configs = param_configs
        self.style = self.options.get('style', 'Linear')
        gauge_configs = self.options.get('gauge_configs', {})
        
        # Main layout - Responsive Flow
        self.main_layout = FlowLayout(self, margin=16, hSpacing=16, vSpacing=16)
        
        self.gauges = {}
        self.value_labels = {}
        
        for p_config in param_configs:
            pid = p_config['id']
            # Get specific config or defaults
            g_conf = gauge_configs.get(pid, {})
            min_val = float(g_conf.get('min', self.options.get('min_value', 0)))
            max_val = float(g_conf.get('max', self.options.get('max_value', 100)))
            safe_lim = float(g_conf.get('safe', 70)) if 'safe' in g_conf else None
            warn_lim = float(g_conf.get('warning', 90)) if 'warning' in g_conf else None
            
            # Container
            container = QFrame()
            # Fixed size based on style
            if self.style == 'Circular':
                container.setFixedSize(160, 160)
            else:
                container.setFixedSize(200, 100)
                
            container.setStyleSheet("background: transparent; border: none;")
            
            v_layout = QVBoxLayout(container)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(4)
            
            # Header (Name + Unit)
            header_layout = QHBoxLayout()
            name_lbl = QLabel(p_config['name'])
            name_lbl.setFont(QFont("SF Pro Text", 10, QFont.Weight.Medium))
            name_lbl.setStyleSheet("color: #aaaaaa;")
            
            unit_lbl = QLabel(p_config.get('unit', ''))
            unit_lbl.setFont(QFont("SF Pro Text", 10, QFont.Weight.Normal))
            unit_lbl.setStyleSheet("color: #666666;")
            
            header_layout.addWidget(name_lbl)
            header_layout.addStretch()
            header_layout.addWidget(unit_lbl)
            
            v_layout.addLayout(header_layout)
            
            if self.style == 'Circular':
                gauge = CircularGauge(min_val, max_val, safe_lim, warn_lim)
                v_layout.addWidget(gauge, alignment=Qt.AlignmentFlag.AlignCenter)
                self.gauges[pid] = gauge
            else:
                # Linear Capsule Style
                value_lbl = QLabel("--")
                value_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
                value_lbl.setFont(QFont("SF Pro Display", 28, QFont.Weight.Bold))
                value_lbl.setStyleSheet("color: #ffffff;")
                v_layout.addWidget(value_lbl)
                self.value_labels[pid] = value_lbl
                
                gauge = LinearGauge(min_val, max_val, safe_lim, warn_lim)
                v_layout.addWidget(gauge)
                self.gauges[pid] = gauge
                
            self.main_layout.addWidget(container)
        
        self.setStyleSheet("background: transparent;")

    def update_values(self, values_dict):
        for pid, val in values_dict.items():
            if pid in self.gauges:
                v = float(val) if val is not None else self.gauges[pid].min_val
                self.gauges[pid].set_value(v)
                
                if pid in self.value_labels:
                    self.value_labels[pid].setText(f"{v:.2f}")

    def update_value(self, value):
        # Legacy support / Single value update
        if self.param_configs:
            pid = self.param_configs[0]['id']
            self.update_values({pid: value})
        
class TimeGraph(QWidget):
    """
    @brief Widget for plotting parameter values over time.
    @details Supports multiple curves, zooming, panning, and value inspection via mouse hover/click.
    """
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs
        self.curves = {}
        self.last_known_values = {}
        
        # --- NEW: Buffer and Threshold Control ---
        self.latest_history = None  # Buffer to hold latest data
        self.current_y_max = 1.0    # Track the current window top
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._refresh_plot)
        self.update_timer.start(50) # Update UI every 50ms (20 FPS) to prevent crashing
        # -----------------------------------------

        # Main Layout
        container = QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)

        # Plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None) # Transparent background
        self.plot_widget.showGrid(x=True, y=True, alpha=0.1) # Very subtle grid
        self.plot_widget.setAntialiasing(True)
        self.plot_widget.setDownsampling(mode='peak')
        self.plot_widget.setClipToView(True)
        
        # Axis styling
        axis_pen = pg.mkPen(color=QColor(255, 255, 255, 80), width=1)
        self.plot_widget.getAxis('bottom').setPen(axis_pen)
        self.plot_widget.getAxis('bottom').setTextPen(QColor(255, 255, 255, 150))
        self.plot_widget.getAxis('bottom').setLabel('Time (s)', color='#aaaaaa', **{'font-family': 'SF Pro Text', 'font-size': '10pt'})
        
        self.plot_widget.getAxis('left').setPen(axis_pen)
        self.plot_widget.getAxis('left').setTextPen(QColor(255, 255, 255, 150))
        
        # Remove legend for cleaner look
        # self.plot_widget.addLegend(offset=(10, 10))
        
        # Disable AutoRange for Y so our Threshold logic takes control
        self.plot_widget.plotItem.vb.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False) 
        self.plot_widget.enableAutoRange(axis=pg.ViewBox.XAxis, enable=True)

        title = ", ".join([p['name'] for p in self.param_configs])
        units = list(set([p['unit'] for p in self.param_configs]))
        unit_label = units[0] if len(units) == 1 else "Multiple Units"
        
        # Title styling
        self.plot_widget.setTitle(title, color='#ffffff', size='11pt')
        self.plot_widget.setLabel('left', unit_label, color='#aaaaaa', **{'font-family': 'SF Pro Text', 'font-size': '10pt'})

        # Reset Button (Overlay)
        # Parent to self (TimeGraph) instead of plot_widget to avoid potential segfaults with PyQTGraph internals
        self.reset_btn = QPushButton(self)
        self.reset_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.reset_btn.setToolTip("Reset View")
        self.reset_btn.setFixedSize(32, 32)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #fff;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.reset_btn.raise_() # Ensure it's on top of the plot
        # Position in top-right corner
        self.reset_btn.move(10, 10) # Initial position, will update in resizeEvent
        self.reset_btn.clicked.connect(lambda: self.plot_widget.enableAutoRange())

        for p_config in self.param_configs:
            # Use a nice gradient fill
            # We need to define a brush that has a gradient
            color = QColor(p_config['color'])
            pen = pg.mkPen(color, width=2.5)
            
            curve = self.plot_widget.plot(pen=pen, name=p_config['name'])
            
            # Gradient fill
            # Create a gradient from the line color (semi-transparent) to transparent
            # QLinearGradient(0, 0, 0, 1) goes from top (0) to bottom (1) in ObjectBoundingMode
            # We want the top (near the line) to be opaque and bottom to be transparent.
            grad = QLinearGradient(0, 0, 0, 1)
            grad.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
            grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 100)) # Top: More opaque
            grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))   # Bottom: Transparent
            brush = QBrush(grad)
            
            curve.setFillLevel(0)
            curve.setBrush(brush)
            
            # Optimization for jitter
            curve.setDownsampling(auto=True, method='peak', ds=5) # Downsample
            self.plot_widget.setClipToView(True) # Only draw what's visible
            
            self.curves[p_config['id']] = curve

        container.addWidget(self.plot_widget)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 20, 0.9); /* Darker background */
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        
        # Initialize start time for relative plotting
        self.start_time = time.time()
        
        # Crosshairs
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('yellow', style=Qt.PenStyle.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('yellow', style=Qt.PenStyle.DashLine))
        self.label = pg.TextItem(color='white', anchor=(0, 1))
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.plot_widget.addItem(self.label)

        self.proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        self.plot_widget.scene().sigMouseClicked.connect(self.mouse_clicked)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep reset button in top-right corner
        if hasattr(self, 'reset_btn'):
            self.reset_btn.move(self.width() - 42, 10)

    def update_data(self, history):
        """
        Lightweight setter. 
        Just saves the data reference. Does NOT compute or paint.
        """
        self.latest_history = history

    def _refresh_plot(self):
        """
        Called by QTimer @ 20FPS. Handles plotting and Threshold logic.
        """
        if not self.latest_history:
            return

        global_max_val = -float('inf')
        has_data = False

        # 1. Update Curves
        for param_id, curve in self.curves.items():
            if param_id in self.latest_history and self.latest_history[param_id]:
                param_history = self.latest_history[param_id]
                self.last_known_values[param_id] = param_history[-1]
                
                timestamps = [dp['timestamp'] - self.start_time for dp in param_history]
                values = [dp['value'] for dp in param_history]
                curve.setData(x=timestamps, y=values)
                
                # Track max value for threshold logic
                if values:
                    current_max = max(values)
                    if current_max > global_max_val:
                        global_max_val = current_max
                    has_data = True

        # 2. Threshold Window Logic
        if has_data:
            # Dynamic threshold (e.g., 20% of current max to prevent jitter)
            # You can tune this multiplier.
            hysteresis_gap = self.current_y_max * 0.2 

            should_update = False
            
            # Case A: Graph goes UP -> Expand immediately
            if global_max_val > self.current_y_max:
                self.current_y_max = global_max_val * 1.1 # Add 10% headroom
                should_update = True
            
            # Case B: Graph goes DOWN -> Only shrink if we drop below (Max - Threshold)
            elif global_max_val < (self.current_y_max - hysteresis_gap):
                self.current_y_max = global_max_val * 1.1 # Reset to new max + headroom
                should_update = True

            # Apply the stable window
            if should_update:
                # We only set Y range. X range is handled by standard auto-scroll.
                self.plot_widget.setYRange(0, self.current_y_max, padding=0)

    def mouse_moved(self, evt):
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            return

        pos = evt[0]
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_widget.getPlotItem().vb.mapSceneToView(pos)
            
            # Check if mouse is within the X range of the data
            x_min, x_max = self.plot_widget.viewRange()[0]
            if mousePoint.x() < x_min or mousePoint.x() > x_max:
                self.vLine.hide()
                self.hLine.hide()
                self.label.hide()
                return
                
            self.vLine.show()
            self.hLine.show()
            self.label.show()
            
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            text = f"Time: {mousePoint.x():.2f}s\n"
            for pid, curve in self.curves.items():
                x_data, y_data = curve.getData()
                if x_data is not None and len(x_data) > 0:
                    # Find nearest point
                    idx = np.searchsorted(x_data, mousePoint.x())
                    if 0 < idx < len(x_data):
                        # Interpolate or just take nearest? Nearest is safer for raw data
                        val_left = y_data[idx-1]
                        val_right = y_data[idx]
                        # Simple nearest logic
                        if abs(x_data[idx] - mousePoint.x()) < abs(x_data[idx-1] - mousePoint.x()):
                            y_val = val_right
                        else:
                            y_val = val_left
                            
                        p_name = next(p['name'] for p in self.param_configs if p['id'] == pid)
                        text += f"{p_name}: {y_val:.2f}\n"
            self.label.setText(text.strip())
            self.label.setPos(mousePoint)
        else:
            self.vLine.hide()
            self.hLine.hide()
            self.label.hide()
            
    def leaveEvent(self, event):
        """Hide crosshair when mouse leaves the widget"""
        self.vLine.hide()
        self.hLine.hide()
        self.label.hide()
        super().leaveEvent(event)

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
    """
    @brief Widget for displaying the distribution of parameter values.
    @details Uses a bar graph to show a histogram of the data.
    """
    def __init__(self, param_config):
        super().__init__(); self.param = param_config
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,16)
        
        # Title
        title = QLabel(f"{param_config['name']}")
        title.setFont(QFont("SF Pro Text", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)
        
        self.plot = pg.PlotWidget(); self.plot.setBackground(None); self.plot.setMenuEnabled(False)
        self.plot.showGrid(x=True, y=True, alpha=0.1)
        self.plot.getAxis('bottom').setPen(pg.mkPen(color='#888888'))
        self.plot.getAxis('left').setPen(pg.mkPen(color='#888888'))
        
        self.bar_item = pg.BarGraphItem(x=[], height=[], width=0.9, brush=pg.mkBrush('#0a84ff'))
        self.plot.addItem(self.bar_item)
        layout.addWidget(self.plot)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.8);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
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
    """
    @brief Widget for displaying multiple status LEDs (LED Panel).
    @details Changes color (Green/Gray) based on value thresholds/conditions.
    """
    def __init__(self, param_configs, options=None):
        super().__init__()
        self.param_configs = param_configs
        self.options = options or {}
        self.led_configs = self.options.get('led_configs', {})
        
        # Main layout - Responsive Flow
        self.main_layout = FlowLayout(self, margin=16, hSpacing=16, vSpacing=16)
        
        self.leds = {}
        self.value_labels = {}
        
        for p_config in param_configs:
            # Container
            container = QFrame()
            container.setFixedSize(100, 100) # Compact fixed size
            # Remove border/background
            container.setStyleSheet("background: transparent; border: none;")
            
            v_layout = QVBoxLayout(container)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(4)
            v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Clean parameter name
            clean_name = p_config['name'].replace('GPS(', '').replace(')', '') if p_config['name'].startswith('GPS(') else p_config['name']
            
            # Title
            title = QLabel(f"{clean_name}")
            title.setFont(QFont("SF Pro Text", 10, QFont.Weight.Medium))
            title.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # LED indicator (now contains value)
            led = QLabel("--")
            led.setFixedSize(48, 48) # Compact size
            led.setAlignment(Qt.AlignmentFlag.AlignCenter)
            led.setFont(QFont("SF Pro Display", 12, QFont.Weight.Bold))
            
            # Default inactive style
            led.setStyleSheet("""
                border-radius: 24px; 
                background: #2a2a2a; 
                border: 2px solid #444;
                color: #666;
            """)
            
            self.leds[p_config['id']] = led
            
            v_layout.addWidget(title)
            v_layout.addWidget(led, alignment=Qt.AlignmentFlag.AlignCenter)
            
            self.main_layout.addWidget(container)
        
        # Set frame style
        self.setStyleSheet("background: transparent;")

    
    def update_values(self, data):
        for pid, led in self.leds.items():
            if pid in data:
                val = data[pid]
                
                # Handle None values
                if val is None:
                    led.setText("--")
                    led.setStyleSheet("""
                        border-radius: 24px; 
                        background: #2a2a2a; 
                        border: 2px solid #444;
                        color: #666;
                    """)
                    led.setGraphicsEffect(None)
                    continue

                led.setText(f"{val:.1f}") # Show value inside
                
                # Check thresholds
                active_color = None
                if pid in self.led_configs:
                    config = self.led_configs[pid]
                    # New format: multi-threshold with colors
                    if 'thresholds' in config and config['thresholds']:
                        thresholds = sorted(config['thresholds'], key=lambda x: x['value']) # Sort for priority
                        for threshold in thresholds:
                            t_val = float(threshold['value'])
                            cond = threshold.get('condition', '≥')
                            color = threshold['color']
                            
                            match = False
                            if cond in ['≥', '>='] and val >= t_val: match = True
                            elif cond in ['≤', '<='] and val <= t_val: match = True
                            elif cond == '>' and val > t_val: match = True
                            elif cond == '<' and val < t_val: match = True
                            elif cond == '==' and abs(val - t_val) < 0.0001: match = True
                            
                            if match:
                                active_color = color
                                break # Priority to first match (after sorting)
                    # Old format: single threshold (backward compatibility)
                    elif 'threshold' in config:
                        threshold = float(config.get('threshold', 0))
                        condition = config.get('condition', '>')
                        
                        is_active = False
                        if condition == '>': is_active = val > threshold
                        elif condition == '<': is_active = val < threshold
                        elif condition == '>=': is_active = val >= threshold
                        elif condition == '<=': is_active = val <= threshold
                        elif condition == '==': is_active = abs(val - threshold) < 0.0001
                        
                        if is_active:
                            active_color = '#21b35a' # Default green for old format
                
                if active_color:
                    # Active State with Glow
                    # Determine text color based on brightness
                    c = QColor(active_color)
                    brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
                    text_color = "#000000" if brightness > 128 else "#ffffff"
                    
                    led.setStyleSheet(f"""
                        border-radius: 24px; 
                        background-color: {active_color};
                        border: 2px solid {active_color};
                        color: {text_color};
                    """)
                    
                    # Add glow effect if not present
                    if not led.graphicsEffect():
                        glow = QGraphicsDropShadowEffect()
                        glow.setBlurRadius(20)
                        glow.setColor(QColor(active_color))
                        glow.setOffset(0, 0)
                        led.setGraphicsEffect(glow)
                    else:
                        # Update existing glow color
                        led.graphicsEffect().setColor(QColor(active_color))
                else:
                    # Inactive State
                    led.setStyleSheet("""
                        border-radius: 24px; 
                        background: #2a2a2a; 
                        border: 2px solid #444;
                        color: #666;
                    """)
                    led.setGraphicsEffect(None) # Remove glow
            else:
                # If parameter ID is not in current data, set to inactive/default
                led.setText("--")
                led.setStyleSheet("""
                    background: #3a3a3a; 
                    border: 1px solid #555;
                """)
    
    def _get_led_color(self, value, config):
        """
        Get LED color based on value and threshold configuration.
        Supports both old single-threshold and new multi-threshold formats.
        """
        if value is None:
            return None
        
        # New format: multi-threshold with colors
        if 'thresholds' in config and config['thresholds']:
            thresholds = config['thresholds']
            
            # Sort thresholds by value
            sorted_thresholds = sorted(thresholds, key=lambda x: x['value'])
            
            # Find applicable threshold
            for threshold in sorted_thresholds:
                condition = threshold.get('condition', '≥')
                threshold_val = threshold['value']
                
                # Check if condition is met
                is_met = False
                if condition in ['≥', '>=']:
                    is_met = value >= threshold_val
                elif condition in ['≤', '<=']:
                    is_met = value <= threshold_val
                elif condition == '>':
                    is_met = value > threshold_val
                elif condition == '<':
                    is_met = value < threshold_val
                elif condition == '==':
                    is_met = abs(value - threshold_val) < 0.0001
                
                if is_met:
                    return threshold.get('color', '#00ff00')
            
            # No threshold met - return None (gray)
            return None
        
        # Old format: single threshold (backward compatibility)
        elif 'threshold' in config:
            threshold = float(config.get('threshold', 0))
            condition = config.get('condition', '>')
            
            is_active = False
            if condition == '>': is_active = value > threshold
            elif condition == '<': is_active = value < threshold
            elif condition == '>=': is_active = value >= threshold
            elif condition == '<=': is_active = value <= threshold
            elif condition == '==': is_active = abs(value - threshold) < 0.0001
            
            return '#21b35a' if is_active else None
        
        # No configuration - default to gray
        return None
    
    def _adjust_brightness(self, color_hex, factor):
        """Adjust color brightness for border effect"""
        try:
            from PySide6.QtGui import QColor
            color = QColor(color_hex)
            h, s, v, a = color.getHsv()
            v = min(255, int(v * factor))
            color.setHsv(h, s, v, a)
            return color.name()
        except:
            return color_hex
            
# Optional: Map widget using QWebEngineView if available
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
except Exception:
    QWebEngineView = None


class MapWidget(QWidget):
    """
    @brief Widget for displaying GPS position on a map.
    @details Uses Leaflet.js via QWebEngineView if available, otherwise falls back to text display.
    """
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
        layout.setContentsMargins(0, 0, 0, 0) # Remove margins for map to fill
        layout.setSpacing(0)
        
        self.setStyleSheet("""
            MapWidget {
                background-color: rgba(30, 30, 30, 0.8);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            QWebEngineView {
                border-radius: 16px;
                background: transparent;
            }
        """)

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
    """
    @brief Widget for displaying a tabular log of telemetry data.
    @details Shows timestamped values and supports searching/highlighting specific conditions.
    """
    def __init__(self, param_configs):
        super().__init__()
        self.param_configs = param_configs
        self.param_map = {p['id']: {'name': p['name'], 'col': i + 1} for i, p in enumerate(self.param_configs)}
        self.last_known_values = {}
        self.highlight_brush = QBrush(QColor("#0078FF").lighter(150))
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget()
        headers = ["Timestamp"] + [f"{p['name']} ({p['unit']})" for p in self.param_configs]
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Parameter", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Apple-like Table Styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                gridline-color: transparent;
                border: none;
                color: #e0e0e0;
                font-family: "SF Pro Text";
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTableWidget::item:selected {
                background-color: rgba(10, 132, 255, 0.3);
            }
            QHeaderView::section {
                background-color: rgba(40, 40, 40, 0.8);
                color: #aaaaaa;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-family: "SF Pro Text";
                font-size: 12px;
                text-transform: uppercase;
            }
        """)
        
        layout.addWidget(self.table)
        # --- Collapsible Search Bar ---
        
        # 1. Toolbar with Toggle Button
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)
        toolbar.addStretch()
        
        self.toggle_search_btn = QPushButton()
        self.toggle_search_btn.setIcon(QIcon.fromTheme("system-search-symbolic"))
        self.toggle_search_btn.setFixedSize(32, 32)
        self.toggle_search_btn.setCheckable(True)
        self.toggle_search_btn.setToolTip("Toggle Search")
        self.toggle_search_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.toggle_search_btn.clicked.connect(self._toggle_search_visibility)
        toolbar.addWidget(self.toggle_search_btn)
        
        layout.addLayout(toolbar)
        
        # 2. Search Container (Hidden by default)
        self.search_container = QWidget()
        self.search_container.hide()
        
        search_group_layout = QVBoxLayout(self.search_container)
        search_group_layout.setContentsMargins(0, 0, 0, 0)
        
        search_group = QGroupBox("Search and Highlight")
        search_layout = QHBoxLayout(search_group)
        self.search_param_combo = QComboBox(); self.search_param_combo.addItems([p['name'] for p in self.param_configs])
        self.search_cond_combo = QComboBox(); self.search_cond_combo.addItems(["=", ">", "<", ">=", "<="])
        self.search_value_spinbox = QDoubleSpinBox(); self.search_value_spinbox.setRange(-1e9, 1e9); self.search_value_spinbox.setDecimals(4)
        search_btn = QPushButton("Search Last"); clear_btn = QPushButton("Clear")
        search_layout.addWidget(QLabel("Find in:")); search_layout.addWidget(self.search_param_combo)
        search_layout.addWidget(self.search_cond_combo); search_layout.addWidget(self.search_value_spinbox)
        search_layout.addWidget(search_btn); search_layout.addWidget(clear_btn)
        
        search_group_layout.addWidget(search_group)
        layout.addWidget(self.search_container)
        
        search_btn.clicked.connect(self.search_and_highlight)
        clear_btn.clicked.connect(self.clear_highlights)

    def _toggle_search_visibility(self, checked):
        if checked:
            self.search_container.show()
        else:
            self.search_container.hide()
    def update_data(self, updated_param_id, history):
        # Optimization: Limit rows to 100
        if self.table.rowCount() > 100: self.table.removeRow(100)
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

