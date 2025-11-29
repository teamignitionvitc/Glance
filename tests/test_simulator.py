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
# File:        test_simulator.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Unit tests for simulator.
# @details     Tests data simulation.
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
import time
from PySide6.QtCore import QCoreApplication
from app.core.simulator import DataSimulator

class TestDataSimulator:
    def test_initialization(self, qapp):
        sim = DataSimulator(num_channels=10)
        assert sim.num_channels == 10
        assert sim.mode == 'dummy'
        assert sim.isRunning() is False

    def test_dummy_data_generation(self, qapp):
        sim = DataSimulator(num_channels=5) # Fixed rate ~10Hz
        
        received_data = []
        def on_data(data):
            received_data.append(data)
            
        sim.newData.connect(on_data)
        sim.start()
        
        # Let it run for a bit
        start_time = time.time()
        while time.time() - start_time < 0.5:
            QCoreApplication.processEvents()
            time.sleep(0.01)
            
        sim.stop()
        sim.wait()
        
        assert len(received_data) > 0
        assert len(received_data[0]) == 5
        assert all(isinstance(x, float) for x in received_data[0])

    def test_pause_resume(self, qapp):
        sim = DataSimulator()
        sim.start()
        assert sim._is_paused is False
        
        sim.toggle_pause()
        assert sim._is_paused is True
        
        sim.toggle_pause()
        assert sim._is_paused is False
        
        sim.stop()
        sim.wait()
