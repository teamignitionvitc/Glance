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
# File:        filters.py
# Author:      Shawn Liju Thomas
# Created On:  16-09-2025
#
# @brief       Signal filtering implementations.
# @details     Contains classes for Moving Average, Low Pass, Kalman, and Median filters, and a manager class.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MODify | ADD | DELete)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      16-09-2025  Shawn Liju Thomas    Initial creation
####################################################################################################

####################################################################################################
# Imports

from abc import ABC, abstractmethod
from collections import deque

####################################################################################################

class SignalFilter(ABC):
    """
    @brief Abstract base class for all signal filters.
    @details Defines the interface for applying, resetting, and serializing filters.
    """
    
    def __init__(self, filter_id, filter_name):
        self.filter_id = filter_id
        self.filter_name = filter_name
        self.enabled = True
    
    @abstractmethod
    def apply(self, value, timestamp=None):
        """
        @brief Apply the filter to a value.
        @param value The input value to filter.
        @param timestamp Optional timestamp for the value.
        @return The filtered value.
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset the filter state"""
        pass
    
    @abstractmethod
    def to_dict(self):
        """Serialize filter configuration to dictionary"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """Deserialize filter from dictionary"""
        pass


class MovingAverageFilter(SignalFilter):
    """
    @brief Simple moving average filter.
    @details Calculates the unweighted mean of the previous n data points.
    """
    
    def __init__(self, filter_id, window_size=5):
        super().__init__(filter_id, "Moving Average")
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
    
    def apply(self, value, timestamp=None):
        if value is None:
            return None
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)
    
    def reset(self):
        self.buffer.clear()
    
    def to_dict(self):
        return {
            'type': 'moving_average',
            'filter_id': self.filter_id,
            'filter_name': self.filter_name,
            'window_size': self.window_size,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        f = cls(data['filter_id'], data['window_size'])
        f.enabled = data.get('enabled', True)
        return f


class LowPassFilter(SignalFilter):
    """
    @brief Simple low-pass filter (exponential moving average).
    @details Smooths the signal using an exponential weighting factor (alpha).
    """
    
    def __init__(self, filter_id, alpha=0.3):
        super().__init__(filter_id, "Low Pass")
        self.alpha = alpha  # Smoothing factor (0-1), lower = more smoothing
        self.last_value = None
    
    def apply(self, value, timestamp=None):
        if value is None:
            return None
        if self.last_value is None:
            self.last_value = value
            return value
        filtered = self.alpha * value + (1 - self.alpha) * self.last_value
        self.last_value = filtered
        return filtered
    
    def reset(self):
        self.last_value = None
    
    def to_dict(self):
        return {
            'type': 'low_pass',
            'filter_id': self.filter_id,
            'filter_name': self.filter_name,
            'alpha': self.alpha,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        f = cls(data['filter_id'], data['alpha'])
        f.enabled = data.get('enabled', True)
        return f


class KalmanFilter(SignalFilter):
    """
    @brief Simple 1D Kalman filter for scalar values.
    @details Implements a basic predict-update cycle for optimal estimation.
    """
    
    def __init__(self, filter_id, process_variance=0.01, measurement_variance=0.1):
        super().__init__(filter_id, "Kalman")
        self.process_variance = process_variance  # Q
        self.measurement_variance = measurement_variance  # R
        self.estimated_value = None
        self.estimation_error = 1.0  # P
    
    def apply(self, value, timestamp=None):
        if value is None:
            return None
        
        if self.estimated_value is None:
            self.estimated_value = value
            return value
        
        # Prediction step
        predicted_error = self.estimation_error + self.process_variance
        
        # Update step
        kalman_gain = predicted_error / (predicted_error + self.measurement_variance)
        self.estimated_value = self.estimated_value + kalman_gain * (value - self.estimated_value)
        self.estimation_error = (1 - kalman_gain) * predicted_error
        
        return self.estimated_value
    
    def reset(self):
        self.estimated_value = None
        self.estimation_error = 1.0
    
    def to_dict(self):
        return {
            'type': 'kalman',
            'filter_id': self.filter_id,
            'filter_name': self.filter_name,
            'process_variance': self.process_variance,
            'measurement_variance': self.measurement_variance,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        f = cls(data['filter_id'], data['process_variance'], data['measurement_variance'])
        f.enabled = data.get('enabled', True)
        return f


class MedianFilter(SignalFilter):
    """
    @brief Median filter for removing outliers.
    @details Replaces each entry with the median of neighboring entries.
    """
    
    def __init__(self, filter_id, window_size=5):
        super().__init__(filter_id, "Median")
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
    
    def apply(self, value, timestamp=None):
        if value is None:
            return None
        self.buffer.append(value)
        sorted_buffer = sorted(self.buffer)
        n = len(sorted_buffer)
        if n % 2 == 0:
            return (sorted_buffer[n//2 - 1] + sorted_buffer[n//2]) / 2
        else:
            return sorted_buffer[n//2]
    
    def reset(self):
        self.buffer.clear()
    
    def to_dict(self):
        return {
            'type': 'median',
            'filter_id': self.filter_id,
            'filter_name': self.filter_name,
            'window_size': self.window_size,
            'enabled': self.enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        f = cls(data['filter_id'], data['window_size'])
        f.enabled = data.get('enabled', True)
        return f


class FilterManager:
    """
    @brief Manages filters for all parameters.
    @details Handles creation, storage, application, and serialization of filters for multiple parameters.
    """
    # Class-level registry of filter types
    FILTER_CLASSES = {
        'moving_average': MovingAverageFilter,
        'low_pass': LowPassFilter,
        'kalman': KalmanFilter,
        'median': MedianFilter
    }
    
    def __init__(self):
        self.parameter_filters = {}  # param_id -> list of filters
    
    def add_filter(self, param_id, filter_obj):
        """Add a filter to a parameter"""
        if param_id not in self.parameter_filters:
            self.parameter_filters[param_id] = []
        self.parameter_filters[param_id].append(filter_obj)
    
    def remove_filter(self, param_id, filter_id):
        """Remove a filter from a parameter"""
        if param_id in self.parameter_filters:
            self.parameter_filters[param_id] = [
                f for f in self.parameter_filters[param_id] if f.filter_id != filter_id
            ]
    
    def get_filters(self, param_id):
        """Get all filters for a parameter"""
        return self.parameter_filters.get(param_id, [])
    
    def apply_filters(self, param_id, value, timestamp=None):
        """Apply all enabled filters to a value"""
        if param_id not in self.parameter_filters:
            return value
        
        filtered_value = value
        for filter_obj in self.parameter_filters[param_id]:
            if filter_obj.enabled:
                filtered_value = filter_obj.apply(filtered_value, timestamp)
        
        return filtered_value
    
    def reset_filters(self, param_id=None):
        """Reset filters for a parameter or all parameters"""
        if param_id:
            for filter_obj in self.parameter_filters.get(param_id, []):
                filter_obj.reset()
        else:
            for filters in self.parameter_filters.values():
                for filter_obj in filters:
                    filter_obj.reset()
    
    def to_dict(self):
        """Serialize all filters"""
        result = {}
        for param_id, filters in self.parameter_filters.items():
            result[param_id] = [f.to_dict() for f in filters]
        return result
    
    def from_dict(self, data):
        """Deserialize filters"""
        self.parameter_filters.clear()
        for param_id, filter_list in data.items():
            for filter_data in filter_list:
                filter_type = filter_data['type']
                if filter_type == 'moving_average':
                    filter_obj = MovingAverageFilter.from_dict(filter_data)
                elif filter_type == 'low_pass':
                    filter_obj = LowPassFilter.from_dict(filter_data)
                elif filter_type == 'kalman':
                    filter_obj = KalmanFilter.from_dict(filter_data)
                elif filter_type == 'median':
                    filter_obj = MedianFilter.from_dict(filter_data)
                else:
                    continue
                self.add_filter(param_id, filter_obj)
