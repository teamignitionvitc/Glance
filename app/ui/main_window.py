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
# File:        main_window.py
# Author:      MuhammadRamzy
# Created On:  26-09-2025
#
# @brief       Main application window and UI logic.
# @details     Manages the application lifecycle, UI phases (Splash, Welcome, Setup, Dashboard),
#              widget management, and data flow coordination.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      26-09-2025  MuhammadRamzy        First commit with the ui/ux and flow changes
# 001  MOD      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side
#                                                layout and QStackedWidget
# 002  MOD      30-11-2025  MuhammadRamzy        feat: Enhance status bar UI/UX and implement CI/CD
#                                                workflows, fix: Simplify status bar and remove
#                                                CI/CD workflows
####################################################################################################

####################################################################################################
# Imports

import sys
import os
import time
import json
import base64
import math
import uuid
import csv
import random
from datetime import datetime
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QComboBox, QLineEdit, QLabel, QFrame, QPushButton, QFileDialog, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QTabWidget, QDialog,
    QFormLayout, QDialogButtonBox, QDoubleSpinBox, QDockWidget, QSizePolicy,
    QInputDialog, QMessageBox, QTabBar, QAbstractItemView, QSpinBox, QStackedWidget,
    QCheckBox, QTreeWidget, QTreeWidgetItem, QApplication, QMenu, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, Slot, QByteArray, QPropertyAnimation, QEasingCurve, QPoint, QRect, QUrl
from PySide6.QtGui import QFont, QColor, QBrush, QAction, QPixmap, QIcon
import pyqtgraph as pg

try:
    from serial.tools import list_ports as _serial_list_ports
except ImportError:
    _serial_list_ports = None

import webbrowser

# ReportLab imports
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# QWebEngineView import
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    QWebEngineView = None

from app.core.data_logger import DataLogger
from app.core.filters import FilterManager, MovingAverageFilter, LowPassFilter, KalmanFilter, MedianFilter
from app.core.simulator import DataSimulator
from app.widgets import ValueCard, TimeGraph, LogTable, GaugeWidget, HistogramWidget, LEDWidget, MapWidget, ClosableDock
from app.widgets.telemetry import RawTelemetryMonitor, StandaloneTelemetryViewer
from app.dialogs import ConnectionSettingsDialog, AddWidgetDialog, ParameterEntryDialog, ManageParametersDialog, DataLoggingDialog
from app.core.history import CommandHistory
from app.core.commands import AddWidgetCommand, RemoveWidgetCommand, UpdateParametersCommand

####################################################################################################
class MainWindow(QMainWindow):
    """
    @brief Main application window.
    @details Orchestrates the entire application, handling UI navigation, data simulation/acquisition,
             and widget management.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glance - Telemetry Dashboard")
        self.setWindowIcon(QIcon("./docs/public/Glance_nobg.ico"))
        
        # CRITICAL: Initialize fullscreen state before anything else
        self.is_fullscreen = False
        self.normal_geometry = None
        
        # Improved initial sizing and centering
        self.setMinimumSize(1200, 720)
        self.resize(1200, 720)
        try:
            screen = self.screen() or QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                x = geo.x() + (geo.width() - self.width()) // 2
                y = geo.y() + (geo.height() - self.height()) // 3
                self.move(x, y)
        except Exception:
            pass
        
        self.graph_color_palette = ['#00BFFF', '#FF3131', '#39CCCC', '#F012BE', '#FFDC00', '#7FDBFF', '#01FF70', '#FF851B']
        self.next_graph_color_index = 0
        self.parameters = []
        self.data_history = {}
        self.tab_data = {}
        self.graph_color_palette = ['#00BFFF', '#FF3131', '#39CCCC', '#F012BE', '#FFDC00', '#7FDBFF', '#01FF70', '#FF851B']
        self.next_graph_color_index = 0
        self.parameters = []; self.data_history = {}; self.tab_data = {}
        self.connection_settings = {
            'mode': 'dummy',
            'serial_port': 'COM4',
            'baudrate': 115200,
            'tcp_host': '127.0.0.1',
            'tcp_port': 9000,
            'udp_host': '0.0.0.0',
            'udp_port': 9000,
            'timeout': 1.0,
        }
        
        # Initialize data logger
        self.data_logger = DataLogger()
        self.filter_manager = FilterManager()
        self.logging_settings = None
        
        # Undo/Redo History - Dashboard specific
        self.dashboard_history = CommandHistory()  # For widget add/remove operations
        # Note: Parameter dialog has its own history managed internally
        
        # Metrics
        self.packet_count = 0
        self.packet_timestamps = []

        # Raw telemetry monitor
        self.raw_tlm_monitor = None
        
        # Track unsaved changes
        self.has_unsaved_changes = False
        self.current_project_path = None
        # Four-phase UI: Welcome -> Setup -> Widgets -> Dashboard
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.tab_widget = QTabWidget(); self.tab_widget.setTabsClosable(True)
        self.tab_widget.currentChanged.connect(self.on_tab_changed); self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Add these lines:
        self._setup_tab_double_click()
        self._setup_tab_context_menu()
        self._setup_tab_drag_drop()
        # Minimal list to track active displays; not shown in UI currently
        self.active_displays_list = QListWidget()
        header_widget = QWidget(); header_layout = QHBoxLayout(header_widget)
        self.stream_status_label = QLabel("Awaiting Parameters")
        self.connection_status_label = QLabel("Not Connected")
        self.pause_button = QPushButton("Pause Stream"); self.pause_button.setCheckable(True)
        self.logging_status_label = QLabel("Logging: OFF")
        # Customizable dashboard title
        self.dashboard_title = QLabel("<h2>Dashboard</h2>")
        self.dashboard_title.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.dashboard_title.customContextMenuRequested.connect(self._show_title_context_menu)
        self.dashboard_title_text = "Dashboard"
        self.dashboard_title_alignment = Qt.AlignmentFlag.AlignLeft

        header_layout.addWidget(self.dashboard_title); header_layout.addStretch()
        header_layout.addWidget(self.connection_status_label)
        header_layout.addWidget(self.stream_status_label)
        header_layout.addWidget(self.logging_status_label)
        header_layout.addWidget(self.pause_button)
        self.header_dock = QDockWidget(); self.header_dock.setTitleBarWidget(QWidget())
        self.header_dock.setWidget(header_widget); self.header_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.header_dock)
        
        # UI Update Timer (Throttling to ~30 FPS)
        self.ui_update_timer = QTimer(self)
        self.ui_update_timer.timeout.connect(self.update_dashboard_ui)
        self.ui_update_timer.start(33) # 33ms = ~30 FPS

        self.health_timer = QTimer(self); self.health_timer.timeout.connect(self.check_data_stream); self.health_timer.start(1000)
        self.pause_button.clicked.connect(self.toggle_pause_stream); self.simulator = None
        self._build_menu_bar()
        self._build_status_bar()
        self.apply_stylesheet()
        self._build_splash_screen()
        self._build_welcome_page()
        self._build_setup_page()
        self._build_widgets_page()
        self._build_dashboard_page()
        self.show_phase("splash")
        self.restart_simulator()
        self.update_control_states()
        
        # Initialize window title
        self.update_window_title()

    def toggle_fullscreen(self):
        """
        @brief Toggle fullscreen mode.
        @details Switches between fullscreen and normal windowed mode, hiding/showing UI elements as needed.
        """
        if self.is_fullscreen:
            # Exit fullscreen
            self.showNormal()
            
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            
            self.menuBar().setVisible(True)
            self.statusBar().setVisible(True)
            
            if hasattr(self, 'header_dock') and self.header_dock:
                if self.stack.currentWidget() == self.dashboard_page:
                    self.header_dock.setVisible(True)
            
            self.is_fullscreen = False
        else:
            # Enter fullscreen
            self.normal_geometry = self.geometry()
            
            self.menuBar().setVisible(False)
            self.statusBar().setVisible(False)
            
            if hasattr(self, 'header_dock') and self.header_dock:
                self.header_dock.setVisible(False)
            
            self.showFullScreen()
            
            self.is_fullscreen = True
            
            # Show hint (optional)
            QTimer.singleShot(100, self.show_fullscreen_hint)

            # Show hint (optional)
            QTimer.singleShot(100, self.show_fullscreen_hint)

    def undo(self):
        self.history.undo()
        self.update_dashboard_ui() # Refresh UI
        self.update_control_states()

    def redo(self):
        self.history.redo()
        self.update_dashboard_ui() # Refresh UI
        self.update_control_states()

    def keyPressEvent(self, event):
        """Handle key press events"""
        # Undo/Redo shortcuts - context-aware
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Z:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.context_aware_redo()
                else:
                    self.context_aware_undo()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Y:
                self.context_aware_redo()
                event.accept()
                return

        # F11 for fullscreen
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
            event.accept()
        # ESC to exit fullscreen
        elif event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def context_aware_undo(self):
        """Context-aware undo"""
        phase = self._get_current_phase()
        
        if phase == "dashboard":
            if self.dashboard_history.can_undo():
                self.dashboard_history.undo()
            else:
                self.statusBar().showMessage("No dashboard actions to undo", 2000)
        else:
            self.statusBar().showMessage("Undo not available in this view", 2000)
    
    def context_aware_redo(self):
        """Redo based on current context - only works on dashboard"""
        current_phase = self._get_current_phase()
        
        if current_phase == "dashboard":
            if self.dashboard_history.can_redo():
                self.dashboard_history.redo()
                self.update_dashboard_ui()
                self.refresh_active_displays_list()
                self.update_control_states()
            else:
                self.statusBar().showMessage("No dashboard actions to redo", 2000)
        else:
            # Redo not available in other phases
            self.statusBar().showMessage("Redo not available in this view", 2000)
    
    def _get_current_phase(self):
        """Get the current UI phase"""
        if not hasattr(self, 'stack'):
            return "unknown"
        
        current_widget = self.stack.currentWidget()
        if hasattr(self, 'dashboard_page') and current_widget == self.dashboard_page:
            return "dashboard"
        elif hasattr(self, 'setup_page') and current_widget == self.setup_page:
            return "setup"
        elif hasattr(self, 'widgets_page') and current_widget == self.widgets_page:
            return "widgets"
        elif hasattr(self, 'welcome_page') and current_widget == self.welcome_page:
            return "welcome"
        elif hasattr(self, 'splash_page') and current_widget == self.splash_page:
            return "splash"
        return "unknown"
    
    def undo(self):
        """Legacy undo method - redirects to context-aware version"""
        self.context_aware_undo()
    
    def redo(self):
        """Legacy redo method - redirects to context-aware version"""
        self.context_aware_redo()

    def refresh_setup_serial_ports(self):
        """
        @brief Refresh the list of available serial ports.
        @details Updates the combo box in the setup page with currently available ports.
        """
        current_text = self.setup_serial_port.currentText()
        self.setup_serial_port.clear()
        
        ports = self.list_serial_ports()
        self.setup_serial_port.addItems(ports)
        
        # Try to restore previous selection
        index = self.setup_serial_port.findText(current_text)
        if index >= 0:
            self.setup_serial_port.setCurrentIndex(index)
        else:
            self.setup_serial_port.setCurrentText(current_text)

    def list_serial_ports(self):
        ports = []
        try:
            if _serial_list_ports:
                ports = [p.device for p in _serial_list_ports.comports()]
        except Exception:
            ports = []
        # Add common defaults if none found
        if not ports:
            if sys.platform.startswith('linux'): ports = ['/dev/ttyUSB0', '/dev/ttyACM0']
            elif sys.platform.startswith('win'): ports = ['COM3','COM4','COM5']
            else: ports = ['/dev/tty.usbserial', '/dev/tty.usbmodem']
        return ports

    def create_control_dock(self):
        # Removed in favor of top-bar menus
        self.control_dock = None

    # --- MODIFIED: Handles new data source selection ---
    def on_source_changed(self, source_text):
        """
        @brief Handle data source change.
        @param source_text The text of the selected source (Dummy/Backend).
        """
        if not self.simulator: return
        if "Dummy" in source_text or "dummy" in self.simulator.mode:
            self.simulator.mode = "dummy"
            source_text = "Dummy Data"
            if self.simulator._is_paused: self.toggle_pause_stream()
        else: # Backend
            self.simulator.mode = "backend"
            source_text = "Backend"
            if not self.simulator._is_paused: self.toggle_pause_stream()
        # self.update_status_bar()

    def add_widget_to_dashboard(self, config, tab_index, widget_id=None):
        """
        @brief Add a widget to the dashboard.
        @param config Widget configuration dictionary.
        @param tab_index Index of the tab to add the widget to.
        @param widget_id Optional unique ID for the widget.
        """
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        if widget_id is None: widget_id = str(uuid.uuid4())
        param_ids = config['param_ids']
        param_configs = [p for p in self.parameters if p['id'] in param_ids]
        if not param_configs: return
        widget_title = ", ".join([p['name'] for p in param_configs])
        widget = None
        if config['displayType'] == 'Time Graph':
            for p_config in param_configs:
                p_config['color'] = self.graph_color_palette[self.next_graph_color_index % len(self.graph_color_palette)]
                self.next_graph_color_index += 1
            widget = TimeGraph(param_configs)
        elif config['displayType'] == 'Log Table':
            widget = LogTable(param_configs)
        elif config['displayType'] == 'Instant Value':
            widget = ValueCard(param_configs, config['priority'])
        elif config['displayType'] == 'Gauge' and len(param_configs) == 1:
            widget = GaugeWidget(param_configs[0], config.get('options'))
        elif config['displayType'] == 'Histogram' and len(param_configs) == 1:
            widget = HistogramWidget(param_configs[0])
        elif config['displayType'] == 'LED Indicator':
            widget = LEDWidget(param_configs, config.get('options'))
        elif config['displayType'] == 'Map (GPS)' and len(param_configs) == 2:
            widget = MapWidget(param_configs)
        
        if widget:
            # Set minimum sizes for better visibility
            widget.setMinimumSize(300, 200)
            if hasattr(widget, 'plot_widget'):  # For graphs
                widget.setMinimumSize(400, 300)
            elif hasattr(widget, 'table'):  # For tables
                widget.setMinimumSize(500, 300)
            dock = ClosableDock(f"{widget_title} ({config['displayType']})", self, widget_id)
            dock.setObjectName(f"dock_{widget_id}")  # Set unique object name
            dock.setWidget(widget)

            dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                 QDockWidget.DockWidgetFeature.DockWidgetMovable |
                 QDockWidget.DockWidgetFeature.DockWidgetFloatable)

            dock.setMinimumSize(300, 200)
            # Add right-click context menu
            dock.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            dock.customContextMenuRequested.connect(lambda pos: self._show_dock_context_menu(dock, pos))
            dock.closed.connect(self._handle_dock_close)

            tab_mainwindow = tab_info['mainwindow']
            num_docks = len(tab_info['docks'])
            docks_list = list(tab_info['docks'].values())
            if num_docks == 0:
                # First widget - add to left area
                tab_mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            elif num_docks == 1:
                # Second widget - split horizontally
                tab_mainwindow.splitDockWidget(docks_list[0], dock, Qt.Orientation.Horizontal)
                tab_info['last_orient'] = 'h'
            else:
                # Alternate split orientation relative to the last added dock to tile without removing
                last_dock = docks_list[-1]
                last_orient = tab_info.get('last_orient', 'v')
                orient = Qt.Orientation.Horizontal if last_orient == 'v' else Qt.Orientation.Vertical
                tab_mainwindow.splitDockWidget(last_dock, dock, orient)
                tab_info['last_orient'] = 'h' if orient == Qt.Orientation.Horizontal else 'v'
            tab_info['widgets'][widget_id] = widget; tab_info['docks'][widget_id] = dock; tab_info['configs'][widget_id] = config
            # Maintain layout positions for move/tile operations
            positions = tab_info.setdefault('layout_positions', {})
            positions[widget_id] = self._next_grid_position(positions)
            # Ensure new widget is visible and on top
            dock.show()
            dock.raise_()
            dock.activateWindow()
            self.refresh_active_displays_list()

    def _tile_widgets_in_grid(self, mainwindow, docks):
        """
        @brief Arrange widgets in a grid pattern.
        @param mainwindow The QMainWindow instance (tab content).
        @param docks List of dock widgets to tile.
        """
        if len(docks) < 3: return
        try:
            # Calculate grid dimensions
            cols = int(np.ceil(np.sqrt(len(docks))))
            rows = int(np.ceil(len(docks) / cols))
            # Clear existing layout
            for dock in docks:
                mainwindow.removeDockWidget(dock)
            # Add first dock
            mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, docks[0])
            # Add remaining docks in grid
            for i, dock in enumerate(docks[1:], 1):
                if i < cols:
                    # First row - split horizontally
                    mainwindow.splitDockWidget(docks[0], dock, Qt.Orientation.Horizontal)
                else:
                    # Subsequent rows - split vertically with dock above
                    above_dock = docks[i - cols]
                    mainwindow.splitDockWidget(above_dock, dock, Qt.Orientation.Vertical)
        except Exception:
            # Fallback to simple tabify
            for dock in docks[1:]:
                mainwindow.tabifyDockWidget(docks[0], dock)

    def _show_title_context_menu(self, pos):
        """Show context menu for dashboard title customization"""
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # Edit title action
        edit_action = menu.addAction("Edit Title...")
        edit_action.triggered.connect(self._edit_dashboard_title)
        
        menu.addSeparator()
        
        # Alignment submenu
        align_menu = menu.addMenu("Alignment")
        
        left_action = align_menu.addAction("Left")
        left_action.setCheckable(True)
        left_action.setChecked(self.dashboard_title_alignment == Qt.AlignmentFlag.AlignLeft)
        left_action.triggered.connect(lambda: self._set_title_alignment(Qt.AlignmentFlag.AlignLeft))
        
        center_action = align_menu.addAction("Center")
        center_action.setCheckable(True)
        center_action.setChecked(self.dashboard_title_alignment == Qt.AlignmentFlag.AlignCenter)
        center_action.triggered.connect(lambda: self._set_title_alignment(Qt.AlignmentFlag.AlignCenter))
        
        right_action = align_menu.addAction("Right")
        right_action.setCheckable(True)
        right_action.setChecked(self.dashboard_title_alignment == Qt.AlignmentFlag.AlignRight)
        right_action.triggered.connect(lambda: self._set_title_alignment(Qt.AlignmentFlag.AlignRight))
        
        menu.addSeparator()
        
        # Reset action
        reset_action = menu.addAction("Reset to Default")
        reset_action.triggered.connect(self._reset_dashboard_title)
        
        menu.exec(self.dashboard_title.mapToGlobal(pos))
    
    def _edit_dashboard_title(self):
        """Edit the dashboard title text"""
        new_title, ok = QInputDialog.getText(
            self, 
            "Edit Dashboard Title", 
            "Enter new title:",
            text=self.dashboard_title_text
        )
        if ok and new_title:
            self.dashboard_title_text = new_title
            self._update_dashboard_title()
            self.mark_as_unsaved()
    
    def _set_title_alignment(self, alignment):
        """Set the dashboard title alignment"""
        self.dashboard_title_alignment = alignment
        self._update_dashboard_title()
        self.mark_as_unsaved()
    
    def _reset_dashboard_title(self):
        """Reset dashboard title to default"""
        self.dashboard_title_text = "Dashboard"
        self.dashboard_title_alignment = Qt.AlignmentFlag.AlignLeft
        self._update_dashboard_title()
        self.mark_as_unsaved()
    
    def _update_dashboard_title(self):
        """Update the dashboard title display"""
        self.dashboard_title.setText(f"<h2>{self.dashboard_title_text}</h2>")
        self.dashboard_title.setAlignment(self.dashboard_title_alignment)
        
        # Force the label to expand to take up space for alignment to work
        if self.dashboard_title_alignment == Qt.AlignmentFlag.AlignCenter:
            self.dashboard_title.setMinimumWidth(300)
        elif self.dashboard_title_alignment == Qt.AlignmentFlag.AlignRight:
            self.dashboard_title.setMinimumWidth(300)
        else:
            self.dashboard_title.setMinimumWidth(0)

    def _show_dock_context_menu(self, dock, pos):
        """Right-click context menu for dock widgets"""
        self._add_dock_context_menu_transfer(dock, pos)
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        # Get widget info - store the dock reference directly
        self._context_dock = dock
        current_index = self.tab_widget.currentIndex()
        tinfo = self.tab_data.get(current_index, {})
        widget_id = None
        for wid, d in tinfo.get('docks', {}).items():
            if d == dock:
                widget_id = wid
                break
        
        if widget_id:
            rename_action = menu.addAction("Rename Widget")
            rename_action.triggered.connect(self._rename_widget_direct)
            float_action = menu.addAction("Float / Dock")
            float_action.triggered.connect(self._toggle_float_direct)
            menu.addSeparator()
            close_action = menu.addAction("Close Widget")
            close_action.triggered.connect(self._close_widget_direct)
            menu.addSeparator()
            tile_action = menu.addAction("Tile Evenly")
            tile_action.triggered.connect(lambda: self._tile_evenly_safe(current_index))  # Pass current_index
        else:
            menu.addAction("No actions available")
        menu.exec(dock.mapToGlobal(pos))
    

    def _next_grid_position(self, positions):
        """Compute next row,col for a new widget using a nearly square grid."""
        n = len(positions)
        if n == 0:
            return (0, 0)
        cols = int(np.ceil(np.sqrt(n + 1)))
        row = n // cols
        col = n % cols
        return (row, col)

    def _retile_positions(self, tab_index):
        """Retile docks based on saved positions (row, col) without changing assignments."""
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: 
            return
        docks = tab_info['docks']
        positions = tab_info.get('layout_positions', {})
        if not docks: 
            return
        
        # Filter out floating docks - they shouldn't be retiled
        non_floating_docks = {}
        floating_docks = {}
        
        for widget_id, dock in docks.items():
            if dock.isFloating():
                floating_docks[widget_id] = dock
            else:
                non_floating_docks[widget_id] = dock
        
        # Only retile non-floating docks
        if not non_floating_docks:
            return
            
        # Create positions for non-floating docks only
        non_floating_positions = {wid: pos for wid, pos in positions.items() if wid in non_floating_docks}
        
        # If no positions saved, create a default grid layout
        if not non_floating_positions:
            self._create_default_grid_positions(non_floating_docks, tab_index)
            non_floating_positions = tab_info.get('layout_positions', {})
        
        # Order docks by row-major order
        ordered = sorted(non_floating_positions.items(), key=lambda x: (x[1][0], x[1][1]))
        dock_list = [non_floating_docks[wid] for wid, _ in ordered if wid in non_floating_docks]
        
        if not dock_list:
            return
            
        mw = tab_info['mainwindow']
        
        try:
            # Remove all non-floating docks from layout
            for dock in dock_list:
                mw.removeDockWidget(dock)
            
            # Add first dock
            mw.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_list[0])
            dock_list[0].setVisible(True)
            dock_list[0].raise_()
            
            # Calculate grid dimensions dynamically
            if len(dock_list) == 1:
                return
                
            # Calculate optimal grid dimensions
            n = len(dock_list)
            cols = max(1, len(set(c for _, (_, c) in non_floating_positions.items())))
            rows = max(1, len(set(r for _, (r, _) in non_floating_positions.items())))
            
            # Ensure we have a reasonable grid
            if cols == 0:
                cols = int(np.ceil(np.sqrt(n)))
            if rows == 0:
                rows = int(np.ceil(n / cols))
            
            # Create grid layout dynamically
            for i, dock in enumerate(dock_list[1:], 1):
                row = i // cols
                col = i % cols
                
                if col == 0:
                    # First column of new row - split vertically with dock above
                    above_idx = i - cols
                    if above_idx >= 0 and above_idx < len(dock_list):
                        mw.splitDockWidget(dock_list[above_idx], dock, Qt.Orientation.Vertical)
                else:
                    # Same row - split horizontally with previous dock
                    mw.splitDockWidget(dock_list[i - 1], dock, Qt.Orientation.Horizontal)
                
                dock.setVisible(True)
                dock.raise_()
            
            # Ensure all docks are visible and properly positioned
            for dock in dock_list:
                dock.setVisible(True)
                dock.raise_()
            
            # Force layout update
            mw.update()
            QApplication.processEvents()
            
        except Exception as e:
            print(f"Retiling failed: {e}")
            # Fallback to tabify all docks
            try:
                for dock in dock_list[1:]:
                    mw.tabifyDockWidget(dock_list[0], dock)
                    dock.setVisible(True)
            except Exception as e2:
                print(f"Fallback tabify also failed: {e2}")
                # Last resort - just make sure docks are visible
                for dock in dock_list:
                    dock.setVisible(True)
                    dock.show()

    def _create_default_grid_positions(self, docks_dict, tab_index):
        """Create default grid positions for docks that don't have saved positions."""
        tab_info = self.tab_data.get(tab_index)
        if not tab_info:
            return
            
        positions = tab_info.setdefault('layout_positions', {})
        n = len(docks_dict)
        
        if n == 0:
            return
            
        # Calculate optimal grid dimensions
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        
        # Assign positions in row-major order
        for i, widget_id in enumerate(docks_dict.keys()):
            row = i // cols
            col = i % cols
            positions[widget_id] = (row, col)

    def _rename_widget(self, widget_id):
        """Rename a widget"""
        tab_info = self.tab_data.get(self.tab_widget.currentIndex())
        if not tab_info or widget_id not in tab_info['docks']: return
        dock = tab_info['docks'][widget_id]
        current_name = dock.windowTitle()
        new_name, ok = QInputDialog.getText(self, "Rename Widget", "Enter new name:", text=current_name)
        if ok and new_name:
            dock.setWindowTitle(new_name)

    def _close_widget_direct(self):
        """Close the dock that was right-clicked"""
        if not hasattr(self, '_context_dock'): return
        dock = self._context_dock
        current_index = self.tab_widget.currentIndex()
        tab_info = self.tab_data.get(current_index)
        if not tab_info: return
        
        # Find the widget_id for this dock
        widget_id = None
        for wid, d in tab_info['docks'].items():
            if d == dock:
                widget_id = wid
                break
        
        if widget_id:
            dock.deleteLater()
            del tab_info['docks'][widget_id]
            if widget_id in tab_info['widgets']: 
                del tab_info['widgets'][widget_id]
            if widget_id in tab_info['configs']: 
                del tab_info['configs'][widget_id]
            if 'layout_positions' in tab_info and widget_id in tab_info['layout_positions']:
                del tab_info['layout_positions'][widget_id]
            self.refresh_active_displays_list()

    def _rename_widget_direct(self):
        """Rename the dock that was right-clicked"""
        if not hasattr(self, '_context_dock'): return
        dock = self._context_dock
        current_name = dock.windowTitle()
        new_name, ok = QInputDialog.getText(self, "Rename Widget", "Enter new name:", text=current_name)
        if ok and new_name:
            dock.setWindowTitle(new_name)

    def _toggle_float_direct(self):
        """Toggle float for the dock that was right-clicked with improved snapping back behavior"""
        if not hasattr(self, '_context_dock'): 
            return
        dock = self._context_dock
        
        if dock.isFloating():
            # Snapping back to docked state
            dock.setFloating(False)
            dock.setVisible(True)
            dock.show()
            
            # Trigger retiling to ensure proper positioning
            self._retile_positions(self.tab_widget.currentIndex())
        else:
            # Floating the widget
            dock.setFloating(True)
            dock.raise_()
            dock.activateWindow()

    def _tile_evenly_safe(self, tab_index):
        """Safely tile widgets in a grid pattern - handles any number of widgets dynamically"""
        tab_info = self.tab_data.get(tab_index)
        if not tab_info or not tab_info.get('docks'): 
            return
        
        docks_dict = tab_info['docks']
        docks = list(docks_dict.values())
        
        if len(docks) <= 1: 
            return
        
        mainwindow = tab_info['mainwindow']
        
        try:
            # Calculate optimal grid dimensions dynamically
            n = len(docks)
            cols = int(np.ceil(np.sqrt(n)))
            rows = int(np.ceil(n / cols))
            
            # Store visibility and floating state
            dock_states = {}
            for dock in docks:
                dock_states[dock] = {
                    'visible': dock.isVisible(),
                    'floating': dock.isFloating()
                }
                # Make sure it's not floating for tiling
                if dock.isFloating():
                    dock.setFloating(False)
            
            # Remove all docks from layout
            for dock in docks:
                mainwindow.removeDockWidget(dock)
            
            # Add first dock
            mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, docks[0])
            docks[0].setVisible(True)
            docks[0].raise_()
            
            # Create grid layout dynamically for any number of widgets
            for i, dock in enumerate(docks[1:], 1):
                row = i // cols
                col = i % cols
                
                if col == 0:
                    # First column of new row - split vertically with dock above
                    above_idx = i - cols
                    if above_idx >= 0 and above_idx < len(docks):
                        mainwindow.splitDockWidget(docks[above_idx], dock, Qt.Orientation.Vertical)
                else:
                    # Same row - split horizontally with previous dock
                    mainwindow.splitDockWidget(docks[i - 1], dock, Qt.Orientation.Horizontal)
                
                dock.setVisible(True)
                dock.raise_()
            
            # Update layout positions for future retiling
            positions = tab_info.setdefault('layout_positions', {})
            for i, (widget_id, dock) in enumerate(docks_dict.items()):
                row = i // cols
                col = i % cols
                positions[widget_id] = (row, col)
            
            # Ensure all docks are visible and raised
            for dock in docks:
                dock.setVisible(True)
                dock.raise_()
            
            # Force layout update
            mainwindow.update()
            QApplication.processEvents()
            
        except Exception as e:
            # Emergency fallback - make sure docks are visible
            print(f"Tiling failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to recover by making docks visible
            try:
                for dock in docks:
                    if not dock.parent():
                        mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
                    dock.setVisible(True)
                    dock.show()
            except Exception as e2:
                print(f"Failed to recover dock: {e2}")

    def _toggle_float_widget(self, widget_id):
        """Toggle float for a widget with improved snapping back behavior"""
        tab_info = self.tab_data.get(self.tab_widget.currentIndex())
        if not tab_info or widget_id not in tab_info['docks']: 
            return
        dock = tab_info['docks'][widget_id]
        
        if dock.isFloating():
            # Snapping back to docked state
            dock.setFloating(False)
            dock.setVisible(True)
            dock.show()
            
            # Trigger retiling to ensure proper positioning
            self._retile_positions(self.tab_widget.currentIndex())
        else:
            # Floating the widget
            dock.setFloating(True)
            dock.raise_()
            dock.activateWindow()

    def _toggle_maximize_widget(self, widget_id):
        tab_info = self.tab_data.get(self.tab_widget.currentIndex())
        if not tab_info or widget_id not in tab_info['docks']: return
        mw = tab_info['mainwindow']
        docks = tab_info['docks']
        maximized = tab_info.get('maximized_widget_id')
        if maximized == widget_id:
            # Restore all docks
            for wid, d in docks.items():
                d.show()
            tab_info['maximized_widget_id'] = None
        elif maximized is None:
            # Hide all except this
            for wid, d in docks.items():
                if wid != widget_id:
                    d.hide()
            tab_info['maximized_widget_id'] = widget_id
        else:
            # Switch maximized target
            for wid, d in docks.items():
                d.setVisible(wid == widget_id)
            tab_info['maximized_widget_id'] = widget_id

    def _tile_evenly(self, tab_index):
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        # Reassign positions into an even grid
        positions = {}
        ids = list(tab_info['docks'].keys())
        for i, wid in enumerate(ids):
            positions[wid] = self._next_grid_position(positions)
        tab_info['layout_positions'] = positions
        self._retile_positions(tab_index)

    def _move_widget(self, widget_id, direction):
        """Move widget in specified direction within the grid and retile."""
        tab_index = self.tab_widget.currentIndex()
        tab_info = self.tab_data.get(tab_index)
        if not tab_info: return
        positions = tab_info.setdefault('layout_positions', {})
        if widget_id not in positions: return
        # Determine grid size
        cols = int(np.ceil(np.sqrt(max(1, len(positions)))))
        row, col = positions[widget_id]
        target = None
        if direction == 'left' and col > 0:
            target = (row, col - 1)
        elif direction == 'right':
            target = (row, col + 1)
        elif direction == 'up' and row > 0:
            target = (row - 1, col)
        elif direction == 'down':
            target = (row + 1, col)
        if target is None:
            return
        # Find widget at target; if none, just move into the spot
        swap_id = None
        for wid, pos in positions.items():
            if pos == target:
                swap_id = wid
                break
        positions[widget_id] = target
        if swap_id:
            positions[swap_id] = (row, col)
        # Normalize positions to a compact grid
        self._normalize_positions(positions)
        self._retile_positions(tab_index)

    def _handle_dock_snapping(self, dock):
        """Handle automatic snapping back when dock is dragged close to main window"""
        if not dock.isFloating():
            return
            
        # Get the main window geometry
        main_window = self.geometry()
        dock_geometry = dock.geometry()
        
        # Define snap threshold (pixels)
        snap_threshold = 50
        
        # Check if dock is close to main window edges
        dock_left = dock_geometry.left()
        dock_right = dock_geometry.right()
        dock_top = dock_geometry.top()
        dock_bottom = dock_geometry.bottom()
        
        main_left = main_window.left()
        main_right = main_window.right()
        main_top = main_window.top()
        main_bottom = main_window.bottom()
        
        # Check for proximity to main window
        close_to_left = abs(dock_right - main_left) < snap_threshold
        close_to_right = abs(dock_left - main_right) < snap_threshold
        close_to_top = abs(dock_bottom - main_top) < snap_threshold
        close_to_bottom = abs(dock_top - main_bottom) < snap_threshold
        
        # Check if dock is overlapping with main window
        overlapping = (dock_left < main_right and dock_right > main_left and 
                     dock_top < main_bottom and dock_bottom > main_top)
        
        # If dock is close to or overlapping with main window, snap it back
        if (close_to_left or close_to_right or close_to_top or close_to_bottom or overlapping):
            dock.setFloating(False)
            dock.setVisible(True)
            dock.show()
            
            # Trigger retiling to ensure proper positioning
            self._retile_positions(self.tab_widget.currentIndex())

    def _normalize_positions(self, positions):
        """Compress rows/cols to remove gaps after moves/closures with improved robustness."""
        if not positions: 
            return
            
        # Handle empty positions gracefully
        if not positions.values():
            return
            
        # Extract all unique rows and columns
        rows = sorted(set(r for (r, c) in positions.values() if isinstance(r, (int, float))))
        cols = sorted(set(c for (r, c) in positions.values() if isinstance(c, (int, float))))
        
        # Handle edge cases
        if not rows or not cols:
            return
            
        # Create mapping to compact grid (starting from 0)
        row_map = {r: i for i, r in enumerate(rows)}
        col_map = {c: i for i, c in enumerate(cols)}
        
        # Update positions with normalized coordinates
        for wid, (r, c) in list(positions.items()):
            if isinstance(r, (int, float)) and isinstance(c, (int, float)):
                if r in row_map and c in col_map:
                    positions[wid] = (row_map[r], col_map[c])
                else:
                    # Handle invalid positions by placing at (0, 0)
                    positions[wid] = (0, 0)
            else:
                # Handle non-numeric positions
                positions[wid] = (0, 0)
        
        # Ensure all positions are valid integers
        for wid, (r, c) in list(positions.items()):
            positions[wid] = (int(r), int(c))

    # --- HEAVILY MODIFIED: Core logic now processes an array, not a dict ---
    def update_data(self, packet: list):
        if packet is None or not isinstance(packet, (list, tuple)):
            return
        timestamp = time.time()

        # Track packets and bytes for status bar
        self.total_packets += 1
        # Estimate bytes (each value as 4 bytes for simplicity)
        self.total_rx_bytes += len(packet) * 4

        # Iterate through the user-defined parameters, not the incoming data keys
        for param_meta in self.parameters:
            param_id = param_meta['id']
            array_idx = param_meta.get('array_index')

            # Check if the parameter has a valid index and if the index is within the packet bounds
            if array_idx is not None and 0 <= array_idx < len(packet):
                raw_value = packet[array_idx]
                if raw_value is None: 
                    continue  # Skip if data for this channel is null

                # Apply filters to get filtered value
                filtered_value = self.filter_manager.apply_filters(param_id, raw_value, timestamp)

                # Store RAW value in history (for logging)
                if param_id not in self.data_history: 
                    self.data_history[param_id] = []
                self.data_history[param_id].append({
                    'value': raw_value,  # Store raw value
                    'filtered_value': filtered_value,  # Also store filtered value
                    'timestamp': timestamp
                })
                self.data_history[param_id] = self.data_history[param_id][-500:]  # Limit history
        
        # Log RAW data (not filtered) if logging is enabled
        if self.data_logger.is_logging:
            self.data_logger.log_data(packet, self.data_history)

        # Send RAW data to raw telemetry monitor if open
        if self.raw_tlm_monitor and self.raw_tlm_monitor.isVisible():
            self.raw_tlm_monitor.append_packet(packet)


    def update_dashboard_ui(self):
        """
        @brief Update dashboard widgets at a fixed frame rate.
        @details Called by QTimer to refresh UI elements using the latest data.
        """
        # Only update visible tab to save resources
        current_tab_idx = self.tab_widget.currentIndex()
        if current_tab_idx < 0:
            return
            
        tab_info = self.tab_data.get(current_tab_idx)
        if not tab_info:
            return

        # Iterate through widgets in the current tab
        for widget_id, widget in tab_info['widgets'].items():
            config = tab_info['configs'].get(widget_id)
            if not config:
                continue
                
            # Check if widget is visible
            if not widget.isVisible():
                continue

            # Update based on widget type
            if isinstance(widget, ValueCard):
                # ValueCard now accepts a dict of values
                values = {}
                for pid in config['param_ids']:
                    if pid in self.data_history and self.data_history[pid]:
                        values[pid] = self.data_history[pid][-1]['filtered_value']
                widget.update_values(values)
            
            elif isinstance(widget, GaugeWidget):
                    if config['param_ids']:
                        pid = config['param_ids'][0]
                        if pid in self.data_history and self.data_history[pid]:
                            val = self.data_history[pid][-1]['filtered_value']
                            widget.update_value(val)

            elif isinstance(widget, LEDWidget):
                # LEDWidget now accepts a dict of values
                values = {}
                for pid in config['param_ids']:
                    if pid in self.data_history and self.data_history[pid]:
                        values[pid] = self.data_history[pid][-1]['filtered_value']
                widget.update_values(values)

            elif isinstance(widget, TimeGraph):
                    # Create filtered history for graphs
                    filtered_history = {}
                    has_data = False
                    for pid in config['param_ids']:
                        if pid in self.data_history:
                            # Optimization: Only pass the last N points if history is huge?
                            # For now, pass all, but TimeGraph should handle downsampling
                            filtered_history[pid] = [
                                {'value': dp['filtered_value'], 'timestamp': dp['timestamp']}
                                for dp in self.data_history[pid]
                            ]
                            has_data = True
                    if has_data:
                        widget.update_data(filtered_history)

            elif isinstance(widget, HistogramWidget):
                if config['param_ids']:
                    pid = config['param_ids'][0]
                    if pid in self.data_history:
                        hist_vals = [dp['filtered_value'] for dp in self.data_history[pid]]
                        widget.update_histogram(hist_vals)

            elif isinstance(widget, MapWidget):
                # Map widget handles its own history extraction usually, or we pass full history
                widget.update_position(self.data_history)
            
            elif isinstance(widget, LogTable):
                # LogTable might need specific handling to not refresh too often
                # It usually shows the latest value for a param
                if config['param_ids']:
                    pid = config['param_ids'][0]
                    widget.update_data(pid, self.data_history)
        


    def restart_simulator(self):
        if self.simulator: 
            self.simulator.stop()
            self.simulator.wait()
        
        # Create new simulator with connection settings and parameters
        self.simulator = DataSimulator(num_channels=32, connection_settings=self.connection_settings, parameters=self.parameters)
        
        # CRITICAL: Set mode based on connection settings
        conn_mode = self.connection_settings.get('mode', 'dummy')
        if conn_mode == 'dummy':
            self.simulator.mode = "dummy"
        else:
            # For serial, tcp, udp - all use backend mode
            self.simulator.mode = "backend"
        
        # Connect the signal for both modes
        self.simulator.newData.connect(self.update_data)
        self.simulator.start()
        
        # Give the connection a moment to establish
        QTimer.singleShot(500, self.update_connection_status)

    # --- All other MainWindow methods are unchanged ---

    def _handle_dock_close(self, widget_id):
        #Called when the dock is closed using the title bar button
        index = self.tab_widget.currentIndex()
        if index < 0:
            return

        tab_info = self.tab_data.get(index)
        if not tab_info:
            return

        if widget_id in tab_info['docks']:
            tab_info['docks'][widget_id].deleteLater()
            del tab_info['docks'][widget_id]
        if widget_id in tab_info['widgets']:
            del tab_info['widgets'][widget_id]
        if widget_id in tab_info['configs']:
            del tab_info['configs'][widget_id]
        if 'layout_positions' in tab_info and widget_id in tab_info['layout_positions']:
            del tab_info['layout_positions'][widget_id]

        self.refresh_active_displays_list()
        self.mark_as_unsaved()

    def open_add_widget_dialog(self):
        index = self.tab_widget.currentIndex()
        if index < 0: QMessageBox.warning(self, "No Tab", "No active tab to add a widget to."); return
        dialog = AddWidgetDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            widget_config = dialog.get_selection()
            # Use Command for Undo/Redo
            command = AddWidgetCommand(self, widget_config, index)
            self.dashboard_history.push(command)
            self.has_unsaved_changes = True
            self.update_window_title()

    def _add_widget_internal(self, config, tab_idx, restore_id=None):
        """Internal method to add a widget, used by Command"""
        if tab_idx not in self.tab_data:
            return None
            
        tab_info = self.tab_data[tab_idx]
        widget_id = restore_id or str(uuid.uuid4())
        
        # Create widget instance
        param_configs = [p for p in self.parameters if p['id'] in config['param_ids']]
        if not param_configs:
            return None
            
        widget = None
        if config['displayType'] == 'Time Graph':
            # Assign colors to param_configs for graph display
            for p_config in param_configs:
                p_config['color'] = self.graph_color_palette[self.next_graph_color_index % len(self.graph_color_palette)]
                self.next_graph_color_index += 1
            widget = TimeGraph(param_configs)
        elif config['displayType'] == 'Log Table':
            widget = LogTable(param_configs)
        elif config['displayType'] == 'Instant Value':
            widget = ValueCard(param_configs, config['priority'])
        elif config['displayType'] == 'Gauge' and len(param_configs) == 1:
            widget = GaugeWidget(param_configs[0], config.get('options'))
        elif config['displayType'] == 'Histogram' and len(param_configs) == 1:
            widget = HistogramWidget(param_configs[0])
        elif config['displayType'] == 'LED Indicator':
            widget = LEDWidget(param_configs, config.get('options'))
        elif config['displayType'] == 'Map (GPS)' and len(param_configs) == 2:
            widget = MapWidget(param_configs)
        
        if widget:
            # Wrap in dock
            mainwindow = tab_info['mainwindow']
            dock = ClosableDock(config['displayType'], mainwindow, widget_id=widget_id)
            dock.setWidget(widget)
            dock.closed.connect(self.remove_widget_by_id)
            
            # Connect edit signal with explicit lambda
            dock.edit_requested.connect(lambda wid: self.edit_widget(wid))
            
            # Store in tab_data
            tab_info['widgets'][widget_id] = widget
            tab_info['configs'][widget_id] = config
            tab_info['docks'][widget_id] = dock
            
            # Add to the tab's QMainWindow
            mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
            
            # Ensure new widget is visible and on top
            dock.show()
            dock.raise_()
            
            # Arrange widgets
            self._tile_evenly_safe(tab_idx)
            
            self.refresh_active_displays_list()
            
            return widget_id
        return None
    
    @Slot(str)
    def edit_widget(self, widget_id):
        """Open edit dialog for existing widget"""
        # Find the widget configuration
        for tab_idx, tab_info in self.tab_data.items():
            if widget_id in tab_info['configs']:
                config = tab_info['configs'][widget_id]
                
                # Open AddWidgetDialog in edit mode
                dialog = AddWidgetDialog(self.parameters, self, edit_mode=True, existing_config=config)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_config = dialog.get_selection()
                    
                    # Remove old widget
                    self._remove_widget_internal(widget_id, tab_idx)
                    
                    # Add new widget with same ID
                    self._add_widget_internal(new_config, tab_idx, restore_id=widget_id)
                    
                    self.has_unsaved_changes = True
                    self.update_window_title()
                break

    def _remove_widget_internal(self, widget_id, tab_idx):
        """Internal method to remove a widget, used by Command"""
        if tab_idx in self.tab_data:
            tab_info = self.tab_data[tab_idx]
            if widget_id in tab_info['widgets']:
                dock = tab_info['docks'][widget_id]
                # Hide immediately for instant visual feedback
                dock.hide()
                dock.deleteLater()
                
                del tab_info['widgets'][widget_id]
                del tab_info['configs'][widget_id]
                del tab_info['docks'][widget_id]
                
                # Clean up layout positions
                if 'layout_positions' in tab_info and widget_id in tab_info['layout_positions']:
                    del tab_info['layout_positions'][widget_id]
                    # Normalize positions after removal
                    self._normalize_positions(tab_info['layout_positions'])

    def _get_widget_config(self, widget_id, tab_idx):
        """Helper to get config for undo"""
        if tab_idx in self.tab_data:
            return self.tab_data[tab_idx]['configs'].get(widget_id)
        return None

    def remove_widget_by_id(self, widget_id):
        # Find which tab has this widget
        for tab_idx, info in self.tab_data.items():
            if widget_id in info['widgets']:
                # Use Command
                command = RemoveWidgetCommand(self, widget_id, tab_idx)
                self.dashboard_history.push(command)
                self.has_unsaved_changes = True
                self.update_window_title()
                break
        self.refresh_active_displays_list() # Refresh list after command is pushed and executed
        
    def remove_selected_display(self):
        """Remove a widget via dialog selection"""
        index = self.tab_widget.currentIndex()
        if index < 0: 
            QMessageBox.warning(self, "No Tab", "No active tab.")
            return
        
        tab_info = self.tab_data.get(index)
        if not tab_info or not tab_info['configs']:
            QMessageBox.information(self, "No Widgets", "No widgets to remove in current tab.")
            return
        
        # Create a selection dialog
        widget_names = []
        widget_ids = []
        for widget_id, config in tab_info['configs'].items():
            param_names = [p['name'] for p in self.parameters if p['id'] in config['param_ids']]
            display_name = f"{', '.join(param_names)} ({config['displayType']})"
            widget_names.append(display_name)
            widget_ids.append(widget_id)
        
        item, ok = QInputDialog.getItem(
            self, 
            "Remove Widget", 
            "Select widget to remove:",
            widget_names,
            0,
            False
        )
        
        if ok and item:
            # Find the widget_id for the selected item
            selected_index = widget_names.index(item)
            widget_id = widget_ids[selected_index]
            
            # Remove the widget
            if widget_id in tab_info['docks']:
                tab_info['docks'][widget_id].deleteLater()
                del tab_info['docks'][widget_id]
            if widget_id in tab_info['widgets']:
                del tab_info['widgets'][widget_id]
            if widget_id in tab_info['configs']:
                del tab_info['configs'][widget_id]
            if 'layout_positions' in tab_info and widget_id in tab_info['layout_positions']:
                del tab_info['layout_positions'][widget_id]
            
            self.refresh_active_displays_list()
            self.mark_as_unsaved()

    def refresh_active_displays_list(self):
        self.active_displays_list.clear(); index = self.tab_widget.currentIndex()
        if index < 0 or index not in self.tab_data: return
        tab_info = self.tab_data.get(index)
        for widget_id, config in tab_info['configs'].items():
            param_names = [p['name'] for p in self.parameters if p['id'] in config['param_ids']]
            display_name = f"{', '.join(param_names)} ({config['displayType']})"
            item = QListWidgetItem(display_name); item.setData(Qt.ItemDataRole.UserRole, widget_id)
            self.active_displays_list.addItem(item)
    def manage_parameters(self):
        """Open dialog to manage parameters"""
        dialog = ManageParametersDialog(self.parameters, self, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Parameters are updated in-place or via commands, but we might need to refresh UI
            self.restart_simulator()
            self.has_unsaved_changes = True
            self.update_window_title() 
            self.mark_as_unsaved()
            QMessageBox.information(self, "Update", "Parameter definitions have been updated.")

    def update_filter_menus(self):
        """Update filter submenus with current parameters"""
        # Clear existing actions
        for menu in self.filter_submenus.values():
            menu.clear()
        
        # If no parameters, show disabled message
        if not self.parameters:
            for menu in self.filter_submenus.values():
                no_params_action = QAction("(No parameters available)", self)
                no_params_action.setEnabled(False)
                menu.addAction(no_params_action)
            return
        
        # Add parameter actions to each filter type menu
        for param in self.parameters:
            param_id = param['id']
            param_name = param['name']
            
            # Check if this parameter has any filters
            existing_filters = self.filter_manager.get_filters(param_id)
            filter_count = len(existing_filters)
            
            # Add visual indicator if filters exist
            if filter_count > 0:
                display_name = f"{param_name}  [🔧 {filter_count}]"
            else:
                display_name = param_name
            
            # Moving Average submenu
            ma_action = QAction(display_name, self)
            ma_action.triggered.connect(lambda checked, pid=param_id, pname=param_name: 
                                    self.add_filter_to_parameter(pid, pname, 'moving_average'))
            self.filter_submenus['moving_average'].addAction(ma_action)
            
            # Low Pass submenu
            lp_action = QAction(display_name, self)
            lp_action.triggered.connect(lambda checked, pid=param_id, pname=param_name: 
                                    self.add_filter_to_parameter(pid, pname, 'low_pass'))
            self.filter_submenus['low_pass'].addAction(lp_action)
            
            # Kalman submenu
            k_action = QAction(display_name, self)
            k_action.triggered.connect(lambda checked, pid=param_id, pname=param_name: 
                                    self.add_filter_to_parameter(pid, pname, 'kalman'))
            self.filter_submenus['kalman'].addAction(k_action)
            
            # Median submenu
            m_action = QAction(display_name, self)
            m_action.triggered.connect(lambda checked, pid=param_id, pname=param_name: 
                                    self.add_filter_to_parameter(pid, pname, 'median'))
            self.filter_submenus['median'].addAction(m_action)

    def add_filter_to_parameter(self, param_id, param_name, filter_type):
        """Add a specific filter type to a parameter"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QSpinBox
        
        # Create configuration dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {filter_type.replace('_', ' ').title()} Filter to {param_name}")
        dialog.setMinimumWidth(350)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        # Different parameters for different filter types
        if filter_type == 'moving_average':
            window_spin = QSpinBox()
            window_spin.setRange(2, 100)
            window_spin.setValue(5)
            form.addRow("Window Size:", window_spin)
            
        elif filter_type == 'low_pass':
            alpha_spin = QDoubleSpinBox()
            alpha_spin.setRange(0.01, 1.0)
            alpha_spin.setSingleStep(0.05)
            alpha_spin.setValue(0.3)
            alpha_spin.setDecimals(2)
            form.addRow("Alpha (0-1, lower=smoother):", alpha_spin)
            
        elif filter_type == 'kalman':
            process_var_spin = QDoubleSpinBox()
            process_var_spin.setRange(0.001, 10.0)
            process_var_spin.setSingleStep(0.01)
            process_var_spin.setValue(0.01)
            process_var_spin.setDecimals(3)
            form.addRow("Process Variance:", process_var_spin)
            
            measurement_var_spin = QDoubleSpinBox()
            measurement_var_spin.setRange(0.001, 10.0)
            measurement_var_spin.setSingleStep(0.1)
            measurement_var_spin.setValue(0.1)
            measurement_var_spin.setDecimals(3)
            form.addRow("Measurement Variance:", measurement_var_spin)
            
        elif filter_type == 'median':
            window_spin = QSpinBox()
            window_spin.setRange(3, 101)
            window_spin.setSingleStep(2)
            window_spin.setValue(5)
            form.addRow("Window Size (odd):", window_spin)
        
        layout.addLayout(form)
        
        # Add buttons
        from PySide6.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Create the filter based on type
            filter_id = str(uuid.uuid4())
            
            if filter_type == 'moving_average':
                filter_obj = MovingAverageFilter(filter_id, window_spin.value())
            elif filter_type == 'low_pass':
                filter_obj = LowPassFilter(filter_id, alpha_spin.value())
            elif filter_type == 'kalman':
                filter_obj = KalmanFilter(filter_id, process_var_spin.value(), measurement_var_spin.value())
            elif filter_type == 'median':
                filter_obj = MedianFilter(filter_id, window_spin.value())
            else:
                return
            
            # Add to filter manager
            self.filter_manager.add_filter(param_id, filter_obj)
            self.mark_as_unsaved()
            
            QMessageBox.information(self, "Filter Added", 
                                f"{filter_obj.filter_name} filter added to parameter '{param_name}'")
            self.update_filter_menus() 

    def open_manage_filters_dialog(self):
        """Open dialog to manage all filters"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Filters")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Tree widget to show parameters and their filters
        tree = QTreeWidget()
        tree.setHeaderLabels(["Parameter / Filter", "Type", "Status", "Details"])
        tree.setColumnWidth(0, 200)
        
        # Populate tree
        for param in self.parameters:
            param_id = param['id']
            param_name = param['name']
            filters = self.filter_manager.get_filters(param_id)
            
            # Create parameter item
            param_item = QTreeWidgetItem([param_name, "", "", f"{len(filters)} filter(s)"])
            param_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'parameter', 'param_id': param_id})
            
            # Add filter children
            for filter_obj in filters:
                status = "Enabled" if filter_obj.enabled else "Disabled"
                details = ""
                
                if isinstance(filter_obj, MovingAverageFilter):
                    details = f"Window: {filter_obj.window_size}"
                elif isinstance(filter_obj, LowPassFilter):
                    details = f"Alpha: {filter_obj.alpha:.2f}"
                elif isinstance(filter_obj, KalmanFilter):
                    details = f"Q: {filter_obj.process_variance:.3f}, R: {filter_obj.measurement_variance:.3f}"
                elif isinstance(filter_obj, MedianFilter):
                    details = f"Window: {filter_obj.window_size}"
                
                filter_item = QTreeWidgetItem([f"  → {filter_obj.filter_name}", 
                                            filter_obj.__class__.__name__, 
                                            status, 
                                            details])
                filter_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'type': 'filter',
                    'param_id': param_id,
                    'filter_id': filter_obj.filter_id,
                    'filter_obj': filter_obj
                })
                param_item.addChild(filter_item)
            
            tree.addTopLevelItem(param_item)
        
        tree.expandAll()
        layout.addWidget(tree)
        
        # Buttons
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add Filter...")
        add_btn.clicked.connect(lambda: self.add_filter_from_tree(tree, dialog))

        enable_btn = QPushButton("Enable/Disable")
        enable_btn.clicked.connect(lambda: self.toggle_filter_from_tree(tree))

        remove_btn = QPushButton("Remove Filter")
        remove_btn.clicked.connect(lambda: self.remove_filter_from_tree(tree))

        reset_btn = QPushButton("Reset Filter State")
        reset_btn.clicked.connect(lambda: self.reset_filter_from_tree(tree))

        close_btn = QPushButton("Close")

        close_btn.clicked.connect(dialog.accept)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(enable_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def add_filter_from_tree(self, tree, parent_dialog):
        """Add a new filter to the selected parameter from the tree"""
        item = tree.currentItem()
        
        # Get parameter ID - either from selected parameter or from selected filter's parent
        param_id = None
        param_name = None
        
        if item:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                if data.get('type') == 'parameter':
                    # Selected a parameter directly
                    param_id = data['param_id']
                    param_name = item.text(0)
                elif data.get('type') == 'filter':
                    # Selected a filter - get parent parameter
                    param_id = data['param_id']
                    parent = item.parent()
                    if parent:
                        param_name = parent.text(0)
        
        if not param_id:
            QMessageBox.information(parent_dialog, "No Selection", 
                                "Please select a parameter to add a filter to.")
            return
        
        # Show filter type selection dialog
        from PySide6.QtWidgets import QInputDialog
        
        filter_types = ["Moving Average", "Low Pass", "Kalman", "Median"]
        filter_type, ok = QInputDialog.getItem(
            parent_dialog, 
            f"Add Filter to {param_name}",
            "Select filter type:",
            filter_types,
            0,
            False
        )
        
        if not ok:
            return
        
        # Map display name to internal name
        filter_type_map = {
            "Moving Average": "moving_average",
            "Low Pass": "low_pass",
            "Kalman": "kalman",
            "Median": "median"
        }
        
        internal_type = filter_type_map[filter_type]
        
        # Show configuration dialog
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QSpinBox, QDialogButtonBox
        
        config_dialog = QDialog(parent_dialog)
        config_dialog.setWindowTitle(f"Configure {filter_type}")
        config_dialog.setMinimumWidth(350)
        
        layout = QVBoxLayout(config_dialog)
        form = QFormLayout()
        
        # Different parameters for different filter types
        if internal_type == 'moving_average':
            window_spin = QSpinBox()
            window_spin.setRange(2, 100)
            window_spin.setValue(5)
            form.addRow("Window Size:", window_spin)
            
        elif internal_type == 'low_pass':
            alpha_spin = QDoubleSpinBox()
            alpha_spin.setRange(0.01, 1.0)
            alpha_spin.setSingleStep(0.05)
            alpha_spin.setValue(0.3)
            alpha_spin.setDecimals(2)
            form.addRow("Alpha (0-1, lower=smoother):", alpha_spin)
            
        elif internal_type == 'kalman':
            process_var_spin = QDoubleSpinBox()
            process_var_spin.setRange(0.001, 10.0)
            process_var_spin.setSingleStep(0.01)
            process_var_spin.setValue(0.01)
            process_var_spin.setDecimals(3)
            form.addRow("Process Variance:", process_var_spin)
            
            measurement_var_spin = QDoubleSpinBox()
            measurement_var_spin.setRange(0.001, 10.0)
            measurement_var_spin.setSingleStep(0.1)
            measurement_var_spin.setValue(0.1)
            measurement_var_spin.setDecimals(3)
            form.addRow("Measurement Variance:", measurement_var_spin)
            
        elif internal_type == 'median':
            window_spin = QSpinBox()
            window_spin.setRange(3, 101)
            window_spin.setSingleStep(2)
            window_spin.setValue(5)
            form.addRow("Window Size (odd):", window_spin)
        
        layout.addLayout(form)
        
        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(config_dialog.accept)
        buttons.rejected.connect(config_dialog.reject)
        layout.addWidget(buttons)
        
        # Show dialog
        if config_dialog.exec() == QDialog.DialogCode.Accepted:
            # Create the filter based on type
            filter_id = str(uuid.uuid4())
            
            if internal_type == 'moving_average':
                filter_obj = MovingAverageFilter(filter_id, window_spin.value())
            elif internal_type == 'low_pass':
                filter_obj = LowPassFilter(filter_id, alpha_spin.value())
            elif internal_type == 'kalman':
                filter_obj = KalmanFilter(filter_id, process_var_spin.value(), measurement_var_spin.value())
            elif internal_type == 'median':
                filter_obj = MedianFilter(filter_id, window_spin.value())
            else:
                return
            
            # Add to filter manager
            self.filter_manager.add_filter(param_id, filter_obj)
            self.mark_as_unsaved()
            
            # Refresh the tree to show the new filter
            self.refresh_manage_filters_tree(tree)
            
            QMessageBox.information(parent_dialog, "Filter Added", 
                                f"{filter_obj.filter_name} filter added to parameter '{param_name}'")
            self.update_filter_menus()

    def refresh_manage_filters_tree(self, tree):
        """Refresh the filter management tree widget"""
        from PySide6.QtWidgets import QTreeWidgetItem  # Add this line
        
        tree.clear()
        
        # Populate tree
        for param in self.parameters:
            param_id = param['id']
            param_name = param['name']
            filters = self.filter_manager.get_filters(param_id)
            
            # Create parameter item
            param_item = QTreeWidgetItem([param_name, "", "", f"{len(filters)} filter(s)"])
            param_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'parameter', 'param_id': param_id})
            
            # Add filter children
            for filter_obj in filters:
                status = "Enabled" if filter_obj.enabled else "Disabled"
                details = ""
                
                if isinstance(filter_obj, MovingAverageFilter):
                    details = f"Window: {filter_obj.window_size}"
                elif isinstance(filter_obj, LowPassFilter):
                    details = f"Alpha: {filter_obj.alpha:.2f}"
                elif isinstance(filter_obj, KalmanFilter):
                    details = f"Q: {filter_obj.process_variance:.3f}, R: {filter_obj.measurement_variance:.3f}"
                elif isinstance(filter_obj, MedianFilter):
                    details = f"Window: {filter_obj.window_size}"
                
                filter_item = QTreeWidgetItem([f"  → {filter_obj.filter_name}", 
                                            filter_obj.__class__.__name__, 
                                            status, 
                                            details])
                filter_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'type': 'filter',
                    'param_id': param_id,
                    'filter_id': filter_obj.filter_id,
                    'filter_obj': filter_obj
                })
                param_item.addChild(filter_item)
            
            tree.addTopLevelItem(param_item)
        
        tree.expandAll()

    def toggle_filter_from_tree(self, tree):
        """Toggle filter enabled/disabled state"""
        item = tree.currentItem()
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('type') == 'filter':
            filter_obj = data['filter_obj']
            filter_obj.enabled = not filter_obj.enabled
            status = "Enabled" if filter_obj.enabled else "Disabled"
            item.setText(2, status)
            self.mark_as_unsaved()

    def remove_filter_from_tree(self, tree):
        """Remove selected filter"""
        item = tree.currentItem()
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('type') == 'filter':
            reply = QMessageBox.question(self, "Remove Filter",
                                        "Are you sure you want to remove this filter?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.filter_manager.remove_filter(data['param_id'], data['filter_id'])
                parent = item.parent()
                parent.removeChild(item)
                parent.setText(3, f"{parent.childCount()} filter(s)")
                self.mark_as_unsaved()
                self.refresh_manage_filters_tree(tree)
                self.update_filter_menus()

    def reset_filter_from_tree(self, tree):
        """Reset filter state (clear buffer/history)"""
        item = tree.currentItem()
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('type') == 'filter':
            filter_obj = data['filter_obj']
            filter_obj.reset()
            QMessageBox.information(self, "Filter Reset", "Filter state has been reset.")

    def import_custom_filter(self):
        """Import custom filter from JSON file"""
        QMessageBox.information(self, "Coming Soon", 
                            "Custom filter import functionality will be available in a future update.")

    def update_control_states(self):
        has_params = bool(self.parameters)
        if hasattr(self, 'add_widget_btn') and self.add_widget_btn:
            self.add_widget_btn.setEnabled(has_params)
    def add_new_tab(self, name=None, is_closable=True):
        if name is None:
            name, ok = QInputDialog.getText(self, "New Tab", "Enter tab name:")
            if not ok or not name: return
        tab_main_window = QMainWindow()
        tab_main_window.setDockNestingEnabled(True)
        # Ensure proper dock widget area setup
        tab_main_window.setCentralWidget(None)  # Clear any central widget
        tab_index = self.tab_widget.addTab(tab_main_window, name)
        self.tab_data[tab_index] = {
            'mainwindow': tab_main_window, 
            'widgets': {}, 
            'docks': {}, 
            'configs': {},
            'is_floating': False,
            'floating_window': None,
            'layout_positions': {}  # Initialize layout positions
        }
        if not is_closable:
            self.tab_widget.tabBar().setTabButton(tab_index, QTabBar.ButtonPosition.RightSide, None)
        self.tab_widget.setCurrentIndex(tab_index)
        return tab_index

    def _setup_tab_double_click(self):
        """Setup double-click handler for tab bar"""
        self.tab_widget.tabBar().setMouseTracking(True)
        self.tab_widget.tabBar().mouseDoubleClickEvent = self._on_tab_double_click

    def _on_tab_double_click(self, event):
        """Handle double-click on tab to float/unfloat"""
        tab_index = self.tab_widget.tabBar().tabAt(event.pos())
        if tab_index >= 0:
            self.toggle_float_tab(tab_index)

    def toggle_float_tab(self, tab_index):
        """Toggle tab between docked and floating state"""
        if tab_index not in self.tab_data:
            return
        
        tab_info = self.tab_data[tab_index]
        
        if tab_info['is_floating']:
            # Dock the tab back
            self._dock_tab(tab_index)
        else:
            # Float the tab
            self._float_tab(tab_index)

    def _float_tab(self, tab_index):
        """Detach tab into floating window"""
        tab_info = self.tab_data[tab_index]
        tab_name = self.tab_widget.tabText(tab_index)
        
        # Create floating window
        floating_window = QMainWindow()
        floating_window.setWindowTitle(f"{tab_name} - Glance")
        floating_window.setMinimumSize(800, 600)
        
        # Get current tab widget
        tab_main_window = tab_info['mainwindow']
        
        # Store the tab name before removing
        tab_info['stored_tab_name'] = tab_name
        tab_info['stored_tab_index'] = tab_index
        
        # Remove from tab widget (but don't delete)
        self.tab_widget.removeTab(tab_index)
        
        # Set as central widget of floating window
        floating_window.setCentralWidget(tab_main_window)
        
        # Update tab info
        tab_info['is_floating'] = True
        tab_info['floating_window'] = floating_window
        
        # Add menu bar to floating window
        self._add_floating_window_menu(floating_window, tab_index, tab_name)
        
        # Show floating window
        floating_window.show()
        floating_window.raise_()
        floating_window.activateWindow()
        
        # Handle close event
        original_close = floating_window.closeEvent
        def on_close(event):
            # Only dock if not being destroyed during app shutdown
            if not self.isHidden():
                self._dock_tab(tab_index)
            if original_close:
                original_close(event)
            event.accept()
        
        floating_window.closeEvent = on_close

    def _dock_tab(self, tab_index):
        """Dock floating tab back to main window"""
        if tab_index not in self.tab_data:
            return
        
        tab_info = self.tab_data[tab_index]
        
        if not tab_info.get('is_floating', False):
            return
        
        # Get the floating window
        floating_window = tab_info.get('floating_window')
        
        if not floating_window:
            return
        
        # Get the main window widget back
        tab_main_window = floating_window.centralWidget()
        
        if not tab_main_window:
            return
        
        # Disconnect from floating window
        floating_window.setCentralWidget(None)
        
        # Get stored tab name
        tab_name = tab_info.get('stored_tab_name', 'Tab')
        
        # Find a good position to insert (append to end)
        insert_position = self.tab_widget.count()
        
        # Add back to tab widget
        new_index = self.tab_widget.addTab(tab_main_window, tab_name)
        
        # Update tab info
        tab_info['is_floating'] = False
        tab_info['floating_window'] = None
        
        # Close floating window
        try:
            floating_window.closeEvent = None  # Prevent recursion
            floating_window.close()
            floating_window.deleteLater()
        except:
            pass
        # Switch to the docked tab
        self.tab_widget.setCurrentIndex(new_index)
        
        # If the index changed, update the mapping
        if new_index != tab_index:
            # We need to be careful here. tab_index is the OLD index.
            # But wait, tab_index was removed from tab_widget earlier in _float_tab?
            # No, _float_tab calls removeTab(tab_index).
            # So when we call addTab, we get a NEW index.
            # The tab_data still has the OLD index as key.
            # We must move the data to the NEW index key.
            
            # Check if target index already exists (collision)
            if new_index in self.tab_data:
                # This shouldn't happen if indices are strictly managed, but let's be safe
                # Shift existing data? Or just overwrite?
                # Actually, QTabWidget indices shift when tabs are removed/added.
                # We need to re-sync ALL tab_data keys with current QTabWidget indices.
                pass

            self.tab_data[new_index] = self.tab_data.pop(tab_index)
            
            # We should probably re-index everything to be safe
            self._reindex_tabs()

    def _reindex_tabs(self):
        """Re-sync tab_data keys with current QTabWidget indices"""
        new_tab_data = {}
        
        # Create a mapping of mainwindow -> tab_info
        mw_to_info = {}
        for idx, info in self.tab_data.items():
            mw_to_info[info['mainwindow']] = info
            
        # Iterate through current tabs in QTabWidget
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if widget in mw_to_info:
                new_tab_data[i] = mw_to_info[widget]
            else:
                print(f"Warning: Tab at index {i} has no data")
                
        # Handle floating tabs
        for idx, info in self.tab_data.items():
            if info.get('is_floating', False):
                # Find a free key for floating tabs
                new_key = 1000
                while new_key in new_tab_data:
                    new_key += 1
                new_tab_data[new_key] = info
                    
        self.tab_data = new_tab_data

    def _enable_dock_drag_drop(self):
        """Enable drag and drop for dock widgets across tabs"""
        # This is automatically handled by Qt's dock system
        # We just need to handle cross-tab transfers
        pass

    def _add_dock_context_menu_transfer(self, dock, pos):
        """Enhanced dock context menu with transfer option"""
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # Store the dock reference
        self._context_dock = dock
        current_index = self.tab_widget.currentIndex()
        tinfo = self.tab_data.get(current_index, {})
        widget_id = None
        
        for wid, d in tinfo.get('docks', {}).items():
            if d == dock:
                widget_id = wid
                break
        
        if widget_id:
            # Existing actions
            rename_action = menu.addAction("Rename Widget")
            rename_action.triggered.connect(self._rename_widget_direct)
            
            float_action = menu.addAction("Float / Dock")
            float_action.triggered.connect(self._toggle_float_direct)
            
            menu.addSeparator()
            
            # NEW: Transfer to tab submenu
            if self.tab_widget.count() > 1:
                transfer_menu = menu.addMenu("Move to Tab")
                
                for i in range(self.tab_widget.count()):
                    if i != current_index:  # Don't show current tab
                        tab_name = self.tab_widget.tabText(i)
                        transfer_action = transfer_menu.addAction(tab_name)
                        transfer_action.triggered.connect(
                            lambda checked, src=current_index, dst=i, wid=widget_id: 
                            self._transfer_widget_to_tab(src, dst, wid)
                        )
                
                menu.addSeparator()
            
            close_action = menu.addAction("Close Widget")
            close_action.triggered.connect(self._close_widget_direct)
            
            menu.addSeparator()
            
            tile_action = menu.addAction("Tile Evenly")
            tile_action.triggered.connect(lambda: self._tile_evenly_safe(current_index))
        else:
            menu.addAction("No actions available")
        
        menu.exec(dock.mapToGlobal(pos))

    def _transfer_widget_to_tab(self, source_tab_index, dest_tab_index, widget_id):
        """Transfer a widget from one tab to another"""
        source_tab = self.tab_data.get(source_tab_index)
        dest_tab = self.tab_data.get(dest_tab_index)
        
        if not source_tab or not dest_tab:
            return
        
        if widget_id not in source_tab['docks']:
            return
        
        # Get widget information
        dock = source_tab['docks'][widget_id]
        widget = source_tab['widgets'][widget_id]
        config = source_tab['configs'][widget_id]
        
        # Get dock title for the new tab
        dock_title = dock.windowTitle()
        
        # Remove from source tab
        source_main_window = source_tab['mainwindow']
        source_main_window.removeDockWidget(dock)
        
        # Remove from source tracking
        del source_tab['docks'][widget_id]
        del source_tab['widgets'][widget_id]
        del source_tab['configs'][widget_id]
        if 'layout_positions' in source_tab and widget_id in source_tab['layout_positions']:
            del source_tab['layout_positions'][widget_id]
        
        # Create new dock in destination tab
        dest_main_window = dest_tab['mainwindow']
        
        # Create a new dock widget (we can't move the old one directly)
        new_dock = QDockWidget(dock_title, self)
        new_dock.setObjectName(f"dock_{widget_id}")
        new_dock.setWidget(widget)
        new_dock.setMinimumSize(300, 200)
        
        # Add context menu
        new_dock.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        new_dock.customContextMenuRequested.connect(
            lambda pos, d=new_dock: self._add_dock_context_menu_transfer(d, pos)
        )
        
        # Add to destination tab
        dest_docks = list(dest_tab['docks'].values())
        if len(dest_docks) == 0:
            dest_main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, new_dock)
        else:
            # Add next to last dock
            dest_main_window.splitDockWidget(dest_docks[-1], new_dock, Qt.Orientation.Horizontal)
        
        # Update destination tracking
        dest_tab['docks'][widget_id] = new_dock
        dest_tab['widgets'][widget_id] = widget
        dest_tab['configs'][widget_id] = config
        
        # Update layout positions
        positions = dest_tab.setdefault('layout_positions', {})
        positions[widget_id] = self._next_grid_position(positions)
        
        # Clean up old dock
        dock.deleteLater()
        
        # Show the widget in new location
        new_dock.show()
        new_dock.raise_()
        
        # Switch to destination tab to show the result
        self.tab_widget.setCurrentIndex(dest_tab_index)
        
        # Refresh display list
        self.refresh_active_displays_list()
        
        QMessageBox.information(
            self, 
            "Widget Moved", 
            f"Widget moved to tab '{self.tab_widget.tabText(dest_tab_index)}'"
        )

    def _setup_tab_drag_drop(self):
        """Setup drag and drop handling between tabs"""
        # Make tab widget accept drops
        self.tab_widget.setAcceptDrops(True)
        self.tab_widget.dragEnterEvent = self._tab_drag_enter
        self.tab_widget.dragMoveEvent = self._tab_drag_move
        self.tab_widget.dropEvent = self._tab_drop

    def _tab_drag_enter(self, event):
        """Handle drag enter on tab widget"""
        # Accept if it's a dock widget being dragged
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    def _tab_drag_move(self, event):
        """Handle drag move on tab widget"""
        event.accept()

    def _tab_drop(self, event):
        """Handle drop on tab widget"""
        # Get the tab index where drop occurred
        tab_bar = self.tab_widget.tabBar()
        drop_pos = event.pos()
        
        # Find which tab we're over
        target_tab_index = -1
        for i in range(self.tab_widget.count()):
            tab_rect = tab_bar.tabRect(i)
            if tab_rect.contains(drop_pos):
                target_tab_index = i
                break
        
        if target_tab_index >= 0:
            event.accept()
        else:
            event.ignore()
    
    def _add_floating_window_menu(self, floating_window, tab_index, tab_name):
        """Add menu bar to floating window"""
        menubar = floating_window.menuBar()
        
        # Window menu
        window_menu = menubar.addMenu("Window")
        
        dock_action = QAction("Dock Tab", floating_window)
        dock_action.setShortcut("Ctrl+D")
        dock_action.triggered.connect(lambda: self._dock_tab(tab_index))
        window_menu.addAction(dock_action)
        
        window_menu.addSeparator()
        
        # Add fullscreen for floating window
        fullscreen_action = QAction("Toggle Fullscreen", floating_window)
        fullscreen_action.setShortcut("F11")
        
        # Store fullscreen state for this window
        floating_window._is_fullscreen = False
        floating_window._normal_geometry = None
        
        def toggle_floating_fullscreen():
            if floating_window._is_fullscreen:
                floating_window.showNormal()
                if floating_window._normal_geometry:
                    floating_window.setGeometry(floating_window._normal_geometry)
                menubar.setVisible(True)
                floating_window._is_fullscreen = False
            else:
                floating_window._normal_geometry = floating_window.geometry()
                menubar.setVisible(False)
                floating_window.showFullScreen()
                floating_window._is_fullscreen = True
        
        fullscreen_action.triggered.connect(toggle_floating_fullscreen)
        window_menu.addAction(fullscreen_action)
        
        window_menu.addSeparator()
        
        rename_action = QAction("Rename Tab", floating_window)
        rename_action.triggered.connect(lambda: self._rename_floating_tab(tab_index, floating_window))
        window_menu.addAction(rename_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        add_widget_action = QAction("Add Widget...", floating_window)
        add_widget_action.setShortcut("Ctrl+W")
        add_widget_action.triggered.connect(self.open_add_widget_dialog)
        view_menu.addAction(add_widget_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", floating_window)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        # Add key event handler for F11 and ESC to floating window
        original_key_press = floating_window.keyPressEvent
        def floating_key_press(event):
            if event.key() == Qt.Key.Key_F11:
                toggle_floating_fullscreen()
                event.accept()
            elif event.key() == Qt.Key.Key_Escape and floating_window._is_fullscreen:
                toggle_floating_fullscreen()
                event.accept()
            else:
                if original_key_press:
                    original_key_press(event)
        
        floating_window.keyPressEvent = floating_key_press

    def _rename_floating_tab(self, tab_index, floating_window):
        """Rename a floating tab"""
        current_name = floating_window.windowTitle().replace(" - Glance", "")
        new_name, ok = QInputDialog.getText(
            floating_window, 
            "Rename Tab", 
            "Enter new tab name:", 
            text=current_name
        )
        if ok and new_name:
            floating_window.setWindowTitle(f"{new_name} - Glance")

    def _setup_tab_context_menu(self):
        """Setup right-click context menu for tabs"""
        self.tab_widget.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.tabBar().customContextMenuRequested.connect(self._show_tab_context_menu)

    def _show_tab_context_menu(self, pos):
        """Show context menu for tab"""
        from PySide6.QtWidgets import QMenu
        
        tab_index = self.tab_widget.tabBar().tabAt(pos)
        if tab_index < 0:
            return
        
        menu = QMenu(self)
        
        # Float/Dock action
        tab_info = self.tab_data.get(tab_index, {})
        if tab_info.get('is_floating', False):
            float_action = menu.addAction("Dock Tab")
            float_action.triggered.connect(lambda: self._dock_tab(tab_index))
        else:
            float_action = menu.addAction("Float Tab")
            float_action.triggered.connect(lambda: self._float_tab(tab_index))
        
        menu.addSeparator()
        
        # Rename action
        rename_action = menu.addAction("Rename Tab")
        rename_action.triggered.connect(lambda: self.rename_tab_by_index(tab_index))
        
        # Close action (if closable)
        if self.tab_widget.tabBar().tabButton(tab_index, QTabBar.ButtonPosition.RightSide):
            menu.addSeparator()
            close_action = menu.addAction("Close Tab")
            close_action.triggered.connect(lambda: self.close_tab(tab_index))
        
        menu.exec(self.tab_widget.tabBar().mapToGlobal(pos))

    def rename_tab_by_index(self, index):
        """Rename tab by index"""
        if index < 0:
            return
        
        tab_info = self.tab_data.get(index)
        if not tab_info:
            return
        
        if tab_info['is_floating']:
            # Rename floating window
            floating_window = tab_info['floating_window']
            self._rename_floating_tab(index, floating_window)
        else:
            # Rename docked tab
            current_name = self.tab_widget.tabText(index)
            new_name, ok = QInputDialog.getText(
                self, 
                "Rename Tab", 
                "Enter new tab name:", 
                text=current_name
            )
            if ok and new_name:
                self.tab_widget.setTabText(index, new_name)

    def close_tab(self, index):
        if index < 0: 
            return
        
        # Handle both floating and docked tabs
        tab_info = None
        
        # First, try to find by direct index
        if index in self.tab_data:
            tab_info = self.tab_data[index]
        else:
            # If not found, might be because of reindexing, search by position
            for idx, info in list(self.tab_data.items()):
                if not info.get('is_floating', False):
                    # Check if this is the tab at position 'index'
                    tab_count = 0
                    for i in sorted(self.tab_data.keys()):
                        if not self.tab_data[i].get('is_floating', False):
                            if tab_count == index:
                                tab_info = self.tab_data[i]
                                index = i
                                break
                            tab_count += 1
                    if tab_info:
                        break
        
        if not tab_info:
            return
        
        # If floating, close the floating window first
        if tab_info.get('is_floating', False) and tab_info.get('floating_window'):
            try:
                tab_info['floating_window'].closeEvent = None  # Prevent recursion
                tab_info['floating_window'].close()
                tab_info['floating_window'].deleteLater()
            except:
                pass
        
        # Clean up docks
        for dock in tab_info.get('docks', {}).values():
            try:
                dock.deleteLater()
            except:
                pass
        
        # Clean up main window
        try:
            tab_info['mainwindow'].deleteLater()
        except:
            pass
        
        # Remove from data
        del self.tab_data[index]
        
        # Remove from tab widget if not already removed
        if not tab_info.get('is_floating', False):
            # Find actual position in tab widget
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == tab_info['mainwindow']:
                    self.tab_widget.removeTab(i)
                    break
        
        self.refresh_active_displays_list()

    def rename_current_tab(self):
        index = self.tab_widget.currentIndex()
        if index < 0: return
        current_name = self.tab_widget.tabText(index)
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new tab name:", text=current_name)
        if ok and new_name: self.tab_widget.setTabText(index, new_name)
    def on_tab_changed(self, index): self.refresh_active_displays_list()
    def get_alarm_state(self, value, thresholds):
        # Handle None or non-numeric values gracefully
        if value is None or not isinstance(value, (int, float)):
            return 'Nominal'

        # Validate thresholds structure and values
        required_keys = {'low_crit', 'low_warn', 'high_warn', 'high_crit'}
        if not isinstance(thresholds, dict) or not required_keys.issubset(thresholds.keys()):
            return 'Nominal'

        # Ensure all threshold values are numeric
        try:
            low_crit = float(thresholds['low_crit'])
            low_warn = float(thresholds['low_warn'])
            high_warn = float(thresholds['high_warn'])
            high_crit = float(thresholds['high_crit'])
        except (TypeError, ValueError):
            # In case any threshold is None or non-numeric
            return 'Nominal'

        # Normal evaluation logic
        if value < low_crit or value > high_crit:
            return 'Critical'
        if value < low_warn or value > high_warn:
            return 'Warning'
        return 'Nominal'

    def toggle_pause_stream(self):
        if self.simulator:
            is_paused = self.simulator.toggle_pause()
            self.pause_button.setText("Resume Stream" if is_paused else "Pause Stream")
    def check_data_stream(self):
        if not self.parameters:
            self.stream_status_label.setText("Awaiting Parameters")
            self.stream_status_label.setStyleSheet("color: #FFBF00;")
        elif self.simulator and not self.simulator._is_paused:
            self.stream_status_label.setText("STREAMING")
            self.stream_status_label.setStyleSheet("color: #01FF70;")
        else:
            self.stream_status_label.setText("PAUSED")
            self.stream_status_label.setStyleSheet("color: #FF3131;")
        
        # Update connection status every second
        self.update_connection_status()

    def mark_as_unsaved(self):
        """Mark the project as having unsaved changes"""
        self.has_unsaved_changes = True
        self.update_window_title()
    
    def mark_as_saved(self):
        """Mark the project as saved"""
        self.has_unsaved_changes = False
        self.update_window_title()
    
    def update_window_title(self):
        """Update window title to show unsaved changes"""
        base_title = "Glance"
        if self.current_project_path:
            filename = os.path.basename(self.current_project_path)
            title = f"{base_title} - {filename}"
        else:
            title = f"{base_title} - Untitled"
        
        # Only show asterisk if there are actual unsaved changes
        if self.has_unsaved_changes:
            title += " *"
        
        self.setWindowTitle(title)
    
    def _save_tab_layout_explicit(self, tab_index):
        """Save dock layout using grid positions"""
        tab_info = self.tab_data.get(tab_index)
        if not tab_info:
            return {}
        
        layout_info = {
            'positions': {},  # widget_id -> (row, col, width, height)
        }
        
        mainwindow = tab_info['mainwindow']
        
        # Save each dock's state and relative position
        for widget_id, dock in tab_info['docks'].items():
            layout_info['positions'][widget_id] = {
                'floating': dock.isFloating(),
                'visible': dock.isVisible(),
                'geometry': {
                    'x': dock.x(),
                    'y': dock.y(),
                    'width': dock.width(),
                    'height': dock.height()
                }
            }
        
        # Save layout_positions from tab_info if it exists
        if 'layout_positions' in tab_info:
            layout_info['grid_positions'] = tab_info['layout_positions']
        
        return layout_info

    def save_project(self, file_path=None):
        """Save project with improved functionality"""
        if file_path:
            self.current_project_path = file_path
            
        if not self.current_project_path:
            path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "Dashboard Project (*.json)")
            if not path:
                return
            self.current_project_path = path
        
        try:
            # Ensure tab indices are correct before saving
            self._reindex_tabs()
            
            layout_data = {}
            for index, tab_info in self.tab_data.items():
                # Skip if index is not in tab widget (e.g. floating tabs might need special handling)
                if index < self.tab_widget.count():
                    tab_name = self.tab_widget.tabText(index)
                elif tab_info.get('is_floating'):
                    tab_name = tab_info.get('stored_tab_name', f"Floating Tab {index}")
                else:
                    continue
                    
                state = tab_info['mainwindow'].saveState()
                explicit_layout = self._save_tab_layout_explicit(index)
                layout_data[tab_name] = {
                    'state': base64.b64encode(state.data()).decode('utf-8'),
                    'configs': tab_info['configs'],
                    'explicit_layout': explicit_layout
                }
            
            # Include data logging settings and dashboard title customization
            project_data = {
                'parameters': self.parameters,
                'layout': layout_data,
                'connection_settings': self.connection_settings,
                'logging_settings': self.logging_settings,
                'configured_widgets': getattr(self, 'configured_widgets', []),
                'dashboard_title_text': self.dashboard_title_text,
                'dashboard_title_alignment': str(self.dashboard_title_alignment.value),
                'filters': self.filter_manager.to_dict(),  # NEW: Save filters
                'version': '1.0',
                'created': datetime.now().isoformat()
            }
            
            with open(self.current_project_path, 'w') as f:
                json.dump(project_data, f, indent=4)
            
            self.mark_as_saved()
            QMessageBox.information(self, "Success", f"Project saved successfully to:\n{self.current_project_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
    
    def save_project_as(self):
        """Save project with new filename"""
        self.current_project_path = None
        self.save_project()

    def _restore_tab_layout_explicit(self, tab_index, explicit_layout):
        """Restore dock layout from saved positions"""
        if not explicit_layout:
            return
        
        tab_info = self.tab_data.get(tab_index)
        if not tab_info:
            return
        
        # Restore grid positions if available
        if 'grid_positions' in explicit_layout:
            tab_info['layout_positions'] = explicit_layout['grid_positions']
            # Trigger retiling based on saved positions
            self._retile_positions(tab_index)
        
        # Restore individual dock states (floating, geometry)
        if 'positions' in explicit_layout:
            from PySide6.QtCore import QTimer
            
            def restore_dock_states():
                try:
                    for widget_id, pos_info in explicit_layout['positions'].items():
                        if widget_id not in tab_info['docks']:
                            continue
                        
                        dock = tab_info['docks'][widget_id]
                        
                        # Ensure dock is visible first
                        dock.setVisible(True)
                        
                        # Restore floating and geometry
                        if pos_info.get('floating', False):
                            dock.setFloating(True)
                            geom = pos_info.get('geometry', {})
                            if geom:
                                dock.setGeometry(
                                    geom.get('x', 100), 
                                    geom.get('y', 100), 
                                    geom.get('width', 400), 
                                    geom.get('height', 300)
                                )
                        else:
                            dock.setFloating(False)
                        
                        # Ensure dock is raised and visible
                        dock.show()
                        dock.raise_()
                        
                except Exception as e:
                    print(f"Error restoring dock states for tab {tab_index}: {e}")
            
            # Delay to let Qt finish initial layout and state restoration
            QTimer.singleShot(300, restore_dock_states)

    def load_project(self, file_path=None):
        """Load project with improved functionality"""
        if self.has_unsaved_changes and not file_path:
            reply = QMessageBox.question(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them before loading a new project?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        path = file_path
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "Dashboard Project (*.json);;JSON Files (*.json)")
        
        if not path:
            return
        
        try:
            with open(path, 'r') as f:
                project_data = json.load(f)
            
            # Load parameters
            self.parameters = project_data.get('parameters', [])
            
            # Load connection settings
            if 'connection_settings' in project_data:
                self.connection_settings.update(project_data['connection_settings'])
            
            # Load logging settings
            if 'logging_settings' in project_data:
                self.logging_settings = project_data['logging_settings']
                # Reconfigure data logger if settings exist
                if self.logging_settings:
                    selected_params = [p for p in self.parameters if p['id'] in self.logging_settings['selected_params']]
                    self.data_logger.configure(
                        format_type=self.logging_settings['format'],
                        file_path=self.logging_settings['file_path'],
                        parameters=selected_params,
                        buffer_size=self.logging_settings['buffer_size']
                    )
            
            # Load configured widgets
            if 'configured_widgets' in project_data:
                self.configured_widgets = project_data['configured_widgets']
            
            # Load dashboard title customization
            if 'dashboard_title_text' in project_data:
                self.dashboard_title_text = project_data['dashboard_title_text']
            if 'dashboard_title_alignment' in project_data:
                alignment_val = int(project_data['dashboard_title_alignment'])
                self.dashboard_title_alignment = Qt.AlignmentFlag(alignment_val)
            self._update_dashboard_title()
            

            if 'filters' in project_data:
                self.filter_manager.from_dict(project_data['filters'])
            # Clear existing tabs and data
            
            # Clear existing tabs and data
            self.data_history.clear()
            while self.tab_widget.count() > 0:
                self.close_tab(0)
            
            # Load layout data
            layout_data = project_data.get('layout', {})
            for tab_name, tab_layout_data in layout_data.items():
                index = self.add_new_tab(name=tab_name)
                
                # Add all widgets first
                for widget_id, config in tab_layout_data.get('configs', {}).items():
                    self.add_widget_to_dashboard(config, index, widget_id)
                
                # Use QTimer to ensure proper timing for state restoration
                from PySide6.QtCore import QTimer
                
                def restore_tab_state(tab_idx, state_bytes, explicit_layout_data):
                    def delayed_restore():
                        try:
                            restored = False
                            # First restore Qt's built-in state
                            if state_bytes:
                                restored = self.tab_data[tab_idx]['mainwindow'].restoreState(QByteArray(state_bytes))
                            
                            # Only apply explicit layout restoration if restoreState failed or wasn't available
                            # This prevents overwriting the correct layout with a stale grid layout
                            if not restored and explicit_layout_data:
                                self._restore_tab_layout_explicit(tab_idx, explicit_layout_data)
                                
                            # Ensure all docks are visible
                            tab_info = self.tab_data.get(tab_idx)
                            if tab_info:
                                for dock in tab_info['docks'].values():
                                    dock.show()
                                    dock.raise_()
                        except Exception as e:
                            print(f"Error restoring tab {tab_idx}: {e}")
                    
                    # Delay restoration to let Qt finish widget creation
                    QTimer.singleShot(100, delayed_restore)
                
                # Prepare state data
                state_data = base64.b64decode(tab_layout_data['state']) if tab_layout_data.get('state') else None
                explicit_layout = tab_layout_data.get('explicit_layout')
                
                # Schedule restoration
                restore_tab_state(index, state_data, explicit_layout)
            
            self.current_project_path = path
            self.mark_as_saved()
            
            self.restart_simulator()
            self.update_control_states()
            self.update_filter_menus()
            # self.update_status_bar()
            
            QMessageBox.information(self, "Success", f"Project loaded successfully from:\n{path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project: {e}")


    def open_standalone_telemetry_viewer(self):
        """Open standalone telemetry viewer from welcome screen"""
        standalone_viewer = StandaloneTelemetryViewer(self)
        standalone_viewer.exec()
    
    def _build_menu_bar(self):
        menubar = self.menuBar()
        menubar.clear() 

        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")
        filters_menu = menubar.addMenu("Filters")

        # File menu with shortcuts
        new_action = QAction("New Dashboard", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self.show_phase("setup"))
        
        load_action = QAction("Load Project...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_project)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        
        save_as_action = QAction("Save Project As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        
        conn_action = QAction("Connection Settings...", self)
        conn_action.setShortcut("Ctrl+Shift+C")
        conn_action.triggered.connect(self.open_connection_settings)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(conn_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit menu with shortcuts
        manage_params_action = QAction("Manage Parameters...", self)
        manage_params_action.setShortcut("Ctrl+P")
        manage_params_action.triggered.connect(self.manage_parameters)
        
        add_widget_action = QAction("Add Widget...", self)
        add_widget_action.setShortcut("Ctrl+W")
        add_widget_action.triggered.connect(self.open_add_widget_dialog)
        
        remove_widget_action = QAction("Remove Widget...", self)
        remove_widget_action.setShortcut("Ctrl+Shift+W")
        remove_widget_action.triggered.connect(self.remove_selected_display)
        
        edit_menu.addAction(manage_params_action)
        edit_menu.addAction(add_widget_action)
        edit_menu.addAction(remove_widget_action)
        
        # Filters menu with submenus
        add_filter_menu = filters_menu.addMenu("Add Filter to Parameter")
        
        moving_avg_menu = add_filter_menu.addMenu("Moving Average")
        low_pass_menu = add_filter_menu.addMenu("Low Pass")
        kalman_menu = add_filter_menu.addMenu("Kalman")
        median_menu = add_filter_menu.addMenu("Median")
        
        self.filter_submenus = {
            'moving_average': moving_avg_menu,
            'low_pass': low_pass_menu,
            'kalman': kalman_menu,
            'median': median_menu
        }
        
        self.update_filter_menus()
        
        filters_menu.addSeparator()
        manage_filters_action = QAction("Manage Filters...", self)
        manage_filters_action.setShortcut("Ctrl+F")
        manage_filters_action.triggered.connect(self.open_manage_filters_dialog)
        filters_menu.addAction(manage_filters_action)
        
        filters_menu.addSeparator()
        import_filter_action = QAction("Import Custom Filter...", self)
        import_filter_action.triggered.connect(self.import_custom_filter)
        filters_menu.addAction(import_filter_action)
        
        # Data logging menu with shortcuts
        logging_menu = menubar.addMenu("Data Logging")
        
        config_logging_action = QAction("Configure Logging...", self)
        config_logging_action.setShortcut("Ctrl+L")
        config_logging_action.triggered.connect(self.open_logging_config)
        
        start_logging_action = QAction("Start Logging", self)
        start_logging_action.setShortcut("Ctrl+Shift+L")
        start_logging_action.triggered.connect(self.start_logging)
        
        stop_logging_action = QAction("Stop Logging", self)
        stop_logging_action.setShortcut("Ctrl+Alt+L")
        stop_logging_action.triggered.connect(self.stop_logging)

        logging_menu.addSeparator()

        generate_summary_action = QAction("Generate Summary Report...", self)
        generate_summary_action.setShortcut("Ctrl+Shift+R")
        generate_summary_action.triggered.connect(self.generate_summary_report)

        logging_menu.addAction(config_logging_action)
        logging_menu.addAction(start_logging_action)
        logging_menu.addAction(stop_logging_action)
        logging_menu.addAction(generate_summary_action)

        # View menu with shortcuts
        add_tab_action = QAction("Add Tab", self)
        add_tab_action.setShortcut("Ctrl+T")
        add_tab_action.triggered.connect(lambda: self.add_new_tab())
        
        rename_tab_action = QAction("Rename Current Tab", self)
        rename_tab_action.setShortcut("Ctrl+R")
        rename_tab_action.triggered.connect(self.rename_current_tab)

        # Add this:
        float_tab_action = QAction("Float/Dock Current Tab", self)
        float_tab_action.setShortcut("Ctrl+Shift+F")
        float_tab_action.triggered.connect(lambda: self.toggle_float_tab(self.tab_widget.currentIndex()))

        
        raw_tlm_action = QAction("Raw Telemetry Monitor...", self)
        raw_tlm_action.setShortcut("Ctrl+M")
        raw_tlm_action.triggered.connect(self.open_raw_telemetry_monitor)

        # Add fullscreen action
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)

        
        # NEW: Pause/Resume shortcut
        pause_action = QAction("Pause/Resume Stream", self)
        pause_action.setShortcut("Space")
        pause_action.triggered.connect(self.toggle_pause_stream)
        
        view_menu.addAction(add_tab_action)
        view_menu.addAction(rename_tab_action)
        view_menu.addAction(float_tab_action)
        view_menu.addSeparator()
        view_menu.addAction(fullscreen_action)
        view_menu.addAction(raw_tlm_action)
        view_menu.addSeparator()
        view_menu.addAction(pause_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        
        documentation_action = QAction("Documentation", self)
        documentation_action.setShortcut("F1")
        documentation_action.triggered.connect(self.show_documentation)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        
        help_menu.addAction(documentation_action)
        help_menu.addAction(about_action)

    def _build_splash_screen(self):
        """Splash screen with animated logo that transitions to welcome screen"""
        self.splash_page = QWidget()
        self.splash_page.setStyleSheet("""
            QWidget#splashPage {
                background: qradialgradient(
                    cx: 0.5, cy: 0.5,
                    fx: 0.5, fy: 0.5,
                    radius: 1.2,
                    stop: 0 #212124,
                    stop: 0.6 #111111,
                    stop: 1 #0a0a0a
                );
            }
        """)
        self.splash_page.setObjectName("splashPage")
        
        layout = QVBoxLayout(self.splash_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo container
        self.splash_logo = QLabel()
        self.splash_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.splash_logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        

        self.splash_logo.setText("Glance")
        self.splash_logo.setStyleSheet("color: #ffffff; font-size: 72px; font-weight: bold;")
        
        layout.addWidget(self.splash_logo)
        self.stack.addWidget(self.splash_page)
        
        # Timer to transition after 2 seconds
        self.splash_timer = QTimer(self)
        self.splash_timer.setSingleShot(True)
        self.splash_timer.timeout.connect(self._animate_splash_to_welcome)

    def _animate_splash_to_welcome(self):
        """Transition from splash to welcome screen"""
        self.show_phase("welcome")

    def _animate_splash_to_welcome(self):
        """Animate logo from splash screen to welcome screen position"""
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QRect
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        
        # First, switch to welcome page
        self.show_phase("welcome")
        
        # Create a temporary overlay widget for animation
        overlay = QWidget(self)
        overlay.setGeometry(self.rect())
        overlay.setStyleSheet("background: transparent;")
        overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        overlay.raise_()
        
        # Create animated logo on overlay
        anim_logo = QLabel(overlay)
        anim_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Position at center
        start_x = (self.width() - 500) // 2
        start_y = (self.height() - 500) // 2
        anim_logo.setGeometry(start_x, start_y, 500, 500)
        
        # Show overlay
        overlay.show()
        anim_logo.show()
        
        # Create fade out animation for overlay after movement
        def cleanup_overlay():
            overlay.deleteLater()
        
        QTimer.singleShot(800, cleanup_overlay)

    def _build_welcome_menu_bar(self):
        """Build minimal menu bar for welcome screen"""
        menubar = self.menuBar()
        menubar.clear()  # Clear existing menus
        
        # File menu - minimal options
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Dashboard", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self.show_phase("setup"))
        
        load_action = QAction("Load Project...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._load_project_from_welcome)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        documentation_action = QAction("Documentation", self)
        documentation_action.setShortcut("F1")
        documentation_action.triggered.connect(self.show_documentation)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        
        help_menu.addAction(documentation_action)
        help_menu.addAction(about_action)

    def _load_project_from_welcome(self):
        """Load project from welcome screen and navigate to dashboard"""
        self.load_project()
        # Only switch to dashboard if a project was actually loaded
        if self.parameters or self.tab_widget.count() > 0:
            self.show_phase("dashboard")

    def show_documentation(self):
        """Show the documentation from web with loading animation"""
        doc_url = "https://glance.teamignition.space/"
        
        # Try to use QWebEngineView if available
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtCore import QUrl, QTimer
            from PySide6.QtWidgets import QStackedWidget
            
            # Create documentation viewer dialog
            doc_dialog = QDialog(self)
            doc_dialog.setWindowTitle("Glance Documentation")
            doc_dialog.setMinimumSize(1000, 700)
            
            layout = QVBoxLayout(doc_dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Create a stacked widget to switch between loading and content
            stack = QStackedWidget()
            
            # Loading screen
            loading_widget = QWidget()
            loading_widget.setStyleSheet("background-color: #1a1a1a;")
            loading_layout = QVBoxLayout(loading_widget)
            loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Loading animation container
            loading_container = QWidget()
            loading_container.setFixedSize(200, 250)
            loading_inner_layout = QVBoxLayout(loading_container)
            loading_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            loading_inner_layout.setSpacing(20)
            
            # Animated spinner
            spinner_label = QLabel("⬢")
            spinner_label.setStyleSheet("color: #4a9eff; font-size: 64px; font-weight: bold;")
            spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Loading text
            loading_text = QLabel("Loading Documentation...")
            loading_text.setStyleSheet("color: #e8e8e8; font-size: 16px; font-weight: 500;")
            loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Progress dots
            progress_dots = QLabel("●")
            progress_dots.setStyleSheet("color: #4a9eff; font-size: 14px;")
            progress_dots.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            loading_inner_layout.addWidget(spinner_label)
            loading_inner_layout.addWidget(loading_text)
            loading_inner_layout.addWidget(progress_dots)
            
            loading_layout.addWidget(loading_container)
            
            # Web view
            web_view = QWebEngineView()
            web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # Add both to stack
            stack.addWidget(loading_widget)
            stack.addWidget(web_view)
            stack.setCurrentIndex(0)
            
            layout.addWidget(stack, 1)
            
            # Store timers
            spinner_timer = QTimer(doc_dialog)
            timeout_timer = QTimer(doc_dialog)
            timeout_timer.setSingleShot(True)
            
            # Track if loaded
            is_loaded = [False]
            
            # Animate loading spinner
            rotation_angle = [0]
            dot_state = [0]
            
            def animate_spinner():
                rotation_angle[0] = (rotation_angle[0] + 30) % 360
                spinners = ["⬡", "⬢", "⬣", "⬢"]
                spinner_label.setText(spinners[(rotation_angle[0] // 30) % len(spinners)])
                dot_state[0] = (dot_state[0] + 1) % 4
                dots = "●" * (dot_state[0] + 1) + "○" * (3 - dot_state[0])
                progress_dots.setText(dots)
            
            spinner_timer.timeout.connect(animate_spinner)
            spinner_timer.start(100)
            
            def switch_to_content():
                if not is_loaded[0]:
                    is_loaded[0] = True
                    spinner_timer.stop()
                    timeout_timer.stop()
                    stack.setCurrentIndex(1)
            
            def on_load_finished(success):
                print(f"Load finished: {success}")  # Debug
                switch_to_content()
            
            def on_load_progress(progress):
                print(f"Load progress: {progress}%")  # Debug
                if progress == 100:
                    switch_to_content()
            
            def on_timeout():
                print("Timeout - forcing switch")  # Debug
                if not is_loaded[0]:
                    # Try to switch anyway after timeout
                    switch_to_content()
            
            # Connect signals
            web_view.loadFinished.connect(on_load_finished)
            web_view.loadProgress.connect(on_load_progress)
            timeout_timer.timeout.connect(on_timeout)
            
            # Start timeout (10 seconds)
            timeout_timer.start(10000)
            
            # Load URL
            print(f"Loading: {doc_url}")  # Debug
            web_view.load(QUrl(doc_url))
            
            # Add close button at bottom
            button_container = QWidget()
            button_container.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #2a2a2a;")
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(12, 8, 12, 8)
            
            # Add "Open in Browser" button
            browser_btn = QPushButton("Open in Browser")
            browser_btn.clicked.connect(lambda: webbrowser.open(doc_url))
            
            close_btn = QPushButton("Close")
            close_btn.setMinimumWidth(100)
            close_btn.clicked.connect(doc_dialog.accept)
            
            button_layout.addWidget(browser_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            layout.addWidget(button_container, 0)
            
            doc_dialog.setStyleSheet("""
                QDialog { background-color: #1e1e1e; }
                QPushButton {
                    background-color: #2a2a2a;
                    border: 1px solid #404040;
                    border-radius: 5px;
                    padding: 8px 16px;
                    color: #e8e8e8;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #383838;
                    border-color: #4a9eff;
                }
            """)
            
            doc_dialog.exec()
            
        except ImportError:
            reply = QMessageBox.question(
                self, 
                "Open Documentation", 
                f"The built-in documentation viewer requires PySide6-WebEngine.\n\n"
                f"Would you like to open the documentation in your web browser instead?\n\n"
                f"URL: {doc_url}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                webbrowser.open(doc_url)

    def open_documentation_in_browser(self, doc_path):
        """Open documentation in default web browser"""
        import webbrowser
        abs_path = os.path.abspath(doc_path)
        webbrowser.open(f'file://{abs_path}')
        QMessageBox.information(self, "Documentation Opened", "Documentation opened in your default web browser.")

    def open_raw_telemetry_monitor(self):
        """Open the advanced telemetry viewer window"""
        if self.raw_tlm_monitor is None or not self.raw_tlm_monitor.isVisible():
            # Use StandaloneTelemetryViewer as the main viewer
            self.raw_tlm_monitor = StandaloneTelemetryViewer(self)
            self.raw_tlm_monitor.show()
        else:
            self.raw_tlm_monitor.raise_()
            self.raw_tlm_monitor.activateWindow()

    def open_standalone_telemetry_viewer(self):
        """Open standalone telemetry viewer from welcome screen"""
        # Redirect to the main method to ensure single instance
        self.open_raw_telemetry_monitor()

    def show_about_dialog(self):
        """Display the About dialog with modern professional layout (Final Version)"""
        import webbrowser

        dialog = QDialog(self)
        dialog.setWindowTitle("About Glance")
        dialog.setFixedSize(900, 720) # Adjusted size for compact layout
        
        # Finalized stylesheet with polished gradients, borders, and typography
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #0d0d0d);
            }
            QLabel {
                color: #e8e8e8;
            }
            QFrame#heroCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0d47a1, stop:1 #1a237e); /* Dark blue to indigo gradient */
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 28px;
            }
            QFrame#bentoCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #212121);
                border: 1px solid #383838;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame#accentCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(76, 175, 80, 0.15), stop:1 rgba(33, 150, 243, 0.15));
                border: 1px solid rgba(76, 175, 80, 0.3);
                border-radius: 12px;
                padding: 20px;
            }
            QLabel#heroTitle {
                color: #ffffff;
                font-weight: 700;
                font-size: 32px;
                letter-spacing: -0.5px;
            }
            QLabel#heroSubtitle {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
            }
            QLabel#heroVersion {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                background: rgba(0, 0, 0, 0.2);
                padding: 4px 12px;
                border-radius: 12px;
            }
            QLabel#cardTitle {
                color: #ffffff;
                font-weight: 600;
                font-size: 15px;
                margin-bottom: 12px;
            }
            QLabel#cardContent {
                color: #e0e0e0;
                font-size: 13px;
                line-height: 1.5;
            }
            QPushButton#linkButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid #444;
                color: #e0e0e0;
                padding: 10px;
                border-radius: 6px;
                text-align: left;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton#linkButton:hover {
                background: rgba(94, 179, 255, 0.1);
                border-color: #5eb3ff;
            }
            QLabel#sectionTitle {
                color: #9cdcfe;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin: 12px 0 6px 0;
            }
            QLabel#statValue {
                color: #4fc3f7;
                font-size: 24px;
                font-weight: 700;
                font-family: 'Consolas', monospace;
            }
            QLabel#statLabel {
                color: #aaaaaa;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton#closeButton {
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 10px 24px;
                color: #e8e8e8;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#closeButton:hover {
                background: #333333;
                border-color: #5eb3ff;
            }
            QPushButton#closeButton:pressed {
                background: #1a1a1a;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #1e1e1e; width: 10px; border-radius: 5px; margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a; border-radius: 5px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #5a5a5a; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 28, 28, 28)
        content_layout.setSpacing(18) # Reduced spacing between rows
        
        # === HERO SECTION ===
        hero_card = QFrame(); hero_card.setObjectName("heroCard")
        hero_layout = QHBoxLayout(hero_card); hero_layout.setSpacing(24)
        glance_logo = QLabel()
        glance_logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Calculate project root from this file location: app/ui/main_window.py -> ... -> ... -> root
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        Glogo_path = os.path.join(base_path, "docs/public", "Glance_nobg _jl.png")
        if os.path.exists(Glogo_path):
            pixmap = QPixmap(Glogo_path)
            scaled_pixmap = pixmap.scaled(75, 75, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            glance_logo.setPixmap(scaled_pixmap)
        glance_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_container = QWidget(); text_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        text_layout = QVBoxLayout(text_container); text_layout.setSpacing(6)
        title_label = QLabel("Glance"); title_label.setObjectName("heroTitle")
        subtitle_label = QLabel("Professional Telemetry Dashboard"); subtitle_label.setObjectName("heroSubtitle")
        version_badge = QLabel("Version 2.0.0"); version_badge.setObjectName("heroVersion")
        desc_label = QLabel("Real-time data visualization platform for aerospace applications,\nembedded systems, and industrial monitoring.")
        desc_label.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 12px; line-height: 1.5;"); desc_label.setWordWrap(True)
        text_layout.addWidget(title_label); text_layout.addWidget(subtitle_label); text_layout.addWidget(version_badge)
        text_layout.addSpacing(10); text_layout.addWidget(desc_label); text_layout.addStretch()
        hero_layout.addWidget(glance_logo); hero_layout.addWidget(text_container, 1)
        content_layout.addWidget(hero_card)
        
        # === STATISTICS ROW ===
        stats_row = QHBoxLayout(); stats_row.setSpacing(18)
        def create_stat_card(value, label):
            card = QFrame(); card.setObjectName("bentoCard"); card.setMinimumHeight(80)
            layout = QVBoxLayout(card); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_label = QLabel(value); val_label.setObjectName("statValue"); val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label = QLabel(label); text_label.setObjectName("statLabel"); text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(val_label); layout.addWidget(text_label)
            return card
        stats_row.addWidget(create_stat_card("8+", "Widget Types")); stats_row.addWidget(create_stat_card("4", "Protocols"))
        stats_row.addWidget(create_stat_card("∞", "Parameters")); stats_row.addWidget(create_stat_card("GPL", "Open Source"))
        content_layout.addLayout(stats_row)
        
        # === FEATURES SECTION ===
        features_section = QLabel("Core Features"); features_section.setObjectName("sectionTitle"); content_layout.addWidget(features_section)
        features_row = QHBoxLayout(); features_row.setSpacing(18)
        def create_feature_card(icon, title, features_list):
            card = QFrame(); card.setObjectName("bentoCard")
            layout = QVBoxLayout(card); layout.setSpacing(8)
            header = QHBoxLayout(); icon_label = QLabel(icon); icon_label.setStyleSheet("color: #5eb3ff; font-size: 22px;")
            title_label = QLabel(title); title_label.setObjectName("cardTitle")
            header.addWidget(icon_label); header.addWidget(title_label); header.addStretch(); layout.addLayout(header)
            for feature in features_list:
                item_layout = QHBoxLayout(); bullet = QLabel("▹"); bullet.setStyleSheet("color: #4fc3f7; font-size: 16px; font-weight: bold;")
                item_label = QLabel(feature); item_label.setObjectName("cardContent"); item_label.setWordWrap(True)
                item_layout.addWidget(bullet); item_layout.addWidget(item_label, 1); layout.addLayout(item_layout)
            layout.addStretch()
            return card
        features_row.addWidget(create_feature_card("📈", "Visualization", ["Real-time graphs & gauges", "GPS mapping support", "Configurable data tables"]))
        features_row.addWidget(create_feature_card("⚙️", "Processing", ["Advanced signal filtering", "Kalman, Low-pass & more", "Flexible data logging"]))
        features_row.addWidget(create_feature_card("🔗", "Connectivity", ["Serial, TCP, and UDP", "JSON, CSV, and raw bytes", "Dummy data for testing"]))
        content_layout.addLayout(features_row)
        
        # === LINKS SECTION ===
        links_section = QLabel("Resources & Community"); links_section.setObjectName("sectionTitle"); content_layout.addWidget(links_section)
        links_row = QHBoxLayout(); links_row.setSpacing(18)
        def create_link_button(icon, text, url):
            button = QPushButton(f" {icon}  {text}"); button.setObjectName("linkButton"); button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda: webbrowser.open(url))
            return button
        links_card = QFrame(); links_card.setObjectName("bentoCard")
        links_layout = QVBoxLayout(links_card); links_layout.setSpacing(8)
        links_title = QLabel("Documentation & Code"); links_title.setObjectName("cardTitle"); links_layout.addWidget(links_title)
        links_layout.addWidget(create_link_button("📖", "Read the Docs", "https://glance.teamignition.space/"))
        links_layout.addWidget(create_link_button("💻", "GitHub Repository", "https://github.com/teamignitionvitc/Glance"))
        links_layout.addWidget(create_link_button("🌐", "Team Website", "https://teamignition.space"))
        links_layout.addWidget(create_link_button("🐛", "Report an Issue", "https://github.com/teamignitionvitc/Glance/issues"))
        links_layout.addStretch()
        social_card = QFrame(); social_card.setObjectName("bentoCard")
        social_layout = QVBoxLayout(social_card); social_layout.setSpacing(8)
        social_title = QLabel("Connect With Us"); social_title.setObjectName("cardTitle"); social_layout.addWidget(social_title)
        social_layout.addWidget(create_link_button("🐦", "Twitter / X", "https://x.com/ignitiontech23"))
        social_layout.addWidget(create_link_button("💼", "LinkedIn", "https://www.linkedin.com/in/teamignition/"))
        social_layout.addWidget(create_link_button("📸", "Instagram", "https://www.instagram.com/ignition_vitc"))
        social_layout.addStretch()
        links_row.addWidget(links_card); links_row.addWidget(social_card); content_layout.addLayout(links_row)
        
        # === LICENSE & TEAM INFO ===
        info_row = QHBoxLayout(); info_row.setSpacing(18)
        license_card = QFrame(); license_card.setObjectName("accentCard"); license_card.setMinimumHeight(130)
        license_layout = QVBoxLayout(license_card); license_layout.setSpacing(8)
        license_title = QLabel("📜 License"); license_title.setObjectName("cardTitle"); license_layout.addWidget(license_title)
        license_content = QLabel("GNU GPL v3.0 with additional restrictions\n\n© 2025 Team Ignition · Software Department\nFree and open source software")
        license_content.setObjectName("cardContent"); license_layout.addWidget(license_content); license_layout.addStretch()
        team_card = QFrame(); team_card.setObjectName("accentCard"); team_card.setMinimumHeight(130)
        team_layout = QVBoxLayout(team_card); team_layout.setSpacing(8)
        team_header_layout = QHBoxLayout(); team_title = QLabel("About Team Ignition"); team_title.setObjectName("cardTitle")
        team_logo = QLabel()
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        logo_path = os.path.join(base_path, "docs", "public", "ign_logo_wht.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            team_logo.setPixmap(scaled_pixmap)
        team_header_layout.addWidget(team_title); team_header_layout.addStretch(); team_header_layout.addWidget(team_logo); team_layout.addLayout(team_header_layout)
        team_content = QLabel("Designing, building, and launching experimental rockets with in-house developed avionics and ground control systems.")
        team_content.setObjectName("cardContent"); team_content.setWordWrap(True); team_layout.addWidget(team_content); team_layout.addStretch()
        info_row.addWidget(license_card); info_row.addWidget(team_card); content_layout.addLayout(info_row)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        # === BOTTOM BAR ===
        button_container = QWidget()
        button_container.setStyleSheet("background: #141414; border-top: 1px solid #2a2a2a;")
        button_layout = QHBoxLayout(button_container); button_layout.setContentsMargins(28, 14, 28, 14)
        credits = QLabel("Developed by the Team Ignition Software Department"); credits.setStyleSheet("color: #888888; font-size: 11px;")
        close_btn = QPushButton("Close"); close_btn.setObjectName("closeButton"); close_btn.setMinimumWidth(120); close_btn.setCursor(Qt.CursorShape.PointingHandCursor); close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(credits); button_layout.addStretch(); button_layout.addWidget(close_btn)
        main_layout.addWidget(button_container)
        
        dialog.exec()

        
    # Convenience wrappers for Source menu
    def set_source_backend(self):
        # Open connection settings dialog to let user choose backend type
        self.open_connection_settings()

    def set_source_dummy(self):
        self.connection_settings['mode'] = 'dummy'
        self.restart_simulator()
        # self.update_status_bar()

    def _build_status_bar(self):
        sb = self.statusBar()
        sb.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #252525, stop:1 #1e1e1e);
                border-top: 2px solid #333;
                color: #e0e0e0;
                padding: 6px 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            QStatusBar QLabel {
                color: #e0e0e0;
                padding: 0 6px;
                font-size: 11px;
            }
            QStatusBar QLabel#SBClock {
                font-family: 'Consolas', monospace;
                font-weight: bold;
                color: #64b5f6;
                background: rgba(100, 181, 246, 0.1);
                border-radius: 4px;
                padding: 4px 10px;
            }
            QStatusBar QLabel#SBConnected {
                color: #81c784;
                font-weight: bold;
                background: rgba(129, 199, 132, 0.15);
                border-radius: 4px;
                padding: 4px 8px;
            }
            QStatusBar QLabel#SBDisconnected {
                color: #e57373;
                font-weight: bold;
                background: rgba(229, 115, 115, 0.15);
                border-radius: 4px;
                padding: 4px 8px;
            }
            QStatusBar QLabel#SBValue {
                font-family: 'Consolas', monospace;
                color: #ffb74d;
                background: rgba(255, 183, 77, 0.1);
                border-radius: 3px;
                padding: 3px 8px;
            }
            QStatusBar QLabel#SBMetric {
                font-family: 'Consolas', monospace;
                color: #90caf9;
                font-size: 10px;
            }
            QStatusBar QLabel#Separator {
                color: #555;
                padding: 0 4px;
            }
            QStatusBar QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2e2e2e);
                border: 1px solid #555;
                border-radius: 4px;
                color: #fff;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 500;
                margin: 0 4px;
            }
            QStatusBar QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3e3e3e);
                border-color: #666;
            }
            QStatusBar QPushButton:pressed {
                background: #2a2a2a;
            }
            QStatusBar QPushButton#LoggingActive {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #388e3c, stop:1 #2e7d32);
                border-color: #4caf50;
            }
            QStatusBar QPushButton#LoggingActive:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
            }
            QStatusBar QPushButton#TelemetryBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976d2, stop:1 #1565c0);
                border-color: #2196f3;
                font-weight: 600;
            }
            QStatusBar QPushButton#TelemetryBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196f3, stop:1 #1976d2);
            }
        """)
        
        # Clock
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setObjectName("SBClock")
        self.clock_label.setToolTip("Current Time")
        
        # Connection Status (Clickable)
        self.conn_label = QLabel("Disconnected")
        self.conn_label.setObjectName("SBDisconnected")
        self.conn_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.conn_label.mousePressEvent = lambda e: self.open_connection_settings()
        self.conn_label.setToolTip("Click to configure connection")
        
        # Alias for update_connection_status compatibility
        self.status_conn_label = self.conn_label
        
        # Session Time
        self.session_time_label = QLabel("")
        self.session_time_label.setObjectName("SBValue")
        self.session_time_label.setToolTip("Session Duration")
        self.session_time_label.setVisible(False)
        
        # Stream status - hidden initially
        self.status_label = QLabel("")
        self.status_label.setToolTip("Stream Status")
        self.status_label.setVisible(False)
        
        # Logging Button & Size
        self.logging_btn = QPushButton("Start Logging")
        self.logging_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logging_btn.clicked.connect(self.toggle_logging_from_statusbar)
        self.logging_btn.setToolTip("Start/Stop data logging")
        
        self.log_size_label = QLabel("")
        self.log_size_label.setObjectName("SBValue")
        self.log_size_label.setVisible(False)
        
        # Packet Counter
        self.packet_count_label = QLabel("Packets: 0")
        self.packet_count_label.setObjectName("SBMetric")
        self.packet_count_label.setToolTip("Total Packets Received")
        
        # RX Bytes
        self.rx_bytes_label = QLabel("RX: 0 B")
        self.rx_bytes_label.setObjectName("SBMetric")
        self.rx_bytes_label.setToolTip("Total Data Received")
        
        # Active Parameters
        self.active_params_label = QLabel("Parameters: 0")
        self.active_params_label.setObjectName("SBMetric")
        self.active_params_label.setToolTip("Active Parameters")
        
        # Widget Count
        self.widget_count_label = QLabel("Widgets: 0")
        self.widget_count_label.setObjectName("SBMetric")
        self.widget_count_label.setToolTip("Widgets in Current Tab")
        
        # FPS Counter
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setObjectName("SBMetric")
        self.fps_label.setToolTip("UI Update Rate")
        self.fps_counter = 0
        self.fps_last_time = time.time()
        
        # Metrics
        self.rate_label = QLabel("")
        self.rate_label.setObjectName("SBValue")
        self.rate_label.setToolTip("Data Rate")
        
        # Raw Telemetry Viewer button
        self.telemetry_viewer_btn = QPushButton("Raw Telemetry")
        self.telemetry_viewer_btn.setObjectName("TelemetryBtn")
        self.telemetry_viewer_btn.setToolTip("Open standalone telemetry monitor")
        self.telemetry_viewer_btn.clicked.connect(self.open_standalone_telemetry_viewer)
        self.telemetry_viewer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Separators
        self.sep1 = QLabel("|")
        self.sep1.setObjectName("Separator")
        self.sep2 = QLabel("|")
        self.sep2.setObjectName("Separator")
        self.sep3 = QLabel("|")
        self.sep3.setObjectName("Separator")
        self.sep4 = QLabel("|")
        self.sep4.setObjectName("Separator")
        self.sep5 = QLabel("|")
        self.sep5.setObjectName("Separator")
        self.sep6 = QLabel("|")
        self.sep6.setObjectName("Separator")
        
        # Layout - Left side (only clock on welcome screen)
        sb.addWidget(self.clock_label)
        sb.addWidget(self.sep1)
        sb.addWidget(self.conn_label)
        sb.addWidget(self.sep2)
        sb.addWidget(self.status_label)
        sb.addWidget(self.logging_btn)
        sb.addWidget(self.log_size_label)
        
        # Middle - Metrics (hidden on welcome screen)
        sb.addWidget(self.sep3)
        sb.addWidget(self.packet_count_label)
        sb.addWidget(self.rx_bytes_label)
        sb.addWidget(self.sep4)
        sb.addWidget(self.active_params_label)
        sb.addWidget(self.widget_count_label)
        
        # Right side
        sb.addPermanentWidget(self.fps_label)
        sb.addPermanentWidget(self.sep5)
        sb.addPermanentWidget(self.telemetry_viewer_btn)
        sb.addPermanentWidget(self.sep6)
        sb.addPermanentWidget(self.rate_label)
        
        # Timer for clock and session updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status_bar_periodic)
        self.status_timer.start(1000)
        
        self.session_start_time = None
        self.total_packets = 0
        self.total_rx_bytes = 0


    def _update_status_bar_periodic(self):
        # Update Clock
        self.clock_label.setText(datetime.now().strftime('%H:%M:%S'))
        
        # Update Session Time
        if self.session_start_time:
            duration = datetime.now() - self.session_start_time
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.session_time_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
            self.session_time_label.setVisible(True)
        else:
            self.session_time_label.setVisible(False)
            
        # Update Log Size
        if self.data_logger.is_logging and self.data_logger.current_file:
            try:
                size_bytes = os.path.getsize(self.data_logger.current_file)
                # Convert to readable format
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size_bytes < 1024:
                        break
                    size_bytes /= 1024
                self.log_size_label.setText(f"{size_bytes:.1f} {unit}")
                self.log_size_label.setVisible(True)
            except:
                self.log_size_label.setText("Error")
        else:
            self.log_size_label.setVisible(False)
        
        # Update Packet Counter
        self.packet_count_label.setText(f"Packets: {self.total_packets}")
        
        # Update RX Bytes
        rx_bytes = self.total_rx_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if rx_bytes < 1024:
                break
            rx_bytes /= 1024
        self.rx_bytes_label.setText(f"RX: {rx_bytes:.1f} {unit}")
        
        # Update Active Parameters
        active_count = len(self.parameters)
        self.active_params_label.setText(f"Parameters: {active_count}")
        
        # Update Widget Count for current tab
        current_idx = self.tab_widget.currentIndex()
        widget_count = 0
        if current_idx in self.tab_data:
            widget_count = len(self.tab_data[current_idx].get('docks', {}))
        self.widget_count_label.setText(f"Widgets: {widget_count}")
        
        # Update FPS
        self.fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self.fps_last_time
        if elapsed >= 1.0:
            fps = self.fps_counter / elapsed
            self.fps_label.setText(f"FPS: {int(fps)}")
            self.fps_counter = 0
            self.fps_last_time = current_time

    def toggle_logging_from_statusbar(self):
        """Toggle data logging from status bar button"""
        if self.data_logger.is_logging:
            # Stop logging
            self.stop_logging()
        else:
            # Start logging - check if configured first
            if not self.logging_settings:
                # Open configuration dialog
                reply = QMessageBox.question(
                    self, 
                    "Configure Logging", 
                    "Data logging is not configured. Would you like to configure it now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.open_logging_config()
                    # After configuration, ask if they want to start
                    if self.logging_settings:
                        start_reply = QMessageBox.question(
                            self, 
                            "Start Logging", 
                            "Configuration saved. Start logging now?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if start_reply == QMessageBox.StandardButton.Yes:
                            self.start_logging()
            else:
                # Configuration exists, start logging
                self.start_logging()
        
        # Update button appearance
        self.update_logging_button()

    def update_logging_button(self):
        """Update logging button text and style based on state"""
        if self.data_logger.is_logging:
            self.logging_btn.setText("Stop Logging")
            self.logging_btn.setObjectName("LoggingActive")
            self.logging_btn.setStyleSheet("")  # Reset to apply new object name
            
            # Update header status
            filename = os.path.basename(self.data_logger.log_file_path) if self.data_logger.log_file_path else "unknown"
            self.logging_status_label.setText(f"Logging: ON ({filename})")
            self.logging_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
        else:
            self.logging_btn.setText("Start Logging")
            self.logging_btn.setObjectName("")  # Remove object name
            self.logging_btn.setStyleSheet("")  # Reset styling
            
            # Update header status
            self.logging_status_label.setText("Logging: OFF")
            self.logging_status_label.setStyleSheet("color: #888888; font-weight: bold;")

    def update_status_bar_visibility(self, phase):
        """Show/hide status bar elements based on current phase"""
        is_dashboard = (phase == "dashboard")
        is_splash = (phase == "splash")
        
        # Always show status bar
        self.statusBar().setVisible(True)
        
        # On welcome screen, show only clock and telemetry button
        if not is_dashboard:
            # Hide all dashboard-specific elements
            self.conn_label.setVisible(False)
            self.status_label.setVisible(False)
            self.logging_btn.setVisible(False)
            self.log_size_label.setVisible(False)
            self.session_time_label.setVisible(False)
            self.rate_label.setVisible(False)
            
            # Hide metrics
            self.packet_count_label.setVisible(False)
            self.rx_bytes_label.setVisible(False)
            self.active_params_label.setVisible(False)
            self.widget_count_label.setVisible(False)
            self.fps_label.setVisible(False)
            
            # Hide separators
            self.sep1.setVisible(False)
            self.sep2.setVisible(False)
            self.sep3.setVisible(False)
            self.sep4.setVisible(False)
            self.sep5.setVisible(False)
            self.sep6.setVisible(False)
            
            # Show only clock and telemetry button
            self.clock_label.setVisible(True)
            self.telemetry_viewer_btn.setVisible(True)
        else:
            # Dashboard - show all elements
            self.clock_label.setVisible(True)
            self.conn_label.setVisible(True)
            self.status_label.setVisible(True)
            self.logging_btn.setVisible(True)
            self.telemetry_viewer_btn.setVisible(True)
            self.rate_label.setVisible(True)
            
            # Show metrics
            self.packet_count_label.setVisible(True)
            self.rx_bytes_label.setVisible(True)
            self.active_params_label.setVisible(True)
            self.widget_count_label.setVisible(True)
            self.fps_label.setVisible(True)
            
            # Show separators
            self.sep1.setVisible(True)
            self.sep2.setVisible(True)
            self.sep3.setVisible(True)
            self.sep4.setVisible(True)
            self.sep5.setVisible(True)
            self.sep6.setVisible(True)



    def _build_welcome_page(self):
        self.welcome_page = QWidget()
        
        # Apply gradient background from bottom
        self.welcome_page.setStyleSheet("""
            QWidget#welcomePage {
                background: qradialgradient(
                    cx: 0.5, cy: 1.0,
                    fx: 0.5, fy: 1.0,
                    radius: 1.2,
                    stop: 0 #212124,
                    stop: 0.6 #111111,
                    stop: 1 #111111
                );
            }
        """)
        self.welcome_page.setObjectName("welcomePage")
        
        v = QVBoxLayout(self.welcome_page)
        v.setContentsMargins(60, 40, 60, 40)
        v.setSpacing(24)
        
        # Logo section
        logo_container = QWidget()
        logo_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        try:
            from PySide6.QtGui import QPixmap
            logo = QLabel("")
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            image_path = os.path.join(base_path, "docs", "public", "Glance_nobg.png")
            pix = QPixmap(image_path)

            if not pix.isNull():
                logo.setPixmap(pix.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation))
                logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                logo_layout.addWidget(logo)
        except Exception:
            pass
        
        # Title and subtitle
        subtitle = QLabel("<p style='color: #cccccc; font-size: 14px; margin: 8px 0;'>Professional industrial data visualization and monitoring</p>")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Feature highlights
        features = QWidget()
        features.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        features_layout = QHBoxLayout(features)
        features_layout.setSpacing(30)
        
        feature1 = QLabel("<div style='text-align: center;'><b>Real-time Data</b><br><small>Live streaming from serial, TCP, UDP</small></div>")
        feature2 = QLabel("<div style='text-align: center;'><b>Multiple Widgets</b><br><small>Graphs, gauges, tables, maps</small></div>")
        feature3 = QLabel("<div style='text-align: center;'><b>Professional UI</b><br><small>Industry-ready interface</small></div>")
        
        for f in [feature1, feature2, feature3]:
            f.setStyleSheet("color: #aaaaaa; padding: 8px;")
            f.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            features_layout.addWidget(f)
        
        # Action buttons
        btn_container = QWidget()
        btn_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(16)
        
        create_btn = QPushButton("Create New Dashboard")
        load_btn = QPushButton("Load Project...")
        
        create_btn.setObjectName("PrimaryCTA")
        load_btn.setObjectName("SecondaryCTA")
        create_btn.setMinimumSize(200, 45)
        load_btn.setMinimumSize(180, 45)
        
        btn_layout.addStretch()
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addStretch()
        
        # Assemble layout
        v.addStretch()
        v.addWidget(logo_container)
        v.addSpacing(16)
        v.addWidget(subtitle)
        v.addSpacing(24)
        v.addWidget(features)
        v.addSpacing(32)
        v.addWidget(btn_container)
        v.addStretch()
        
        self.stack.addWidget(self.welcome_page)
        create_btn.clicked.connect(lambda: self.show_phase("setup"))
        def _load_and_go():
            self.load_project(); self.show_phase("dashboard")
        load_btn.clicked.connect(_load_and_go)

    def _build_setup_page(self):
        self.setup_page = QWidget()
        self.setup_page.setObjectName("setupPage")

        # Import necessary classes for standard icons
        from PySide6.QtWidgets import QStyle
        from PySide6.QtGui import QIcon

        # Main layout
        main_layout = QVBoxLayout(self.setup_page)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # --- Title and Subtitle ---
        title_layout = QVBoxLayout()
        title = QLabel("Dashboard Configuration")
        title.setObjectName("setupTitle")
        subtitle = QLabel("Set up your data source and format to begin streaming.")
        subtitle.setObjectName("setupSubtitle")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        main_layout.addLayout(title_layout)

        # --- Two-Column Layout for Cards ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        main_layout.addLayout(content_layout, 1)

        # === LEFT COLUMN: CONNECTION SETTINGS ===
        connection_card = QFrame()
        connection_card.setObjectName("setupCard")
        content_layout.addWidget(connection_card, 1)
        
        # Main layout for the card (no margins)
        card_main_layout_left = QVBoxLayout(connection_card)
        card_main_layout_left.setContentsMargins(0, 0, 0, 0)
        card_main_layout_left.setSpacing(0)

        # Header (now correctly positioned)
        conn_header = QLabel("1. Connection Source")
        conn_header.setObjectName("cardHeader")
        card_main_layout_left.addWidget(conn_header)
        
        # Content area with padding
        conn_content_area = QWidget()
        card_main_layout_left.addWidget(conn_content_area)
        conn_v_layout = QVBoxLayout(conn_content_area)
        conn_v_layout.setContentsMargins(20, 15, 20, 20)
        conn_v_layout.setSpacing(15)

        conn_form = QFormLayout()
        conn_form.setSpacing(12)
        conn_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        conn_v_layout.addLayout(conn_form)

        self.setup_mode_combo = QComboBox()
        self.setup_mode_combo.addItems(["Dummy", "Serial", "TCP", "UDP"])
        self.setup_mode_combo.setCurrentText(self.connection_settings.get('mode','dummy').title())
        conn_form.addRow("Mode:", self.setup_mode_combo)
        
        self.conn_stack = QStackedWidget()
        conn_v_layout.addWidget(self.conn_stack)

        # Page 0: Dummy
        dummy_page = QWidget()
        dummy_layout = QVBoxLayout(dummy_page)
        dummy_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dummy_label = QLabel("✓ Using simulated dummy data.\nNo connection settings required.")
        dummy_label.setObjectName("infoLabel"); dummy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dummy_layout.addWidget(dummy_label)
        self.conn_stack.addWidget(dummy_page)

        # Page 1: Serial
        serial_page = QWidget()
        serial_form = QFormLayout(serial_page); serial_form.setSpacing(12)
        self.setup_serial_port = QComboBox(); self.setup_serial_port.setEditable(True)
        self.setup_serial_port.addItems(self.list_serial_ports())
        self.setup_serial_port.setCurrentText(self.connection_settings.get('serial_port','COM4'))
        
        # --- Create button with standard Qt icon ---
        refresh_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.setup_refresh_ports_btn = QPushButton()
        self.setup_refresh_ports_btn.setIcon(refresh_icon)
        self.setup_refresh_ports_btn.setObjectName("iconButton")
        self.setup_refresh_ports_btn.setToolTip("Refresh serial port list")
        self.setup_refresh_ports_btn.clicked.connect(self.refresh_setup_serial_ports)
        
        port_layout = QHBoxLayout(); port_layout.addWidget(self.setup_serial_port, 1); port_layout.addWidget(self.setup_refresh_ports_btn)
        self.setup_baud = QComboBox(); self.setup_baud.setEditable(True)
        self.setup_baud.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "250000", "460800", "921600", "1000000"])
        self.setup_baud.setCurrentText(str(self.connection_settings.get('baudrate',115200)))
        serial_form.addRow("Serial Port:", port_layout)
        serial_form.addRow("Baud Rate:", self.setup_baud)
        self.conn_stack.addWidget(serial_page)

        # Page 2: TCP
        tcp_page = QWidget()
        tcp_form = QFormLayout(tcp_page); tcp_form.setSpacing(12)
        self.setup_tcp_host = QLineEdit(self.connection_settings.get('tcp_host','127.0.0.1'))
        self.setup_tcp_port = QSpinBox(); self.setup_tcp_port.setRange(1, 65535)
        self.setup_tcp_port.setValue(int(self.connection_settings.get('tcp_port',9000)))
        tcp_form.addRow("Host:", self.setup_tcp_host)
        tcp_form.addRow("Port:", self.setup_tcp_port)
        self.conn_stack.addWidget(tcp_page)

        # Page 3: UDP
        udp_page = QWidget()
        udp_form = QFormLayout(udp_page); udp_form.setSpacing(12)
        self.setup_udp_host = QLineEdit(self.connection_settings.get('udp_host','0.0.0.0'))
        self.setup_udp_host.setToolTip("Use 0.0.0.0 to listen on all available network interfaces.")
        self.setup_udp_port = QSpinBox(); self.setup_udp_port.setRange(1, 65535)
        self.setup_udp_port.setValue(int(self.connection_settings.get('udp_port',9000)))
        udp_form.addRow("Listen Host:", self.setup_udp_host)
        udp_form.addRow("Port:", self.setup_udp_port)
        self.conn_stack.addWidget(udp_page)

        conn_v_layout.addStretch()

        # === RIGHT COLUMN: DATA FORMAT SETTINGS ===
        format_card = QFrame(); format_card.setObjectName("setupCard")
        content_layout.addWidget(format_card, 1)

        card_main_layout_right = QVBoxLayout(format_card)
        card_main_layout_right.setContentsMargins(0, 0, 0, 0)
        card_main_layout_right.setSpacing(0)
        
        format_header = QLabel("2. Data Format"); format_header.setObjectName("cardHeader")
        card_main_layout_right.addWidget(format_header)

        format_content_area = QWidget()
        card_main_layout_right.addWidget(format_content_area)
        format_v_layout = QVBoxLayout(format_content_area)
        format_v_layout.setContentsMargins(20, 15, 20, 20)
        format_v_layout.setSpacing(15)

        format_form = QFormLayout(); format_form.setSpacing(12)
        format_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        format_v_layout.addLayout(format_form)

        self.setup_format = QComboBox(); self.setup_format.addItems(["json_array", "csv", "raw_bytes"])
        self.setup_format.setCurrentText(self.connection_settings.get('data_format','json_array'))
        self.setup_channels = QSpinBox(); self.setup_channels.setRange(1, 1024)
        self.setup_channels.setValue(int(self.connection_settings.get('channel_count',32)))
        format_form.addRow("Format:", self.setup_format)
        format_form.addRow("Channel Count:", self.setup_channels)
        
        format_options_header = QLabel("Format-Specific Options")
        format_options_header.setObjectName("cardSubHeader")
        format_v_layout.addWidget(format_options_header)
        
        self.format_stack = QStackedWidget()
        format_v_layout.addWidget(self.format_stack)

        # Page 0: JSON (no options)
        json_page = QWidget(); self.format_stack.addWidget(json_page)

        # Page 1: CSV
        csv_page = QWidget()
        csv_form = QFormLayout(csv_page); csv_form.setSpacing(12)
        self.setup_csv_sep = QComboBox(); self.setup_csv_sep.setEditable(True)
        self.setup_csv_sep.addItems([",", ";", "|", "\\t"]); self.setup_csv_sep.setToolTip("Common separators: comma, semicolon, pipe, tab (\\t)")
        self.setup_csv_sep.setCurrentText(self.connection_settings.get('csv_separator',','))
        csv_form.addRow("Separator:", self.setup_csv_sep)
        self.format_stack.addWidget(csv_page)
        
        # Page 2: Raw Bytes
        bytes_page = QWidget()
        bytes_form = QFormLayout(bytes_page); bytes_form.setSpacing(12)
        self.setup_width = QSpinBox(); self.setup_width.setRange(1, 8); self.setup_width.setToolTip("Bytes per channel sample (e.g., 2 for uint16_t, 4 for float)")
        self.setup_width.setValue(int(self.connection_settings.get('sample_width_bytes',2)))
        self.setup_endian = QComboBox(); self.setup_endian.addItems(["little", "big"])
        self.setup_endian.setCurrentText('little' if self.connection_settings.get('little_endian',True) else 'big')
        self.setup_endian.setToolTip("Byte order for multi-byte numbers. Most systems (x86, ARM) are little-endian.")
        bytes_form.addRow("Sample Width (bytes):", self.setup_width)
        bytes_form.addRow("Endianness:", self.setup_endian)
        self.format_stack.addWidget(bytes_page)
        
        format_v_layout.addStretch()

        # --- Bottom Button Bar ---
        btn_bar = QHBoxLayout(); btn_bar.setSpacing(12)
        back_btn = QPushButton("Back to Welcome"); manage_btn = QPushButton("Manage Parameters...")
        next_btn = QPushButton("Next: Add Widgets →")
        back_btn.setObjectName("SecondaryCTA"); manage_btn.setObjectName("SecondaryCTA"); next_btn.setObjectName("PrimaryCTA")
        btn_bar.addWidget(back_btn); btn_bar.addStretch(); btn_bar.addWidget(manage_btn); btn_bar.addWidget(next_btn)
        main_layout.addLayout(btn_bar)

        # --- Stylesheet for the page (with updated icon button style) ---
        self.setup_page.setStyleSheet("""
            QWidget#setupPage { background: #1e1e1e; }
            QLabel#setupTitle { color: #ffffff; font-size: 24px; font-weight: 600; }
            QLabel#setupSubtitle { color: #aaaaaa; font-size: 14px; padding-bottom: 10px; }
            QFrame#setupCard { background: #252526; border: 1px solid #383838; border-radius: 12px; }
            QLabel#cardHeader { font-size: 16px; font-weight: 600; padding: 15px 20px; background-color: rgba(0,0,0,0.1); border-top-left-radius: 12px; border-top-right-radius: 12px; border-bottom: 1px solid #383838; }
            QLabel#cardSubHeader { color: #9cdcfe; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; border-top: 1px solid #383838; padding-top: 15px; margin-top: 10px; }
            QLabel#infoLabel { color: #21b35a; font-weight: bold; background-color: rgba(33, 179, 90, 0.1); border: 1px solid rgba(33, 179, 90, 0.2); border-radius: 6px; padding: 20px; }
            QFormLayout QLabel { color: #cccccc; font-size: 13px; padding-top: 5px; }
            QComboBox, QLineEdit, QSpinBox { padding: 8px; font-size: 13px; }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover { border-color: #66b3ff; }
            QPushButton#iconButton {
                padding: 4px;
                min-width: 34px; /* Match height of other inputs */
                max-width: 34px;
                background-color: #3c3c3c;
            }
            QPushButton#iconButton:hover { background-color: #4a4a4a; }
            QPushButton { padding: 10px 16px; font-size: 13px; font-weight: 600; }
        """)
        self.stack.addWidget(self.setup_page)

        # --- Connections ---
        self.setup_mode_combo.currentIndexChanged.connect(self.conn_stack.setCurrentIndex)
        self.conn_stack.setCurrentIndex(self.setup_mode_combo.findText(self.connection_settings.get('mode','dummy').title()))
        
        def _set_format_stack(text):
            if text == "csv": self.format_stack.setCurrentIndex(1)
            elif text == "raw_bytes": self.format_stack.setCurrentIndex(2)
            else: self.format_stack.setCurrentIndex(0)
        self.setup_format.currentTextChanged.connect(_set_format_stack)
        _set_format_stack(self.setup_format.currentText())

        back_btn.clicked.connect(lambda: self.show_phase("welcome"))
        manage_btn.clicked.connect(self.manage_parameters)
        def _start():
            self.connection_settings = {
                'mode': self.setup_mode_combo.currentText().lower(),
                'serial_port': self.setup_serial_port.currentText().strip(),
                'baudrate': int(self.setup_baud.currentText()),
                'tcp_host': self.setup_tcp_host.text().strip(),
                'tcp_port': int(self.setup_tcp_port.value()),
                'udp_host': self.setup_udp_host.text().strip(),
                'udp_port': int(self.setup_udp_port.value()),
                'timeout': 1.0, 'data_format': self.setup_format.currentText(),
                'channel_count': int(self.setup_channels.value()),
                'sample_width_bytes': int(self.setup_width.value()),
                'little_endian': (self.setup_endian.currentText() == 'little'),
                'csv_separator': self.setup_csv_sep.currentText().replace('\\t', '\t'),
            }
            self.restart_simulator(); self.show_phase("widgets")
        next_btn.clicked.connect(_start)

    def _build_widgets_page(self):
        self.widgets_page = QWidget()
        main_layout = QVBoxLayout(self.widgets_page)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("<h2 style='color: #ffffff; margin: 0 0 16px 0;'>Configure Dashboard Widgets</h2>")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("<p style='color: #aaaaaa; margin: 0 0 20px 0;'>Add widgets to display your telemetry data. You can always add more widgets later from the dashboard.</p>")
        main_layout.addWidget(desc)
        
        # Widget configuration area
        config_group = QGroupBox("Widget Configuration")
        config_layout = QVBoxLayout(config_group)
        config_layout.setSpacing(12)
        
        # Current widgets list
        self.widgets_list = QListWidget()
        self.widgets_list.setMinimumHeight(200)
        self.widgets_list.setToolTip("Widgets that will be added to your dashboard")
        config_layout.addWidget(QLabel("Widgets to be added:"))
        config_layout.addWidget(self.widgets_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_widget_btn = QPushButton("Add Widget...")
        add_widget_btn.setObjectName("PrimaryCTA")
        remove_widget_btn = QPushButton("Remove Selected")
        remove_widget_btn.setObjectName("SecondaryCTA")
        clear_widgets_btn = QPushButton("Clear All")
        clear_widgets_btn.setObjectName("SecondaryCTA")
        
        add_widget_btn.clicked.connect(self.add_widget_to_config)
        remove_widget_btn.clicked.connect(self.remove_selected_widget)
        clear_widgets_btn.clicked.connect(self.clear_all_widgets)
        
        btn_layout.addWidget(add_widget_btn)
        btn_layout.addWidget(remove_widget_btn)
        btn_layout.addWidget(clear_widgets_btn)
        btn_layout.addStretch()
        
        config_layout.addLayout(btn_layout)
        main_layout.addWidget(config_group)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Back to Setup")
        back_btn.setObjectName("SecondaryCTA")
        skip_btn = QPushButton("Skip (Add widgets later)")
        skip_btn.setObjectName("SecondaryCTA")
        create_btn = QPushButton("Create Dashboard")
        create_btn.setObjectName("PrimaryCTA")
        
        back_btn.clicked.connect(lambda: self.show_phase("setup"))
        skip_btn.clicked.connect(self.create_dashboard_without_widgets)
        create_btn.clicked.connect(self.create_dashboard_with_widgets)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(skip_btn)
        nav_layout.addWidget(create_btn)
        
        main_layout.addLayout(nav_layout)
        self.stack.addWidget(self.widgets_page)
        
        # Initialize empty widgets list
        self.configured_widgets = []
        
        # Add default parameters if none exist
        # if not self.parameters:
        #     self.create_default_parameters()

    def add_widget_to_config(self):
        """Add a widget to the configuration list"""
        if not self.parameters:
            QMessageBox.warning(self, "No Parameters", "Please add some parameters first using 'Manage Parameters'.")
            return
        
        dialog = AddWidgetDialog(self.parameters, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selection = dialog.get_selection()
            if selection:
                # Create a descriptive name for the widget
                param_names = [p['name'] for p in self.parameters if p['id'] in selection['param_ids']]
                widget_name = f"{selection['displayType']}: {', '.join(param_names)}"
                
                # Add to configured widgets list
                widget_config = {
                    'id': str(uuid.uuid4()),
                    'name': widget_name,
                    'config': selection
                }
                self.configured_widgets.append(widget_config)
                self.mark_as_unsaved()
                
                # Update the display list
                self.refresh_widgets_list()

    def remove_selected_widget(self):
        """Remove the selected widget from configuration"""
        current_row = self.widgets_list.currentRow()
        if current_row >= 0 and current_row < len(self.configured_widgets):
            del self.configured_widgets[current_row]
            self.refresh_widgets_list()

    def clear_all_widgets(self):
        """Clear all configured widgets"""
        if self.configured_widgets:
            reply = QMessageBox.question(self, "Clear All Widgets", 
                                       "Are you sure you want to remove all configured widgets?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.configured_widgets.clear()
                self.refresh_widgets_list()

    def refresh_widgets_list(self):
        """Refresh the widgets list display"""
        self.widgets_list.clear()
        for widget in self.configured_widgets:
            item = QListWidgetItem(widget['name'])
            item.setData(Qt.ItemDataRole.UserRole, widget['id'])
            self.widgets_list.addItem(item)

    def create_dashboard_without_widgets(self):
        """Create dashboard without any widgets"""
        self.create_dashboard_with_widgets()

    def create_dashboard_with_widgets(self):
        """Create dashboard and add configured widgets"""
        # Create the main tab
        self.show_phase("dashboard")
        
        # Ensure we have a tab at index 0
        if self.tab_widget.count() == 0:
            self.add_new_tab(name="Main View", is_closable=False)
        
        # Add configured widgets to the main tab
        if self.configured_widgets:
            for widget_config in self.configured_widgets:
                self.add_widget_to_dashboard(widget_config['config'], 0, widget_config['id'])
        
        # Show success message if widgets were added
        if self.configured_widgets:
            QMessageBox.information(self, "Dashboard Created", 
                                  f"Dashboard created successfully with {len(self.configured_widgets)} widget(s)!")

    def create_default_parameters(self):
        """Create default parameters for demonstration"""
        default_params = [
            {
                'id': 'temp_sensor',
                'name': 'Temperature',
                'array_index': 0,
                'sensor_group': 'Temperature',
                'unit': '°C',
                'description': 'Ambient temperature sensor',
                'color': '#FF3131',
                'decimals': 1,
                'threshold': {'low_crit': -10, 'low_warn': 0, 'high_warn': 80, 'high_crit': 100}
            },
            {
                'id': 'humidity',
                'name': 'Humidity',
                'array_index': 1,
                'sensor_group': 'Environmental',
                'unit': '%',
                'description': 'Relative humidity sensor',
                'color': '#00BFFF',
                'decimals': 1,
                'threshold': {'low_crit': 0, 'low_warn': 20, 'high_warn': 80, 'high_crit': 100}
            },
            {
                'id': 'pressure',
                'name': 'Pressure',
                'array_index': 2,
                'sensor_group': 'Environmental',
                'unit': 'hPa',
                'description': 'Atmospheric pressure sensor',
                'color': '#21b35a',
                'decimals': 2,
                'threshold': {'low_crit': 800, 'low_warn': 900, 'high_warn': 1100, 'high_crit': 1200}
            },
            {
                'id': 'accel_x',
                'name': 'Acceleration X',
                'array_index': 3,
                'sensor_group': 'IMU',
                'unit': 'm/s²',
                'description': 'X-axis acceleration from IMU',
                'color': '#FFBF00',
                'decimals': 2,
                'threshold': {'low_crit': -20, 'low_warn': -10, 'high_warn': 10, 'high_crit': 20}
            },
            {
                'id': 'accel_y',
                'name': 'Acceleration Y',
                'array_index': 4,
                'sensor_group': 'IMU',
                'unit': 'm/s²',
                'description': 'Y-axis acceleration from IMU',
                'color': '#F012BE',
                'decimals': 2,
                'threshold': {'low_crit': -20, 'low_warn': -10, 'high_warn': 10, 'high_crit': 20}
            },
            {
                'id': 'accel_z',
                'name': 'Acceleration Z',
                'array_index': 5,
                'sensor_group': 'IMU',
                'unit': 'm/s²',
                'description': 'Z-axis acceleration from IMU',
                'color': '#39CCCC',
                'decimals': 2,
                'threshold': {'low_crit': -20, 'low_warn': -10, 'high_warn': 10, 'high_crit': 20}
            },
            {
                'id': 'gps_lat',
                'name': 'GPS Latitude',
                'array_index': 6,
                'sensor_group': 'GPS',
                'unit': '°',
                'description': 'GPS latitude coordinate',
                'color': '#FF851B',
                'decimals': 6,
                'threshold': {'low_crit': -90, 'low_warn': -80, 'high_warn': 80, 'high_crit': 90}
            },
            {
                'id': 'gps_lon',
                'name': 'GPS Longitude',
                'array_index': 7,
                'sensor_group': 'GPS',
                'unit': '°',
                'description': 'GPS longitude coordinate',
                'color': '#FF851B',
                'decimals': 6,
                'threshold': {'low_crit': -180, 'low_warn': -170, 'high_warn': 170, 'high_crit': 180}
            }
        ]
        
        self.parameters.extend(default_params)
        self.update_filter_menus()  # NEW: Update menus after adding default params

    def open_logging_config(self):
        """Open data logging configuration dialog"""
        dialog = DataLoggingDialog(self.parameters, self.logging_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.logging_settings = dialog.get_settings()
            
            # Get file path (empty means auto-generate in logs folder)
            file_path = self.logging_settings.get('file_path', '') or None  # Fixed: handle None case
            if file_path:
                file_path = file_path.strip()
                if not file_path:  # If empty after strip
                    file_path = None
            
            # Configure the data logger
            selected_params = [p for p in self.parameters if p['id'] in self.logging_settings['selected_params']]
            self.data_logger.configure(
                format_type=self.logging_settings['format'],
                file_path=file_path,
                parameters=selected_params,
                buffer_size=self.logging_settings['buffer_size']
            )
            self.mark_as_unsaved()
            
            # Show where the file will be saved
            log_location = self.data_logger.log_file_path
            QMessageBox.information(self, "Logging Configured", 
                                f"Data logging configured for {len(selected_params)} parameters.\n\n"
                                f"Log file will be saved to:\n{log_location}")

    def start_logging(self):
        """Start data logging"""
        if not self.logging_settings:
            QMessageBox.warning(self, "Not Configured", "Please configure data logging first.")
            return
        
        try:
            self.data_logger.start_logging()
            self.update_logging_button()
            
            # Show success notification
            filename = os.path.basename(self.data_logger.log_file_path)
            QMessageBox.information(self, "Logging Started", 
                                f"Data logging started to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Logging Error", f"Failed to start logging: {str(e)}")

    def stop_logging(self):
        """Stop data logging"""
        if self.data_logger.is_logging:
            self.data_logger.stop_logging()
            self.update_logging_button()
            QMessageBox.information(self, "Logging Stopped", "Data logging has been stopped.")

    def generate_summary_report(self):
        """Generate a PDF summary report from logged data"""
        
        # Check if ReportLab is available
        if not REPORTLAB_AVAILABLE:
            reply = QMessageBox.question(
                self, 
                "Library Required", 
                "PDF generation requires the 'reportlab' library.\n\n"
                "Would you like to install it now?\n\n"
                "You can install it manually with: pip install reportlab",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                QMessageBox.information(self, "Install Instructions", 
                                    "Please run the following command in your terminal:\n\n"
                                    "pip install reportlab\n\n"
                                    "Then restart Glance.")
            return
        
        # Check if there's any logged data
        if not self.data_logger.log_file_path or not os.path.exists(self.data_logger.log_file_path):
            QMessageBox.warning(self, "No Data Logged", 
                            "No logged data found. Please start logging first, then stop it to generate a report.")
            return
        
        # Ask user for output location
        default_name = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Summary Report", 
            default_name,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not pdf_path:
            return
        
        # Create a progress dialog that allows the UI to remain responsive
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import Qt
        
        progress = QProgressDialog("Analyzing logged data and generating PDF report...", None, 0, 0, self)
        progress.setWindowTitle("Generating Report")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)  # No cancel button
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.show()
        
        # Force the progress dialog to appear
        QApplication.processEvents()
        
        try:
            # Parse the logged data
            progress.setLabelText("Step 1/2: Parsing logged data...")
            QApplication.processEvents()
            
            data_summary = self._parse_logged_data()
            
            # Generate the PDF
            progress.setLabelText("Step 2/2: Creating PDF document...")
            QApplication.processEvents()
            
            self._create_pdf_report(pdf_path, data_summary)
            
            # Close progress dialog
            progress.close()
            QApplication.processEvents()
            
            # Ask if user wants to open the PDF
            reply = QMessageBox.question(
                self, 
                "Report Generated", 
                f"Summary report generated successfully!\n\n{pdf_path}\n\nWould you like to open it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                import webbrowser
                webbrowser.open(pdf_path)
                
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def _parse_logged_data(self):
        """Parse logged data file and compute statistics"""
        
        log_file = self.data_logger.log_file_path
        file_format = self.data_logger.log_format
        
        data_summary = {
            'file_path': log_file,
            'file_size': os.path.getsize(log_file),
            'format': file_format,
            'parameters': {},
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'total_samples': 0
        }
        
        try:
            if file_format == 'csv':
                # Parse CSV file
                with open(log_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    if not rows:
                        return data_summary
                    
                    data_summary['total_samples'] = len(rows)
                    
                    # Get time range
                    if 'timestamp' in rows[0]:
                        data_summary['start_time'] = rows[0]['timestamp']
                        data_summary['end_time'] = rows[-1]['timestamp']
                    
                    if 'elapsed_time' in rows[0] and rows[-1]['elapsed_time']:
                        try:
                            data_summary['duration'] = float(rows[-1]['elapsed_time'])
                        except:
                            pass
                    
                    # Compute statistics for each parameter
                    for param in self.data_logger.parameters:
                        param_id = param['id']
                        param_name = param['name']
                        
                        # Find the column
                        col_name = None
                        for key in rows[0].keys():
                            if param_id in key:
                                col_name = key
                                break
                        
                        if col_name:
                            values = []
                            for row in rows:
                                try:
                                    val = float(row[col_name])
                                    values.append(val)
                                except:
                                    pass
                            
                            if values:
                                data_summary['parameters'][param_name] = {
                                    'unit': param['unit'],
                                    'count': len(values),
                                    'min': min(values),
                                    'max': max(values),
                                    'mean': sum(values) / len(values),
                                    'values': values  # Store for plotting
                                }
            
            elif file_format == 'json':
                # Parse JSON Lines file
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # Skip comment lines
                    json_lines = [line for line in lines if not line.strip().startswith('#')]
                    
                    if not json_lines:
                        return data_summary
                    
                    data_summary['total_samples'] = len(json_lines)
                    
                    # Parse first and last entries
                    first_entry = json.loads(json_lines[0])
                    last_entry = json.loads(json_lines[-1])
                    
                    data_summary['start_time'] = first_entry.get('timestamp', '')
                    data_summary['end_time'] = last_entry.get('timestamp', '')
                    data_summary['duration'] = last_entry.get('elapsed_time', 0)
                    
                    # Collect all values
                    param_values = {}
                    for line in json_lines:
                        entry = json.loads(line)
                        params = entry.get('parameters', {})
                        
                        for param_id, value in params.items():
                            if value is not None:
                                if param_id not in param_values:
                                    param_values[param_id] = []
                                param_values[param_id].append(value)
                    
                    # Compute statistics
                    for param in self.data_logger.parameters:
                        param_id = param['id']
                        param_name = param['name']
                        
                        if param_id in param_values:
                            values = param_values[param_id]
                            data_summary['parameters'][param_name] = {
                                'unit': param['unit'],
                                'count': len(values),
                                'min': min(values),
                                'max': max(values),
                                'mean': sum(values) / len(values),
                                'values': values
                            }
        
        except Exception as e:
            print(f"Error parsing log file: {e}")
            import traceback
            traceback.print_exc()
        
        return data_summary
    
    def _create_pdf_report(self, pdf_path, data_summary):
        """Create a formatted PDF report"""
        
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0a84ff'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1c9c4f'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Glance Telemetry Data Summary Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        story.append(Paragraph("Report Information", heading_style))
        
        meta_data = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Data Source:', os.path.basename(data_summary['file_path'])],
            ['File Size:', f"{data_summary['file_size'] / 1024:.2f} KB"],
            ['Data Format:', data_summary['format'].upper()],
            ['Total Samples:', str(data_summary['total_samples'])],
        ]
        
        if data_summary['start_time']:
            meta_data.append(['Start Time:', data_summary['start_time']])
        if data_summary['end_time']:
            meta_data.append(['End Time:', data_summary['end_time']])
        if data_summary['duration']:
            hours = int(data_summary['duration'] // 3600)
            minutes = int((data_summary['duration'] % 3600) // 60)
            seconds = int(data_summary['duration'] % 60)
            meta_data.append(['Duration:', f"{hours:02d}:{minutes:02d}:{seconds:02d}"])
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Parameter statistics
        if data_summary['parameters']:
            story.append(Paragraph("Parameter Statistics", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Create statistics table
            stats_data = [['Parameter', 'Unit', 'Samples', 'Min', 'Max', 'Mean']]
            
            for param_name, stats in data_summary['parameters'].items():
                stats_data.append([
                    param_name,
                    stats['unit'],
                    str(stats['count']),
                    f"{stats['min']:.3f}",
                    f"{stats['max']:.3f}",
                    f"{stats['mean']:.3f}"
                ])
            
            stats_table = Table(stats_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.9*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a84ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Add detailed breakdown for each parameter
            story.append(PageBreak())
            story.append(Paragraph("Detailed Parameter Analysis", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            for param_name, stats in data_summary['parameters'].items():
                # Parameter name
                param_title = ParagraphStyle(
                    'ParamTitle',
                    parent=styles['Heading3'],
                    fontSize=13,
                    textColor=colors.HexColor('#333333'),
                    spaceAfter=8
                )
                story.append(Paragraph(f"{param_name} ({stats['unit']})", param_title))
                
                # Detailed stats
                detail_data = [
                    ['Metric', 'Value'],
                    ['Sample Count', str(stats['count'])],
                    ['Minimum Value', f"{stats['min']:.6f}"],
                    ['Maximum Value', f"{stats['max']:.6f}"],
                    ['Mean (Average)', f"{stats['mean']:.6f}"],
                    ['Range', f"{stats['max'] - stats['min']:.6f}"],
                ]
                
                # Calculate additional statistics if enough data
                if len(stats['values']) > 1:
                    # Standard deviation
                    mean = stats['mean']
                    variance = sum((x - mean) ** 2 for x in stats['values']) / len(stats['values'])
                    std_dev = variance ** 0.5
                    detail_data.append(['Standard Deviation', f"{std_dev:.6f}"])
                
                detail_table = Table(detail_data, colWidths=[2*inch, 2*inch])
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1c9c4f')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(detail_table)
                story.append(Spacer(1, 0.2*inch))
        
        else:
            story.append(Paragraph("No parameter data found in log file.", styles['Normal']))
        
        # Footer with logo/branding
        story.append(PageBreak())
        story.append(Spacer(1, 2*inch))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("Report generated by Glance Telemetry Dashboard", footer_style))
        story.append(Paragraph("© 2025 Team Ignition · Software Department", footer_style))
        
        # Build PDF
        doc.build(story)

            
    def update_connection_status(self):
        """Update connection status display (both header and status bar)"""
        if not self.simulator:
            # Not connected
            self.connection_status_label.setText("Not Connected")
            self.connection_status_label.setStyleSheet("color: #ff3131; font-weight: bold;")
            # Update status bar too
            if hasattr(self, 'status_conn_label'):
                self.status_conn_label.setText("● Disconnected")
                self.status_conn_label.setStyleSheet("color: #ff3131;")
            return
        
        mode = self.connection_settings.get('mode', 'dummy')
        
        if mode == 'dummy':
            self.connection_status_label.setText("Connected (Dummy Data)")
            self.connection_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
            if hasattr(self, 'status_conn_label'):
                self.status_conn_label.setText("● Connected (Dummy)")
                self.status_conn_label.setStyleSheet("color: #21b35a;")
        else:
            # Check if backend connection is actually alive
            is_connected = False
            
            if hasattr(self.simulator, 'reader') and self.simulator.reader:
                if mode == 'serial':
                    try:
                        is_connected = (hasattr(self.simulator.reader, 'ser') and 
                                    self.simulator.reader.ser and 
                                    self.simulator.reader.ser.is_open)
                    except:
                        is_connected = False
                        
                elif mode == 'tcp':
                    try:
                        is_connected = (hasattr(self.simulator.reader, 'sock') and 
                                    self.simulator.reader.sock is not None)
                        # Additional check: try to get socket error state
                        if is_connected:
                            try:
                                # Check if socket is still connected using getsockopt
                                import socket
                                error = self.simulator.reader.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                                is_connected = (error == 0)
                            except:
                                is_connected = False
                    except:
                        is_connected = False
                        
                elif mode == 'udp':
                    try:
                        is_connected = (hasattr(self.simulator.reader, 'sock') and 
                                    self.simulator.reader.sock is not None)
                    except:
                        is_connected = False
            
            # Update UI based on actual connection state
            if is_connected:
                if mode == 'serial':
                    port = self.connection_settings.get('serial_port', 'N/A')
                    self.connection_status_label.setText(f"Connected (Serial: {port})")
                    if hasattr(self, 'status_conn_label'):
                        self.status_conn_label.setText(f"● Serial: {port}")
                        self.status_conn_label.setStyleSheet("color: #21b35a;")
                elif mode == 'tcp':
                    host = self.connection_settings.get('tcp_host', 'N/A')
                    port = self.connection_settings.get('tcp_port', 'N/A')
                    self.connection_status_label.setText(f"Connected (TCP: {host}:{port})")
                    if hasattr(self, 'status_conn_label'):
                        self.status_conn_label.setText(f"● TCP: {host}:{port}")
                        self.status_conn_label.setStyleSheet("color: #21b35a;")
                elif mode == 'udp':
                    host = self.connection_settings.get('udp_host', 'N/A')
                    port = self.connection_settings.get('udp_port', 'N/A')
                    self.connection_status_label.setText(f"Connected (UDP: {host}:{port})")
                    if hasattr(self, 'status_conn_label'):
                        self.status_conn_label.setText(f"● UDP: {port}")
                        self.status_conn_label.setStyleSheet("color: #21b35a;")
                
                self.connection_status_label.setStyleSheet("color: #21b35a; font-weight: bold;")
            else:
                # Not connected - show attempting
                if mode == 'serial':
                    port = self.connection_settings.get('serial_port', 'N/A')
                    self.connection_status_label.setText(f"Disconnected (Serial: {port})")
                    if hasattr(self, 'status_conn_label'):
                        self.status_conn_label.setText(f"● Disconnected")
                        self.status_conn_label.setStyleSheet("color: #ff9800;")
                elif mode == 'tcp':
                    host = self.connection_settings.get('tcp_host', 'N/A')
                    port = self.connection_settings.get('tcp_port', 'N/A')
                    self.connection_status_label.setText(f"Connecting (TCP: {host}:{port})...")
                    if hasattr(self, 'status_conn_label'):
                        self.status_conn_label.setText(f"● Connecting...")
                        self.status_conn_label.setStyleSheet("color: #ff9800;")
                elif mode == 'udp':
                    port = self.connection_settings.get('udp_port', 'N/A')
                    self.connection_status_label.setText(f"Listening (UDP: {port})")
                    if hasattr(self, 'status_conn_label'):
                        self.status_conn_label.setText(f"● Listening")
                        self.status_conn_label.setStyleSheet("color: #ff9800;")
                
                self.connection_status_label.setStyleSheet("color: #ff9800; font-weight: bold;")

    def _build_dashboard_page(self):
        self.dashboard_page = QWidget(); layout = QVBoxLayout(self.dashboard_page)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.tab_widget)
        self.stack.addWidget(self.dashboard_page)
        # start with a default tab only when entering dashboard the first time

    def show_phase(self, which):
        # Exit fullscreen when changing phases (except when staying in dashboard)
        if self.is_fullscreen and which != "dashboard":
            self.toggle_fullscreen()
        
        # Hide dashboard-specific docks outside dashboard phase
        is_dashboard = (which == "dashboard")
        if hasattr(self, 'control_dock') and self.control_dock:
            self.control_dock.setVisible(is_dashboard)
        if hasattr(self, 'header_dock') and self.header_dock:
            self.header_dock.setVisible(is_dashboard and not self.is_fullscreen)
        
        # NEW: Customize menu bar based on phase
        is_welcome = (which == "welcome")
        is_splash = (which == "splash")
        
        # Hide menu bar during splash or fullscreen
        if is_splash or self.is_fullscreen:
            self.menuBar().setVisible(False)
        elif is_welcome:
            # Show minimal menu bar for welcome screen
            self._build_welcome_menu_bar()
            self.menuBar().setVisible(True)
        else:
            # Show full menu bar for other phases
            self._build_menu_bar()
            self.menuBar().setVisible(True)
        
        # Update status bar visibility
        self.update_status_bar_visibility(which)
        
        # Handle splash screen
        if which == "splash":
            self.stack.setCurrentWidget(self.splash_page)
            # Start timer to transition to welcome after 2 seconds
            self.splash_timer.start(2000)
        elif which == "welcome":
            self.stack.setCurrentWidget(self.welcome_page)
        elif which == "setup":
            self.stack.setCurrentWidget(self.setup_page)
        elif which == "widgets":
            self.stack.setCurrentWidget(self.widgets_page)
        else:  # dashboard
            self.stack.setCurrentWidget(self.dashboard_page)
            if self.tab_widget.count() == 0:
                self.add_new_tab(name="Main View", is_closable=False)

    def show_fullscreen_hint(self):
        """Show a temporary hint that fullscreen is active"""
        hint = QLabel("Fullscreen Mode - Press F11 or ESC to exit", self)
        hint.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: bold;
        """)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Position at top center
        hint.adjustSize()
        x = (self.width() - hint.width()) // 2
        hint.move(x, 20)
        hint.show()
        
        # Fade out after 3 seconds
        QTimer.singleShot(3000, hint.deleteLater)

    def open_connection_settings(self):
        dialog = ConnectionSettingsDialog(self.connection_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.connection_settings = dialog.get_settings()
            self.mark_as_unsaved()
            
            # Stop current simulator
            if self.simulator:
                self.simulator.stop()
                self.simulator.wait()
            
            # Restart with new settings
            self.restart_simulator()
            
            # Force immediate status update
            # QTimer.singleShot(500, self.update_status_bar)
            QTimer.singleShot(500, self.update_connection_status)
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QDialog { background-color: #1e1e1e; color: #d4d4d4; }
            QWidget { font-size: 13px; }
            QDockWidget { background-color: #252526; }
            QDockWidget::title { background-color: #2c2c2c; padding: 6px; border-radius: 4px; font-weight: bold; }
            QGroupBox { border: 1px solid #3a3a3a; margin-top: 1em; padding: 0.75em; border-radius: 6px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; background-color: transparent; }
            QPushButton { background-color: #0a84ff; border: none; padding: 9px 14px; border-radius: 6px; color: #fff; }
            QPushButton:hover { background-color: #1a8fff; }
            QPushButton:pressed { background-color: #0969c3; }
            QPushButton#PrimaryCTA { background-color: #1c9c4f; }
            QPushButton#PrimaryCTA:hover { background-color: #21b35a; }
            QPushButton#SecondaryCTA { background-color: #3c3c3c; }
            QPushButton#SecondaryCTA:hover { background-color: #4a4a4a; }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox { background-color: #2b2b2b; border: 1px solid #4a4a4a; border-radius: 6px; padding: 6px; }
            QTableWidget { background-color: #202020; gridline-color: #444444; }
            QHeaderView::section { background-color: #2a2a2a; border: 1px solid #444444; padding: 6px; }
            QListWidget { background-color: #202020; border: 1px solid #333; border-radius: 6px; }
            QTabWidget::pane { border: 1px solid #333; }
            QTabBar::tab { background: #252526; border: 1px solid #333; padding: 8px 14px; border-bottom: none; }
            QTabBar::tab:selected { background: #343434; }
            QStatusBar QLabel#SBClock { color: #9cdcfe; padding-left: 10px; }
            QStatusBar QLabel#SBConn { color: #ce9178; padding-right: 10px; }
            QStatusBar QLabel#SBRx { color: #b5cea8; padding-right: 10px; }
        """)

    def closeEvent(self, event):
        """Handle application close with unsaved changes check"""
        # Check for unsaved changes
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
                if self.has_unsaved_changes:  # Still unsaved after save attempt
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Stop data logging if active
        if self.data_logger.is_logging:
            self.data_logger.stop_logging()
        
        # Stop raw telemetry monitor if active
        if self.raw_tlm_monitor:
            try:
                # Force disconnect to stop thread
                if hasattr(self.raw_tlm_monitor, 'disconnect_source'):
                    self.raw_tlm_monitor.disconnect_source()
                self.raw_tlm_monitor.close()
            except Exception:
                pass
            
        # Stop simulator
        try:
            if self.simulator:
                self.simulator.stop()
                self.simulator._is_paused = True
                try:
                    if hasattr(self.simulator, 'reader') and self.simulator.reader:
                        self.simulator.reader.close()
                except Exception:
                    pass
                self.simulator.wait(1000)
        except Exception:
            pass
        
        super().closeEvent(event)
