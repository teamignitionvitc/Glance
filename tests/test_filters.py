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
# File:        test_filters.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Unit tests for filters.
# @details     Tests signal filtering.
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
from app.core.filters import MovingAverageFilter, LowPassFilter, KalmanFilter, MedianFilter

def test_moving_average_filter():
    f = MovingAverageFilter("test_ma", window_size=3)
    assert f.apply(1.0) == 1.0
    assert f.apply(2.0) == 1.5
    assert f.apply(3.0) == 2.0
    assert f.apply(4.0) == 3.0 # (2+3+4)/3

def test_low_pass_filter():
    f = LowPassFilter("test_lp", alpha=0.5)
    # y[i] = alpha * x[i] + (1-alpha) * y[i-1]
    # Initial value is assumed 0 or first sample? 
    # Looking at implementation usually:
    val1 = f.apply(10.0)
    assert val1 == 10.0
    val2 = f.apply(20.0)
    assert val2 == 15.0

def test_median_filter():
    f = MedianFilter("test_med", window_size=3)
    assert f.apply(10.0) == 10.0
    assert f.apply(100.0) == 55.0 # Mean of 10, 100? No, median. [10, 100] -> 55 (avg of 2 middle) or just 100?
    # Let's check implementation behavior. Usually median of [10, 100] is 55.
    # Implementation: (sorted_buffer[n//2 - 1] + sorted_buffer[n//2]) / 2 for even n
    # [10, 100] -> (10+100)/2 = 55. Correct.
    
    assert f.apply(20.0) == 20.0 

def test_kalman_filter():
    f = KalmanFilter("test_kalman", process_variance=1e-5, measurement_variance=1e-1)
    val = f.apply(10.0)
    assert val == 10.0
    # Subsequent values should be smoothed
    val2 = f.apply(10.1)
    assert val2 != 10.1 # Should be filtered10.1
