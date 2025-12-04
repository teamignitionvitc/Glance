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
# File:        test_widgets.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Unit tests for widgets.
# @details     Tests widget functionality.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side layout and QStackedWidget
####################################################################################################

####################################################################################################
# Imports

import pytest
from PySide6.QtWidgets import QApplication
from app.widgets.general import ValueCard, GaugeWidget, TimeGraph, HistogramWidget, LEDWidget, MapWidget, LogTable

class TestWidgets:
    @pytest.fixture
    def param_config(self):
        return {
            'id': 'test_param',
            'name': 'Test Parameter',
            'unit': 'V',
            'color': '#FF0000',
            'threshold': {'low_crit': 0, 'low_warn': 10, 'high_warn': 90, 'high_crit': 100}
        }

    def test_value_card_instantiation(self, qapp, param_config):
        # ValueCard now expects a list of param_configs
        widget = ValueCard([param_config], "High")
        assert widget is not None
        assert len(widget.param_configs) == 1

    def test_gauge_widget_instantiation(self, qapp, param_config):
        widget = GaugeWidget(param_config)
        assert widget is not None
        assert len(widget.param_configs) == 1
        assert widget.param_configs[0] == param_config

    def test_time_graph_instantiation(self, qapp, param_config):
        # TimeGraph expects a list of configs
        widget = TimeGraph([param_config])
        assert widget is not None
        assert len(widget.param_configs) == 1

    def test_histogram_widget_instantiation(self, qapp, param_config):
        widget = HistogramWidget(param_config)
        assert widget is not None
        assert widget.param == param_config

    def test_led_widget_instantiation(self, qapp, param_config):
        # LEDWidget now expects a list of param_configs
        widget = LEDWidget([param_config])
        assert widget is not None
        assert len(widget.param_configs) == 1

    def test_log_table_instantiation(self, qapp, param_config):
        widget = LogTable([param_config])
        assert widget is not None
        assert len(widget.param_configs) == 1

    def test_value_card_update(self, qapp, param_config):
        widget = ValueCard([param_config])
        widget.update_values({'test_param': 123.45})
        assert widget.value_labels['test_param'].text() == "123.5"

    def test_gauge_widget_update(self, qapp, param_config):
        widget = GaugeWidget(param_config)
        widget.update_values({'test_param': 50.0})
        assert widget.gauges['test_param'].value == 50.0

    def test_closable_dock_instantiation(self, qapp):
        from app.widgets.general import ClosableDock
        from PySide6.QtWidgets import QMainWindow
        mw = QMainWindow()
        dock = ClosableDock("Test Dock", mw, widget_id="test_id")
        dock.setObjectName("dock_test_id") 
        
        assert dock.widget_id == "test_id"
        assert dock.objectName() == "dock_test_id"
        assert dock.windowTitle() == "Test Dock"
