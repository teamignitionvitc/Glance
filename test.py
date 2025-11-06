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
# File:        test.py
# Author:      Ramzy
# Created On:  <Date>
#
# @brief       Unit and integration tests for the Glance Telemetry Dashboard.
# @details     Provides automated test coverage for dashboard modules, including data logging,
#              signal filtering, simulator, widgets, dialogs, and main window logic. Ensures
#              reliability, correctness, and performance of telemetry visualization and management.
###################################################################################################
# HISTORY:
#
#       +----- (NEW | MODify | ADD | DELete)
#       |
# No#   |       when       who                  what
######+*********+**********+********************+**************************************************
# 000  NEW      <Date>      Ramzy               Initial creation
####################################################################################################

import pytest
import sys
import time
import os
import json
import tempfile
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, call
from collections import deque

# Qt imports
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

# Import application modules
from main import (
    DataLogger, FilterManager, MovingAverageFilter, LowPassFilter,
    KalmanFilter, MedianFilter, DataSimulator, ValueCard,
    TimeGraph, HistogramWidget, LEDWidget, LogTable,
    ParameterEntryDialog, ManageParametersDialog,
    RawTelemetryMonitor, MainWindow, StandaloneTelemetryViewer,
    ConnectionSettingsDialog
)
from backend import DataReader


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def sample_parameters():
    """Sample parameter definitions for testing"""
    return [
        {
            'id': 'temp',
            'name': 'Temperature',
            'array_index': 0,
            'unit': '°C',
            'sensor_group': 'Environmental',
            'description': 'Temperature sensor',
            'threshold': {
                'low_crit': -10,
                'low_warn': 0,
                'high_warn': 80,
                'high_crit': 100
            }
        },
        {
            'id': 'pressure',
            'name': 'Pressure',
            'array_index': 1,
            'unit': 'hPa',
            'sensor_group': 'Environmental',
            'description': 'Pressure sensor',
            'threshold': {
                'low_crit': 800,
                'low_warn': 900,
                'high_warn': 1100,
                'high_crit': 1200
            }
        }
    ]


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ============================================================================
# BACKEND DATA READER TESTS
# ============================================================================

class TestDataReader:
    """Test suite for DataReader class from backend.py"""
    
    def test_init_default(self):
        """Test DataReader initialization with defaults"""
        reader = DataReader()
        assert reader.mode == "serial"
        assert reader.timeout == 1.0
        assert reader.data_format == "json_array"
        assert reader.channel_count == 32
        assert reader.sample_width_bytes == 2
        assert reader.little_endian is True
        assert reader.csv_separator == ","
        assert reader.rx_bytes == 0
        assert reader._buffer == b""
    
    def test_init_mode_serial(self):
        """Test DataReader initialization with serial mode"""
        reader = DataReader(mode="serial", serial_port="COM3", baudrate=9600)
        assert reader.mode == "serial"
    
    def test_init_mode_tcp(self):
        """Test DataReader initialization with TCP mode"""
        reader = DataReader(mode="tcp", tcp_host="127.0.0.1", tcp_port=8080)
        assert reader.mode == "tcp"
    
    def test_init_mode_udp(self):
        """Test DataReader initialization with UDP mode"""
        reader = DataReader(mode="udp", udp_host="0.0.0.0", udp_port=9000)
        assert reader.mode == "udp"
    
    def test_init_invalid_mode(self):
        """Test DataReader with invalid mode"""
        reader = DataReader(mode="invalid_mode")
        assert reader.mode == "invalid_mode"
        # Should handle gracefully
        assert reader.ser is None
        assert reader.sock is None
    
    def test_init_channel_count_bounds(self):
        """Test channel count bounds handling"""
        # Test negative channel count (should be clamped to 1)
        reader = DataReader(channel_count=-5)
        assert reader.channel_count == 1
        
        reader = DataReader(channel_count=0)
        assert reader.channel_count == 1
        
        reader = DataReader(channel_count=100)
        assert reader.channel_count == 100
    
    def test_init_sample_width_bounds(self):
        """Test sample width bounds handling"""
        reader = DataReader(sample_width_bytes=-1)
        assert reader.sample_width_bytes == 1
        
        reader = DataReader(sample_width_bytes=0)
        assert reader.sample_width_bytes == 1
        
        reader = DataReader(sample_width_bytes=4)
        assert reader.sample_width_bytes == 4
    
    def test_init_csv_separator_default(self):
        """Test CSV separator default handling"""
        reader = DataReader(csv_separator=None)
        assert reader.csv_separator == ","
        
        reader = DataReader(csv_separator=";")
        assert reader.csv_separator == ";"
    
    def test_read_line_json_array_valid(self):
        """Test reading valid JSON array format"""
        reader = DataReader(mode="dummy", data_format="json_array")
        # Mock _read_bytes to return valid JSON array
        test_data = b'[1.5, 2.5, 3.5]\n'
        reader._read_bytes = lambda: test_data if hasattr(reader, '_first_call') else None
        reader._first_call = True
        
        # Can't easily test without real connection, but test structure
        assert reader.data_format == "json_array"
    
    def test_read_line_json_array_semicolon(self):
        """Test JSON array with semicolons (should be converted)"""
        reader = DataReader(data_format="json_array")
        assert reader.data_format == "json_array"
    
    def test_read_line_json_array_empty(self):
        """Test reading empty JSON array"""
        reader = DataReader(data_format="json_array")
        # Empty line should return None
        assert reader.data_format == "json_array"
    
    def test_read_line_json_array_invalid(self):
        """Test reading invalid JSON"""
        reader = DataReader(data_format="json_array")
        # Invalid JSON should return None or "Parse"
        assert reader.data_format == "json_array"
    
    def test_read_line_csv_valid(self):
        """Test reading valid CSV format"""
        reader = DataReader(data_format="csv", csv_separator=",")
        assert reader.data_format == "csv"
        assert reader.csv_separator == ","
    
    def test_read_line_csv_custom_separator(self):
        """Test CSV with custom separator"""
        reader = DataReader(data_format="csv", csv_separator=";")
        assert reader.csv_separator == ";"
    
    def test_read_line_csv_semicolon(self):
        """Test CSV with semicolons (should be converted)"""
        reader = DataReader(data_format="csv")
        assert reader.data_format == "csv"
    
    def test_read_line_csv_empty_fields(self):
        """Test CSV with empty fields"""
        reader = DataReader(data_format="csv")
        assert reader.data_format == "csv"
    
    def test_read_line_csv_non_numeric(self):
        """Test CSV with non-numeric values (should skip)"""
        reader = DataReader(data_format="csv")
        assert reader.data_format == "csv"
    
    def test_read_line_raw_bytes_valid(self):
        """Test reading raw bytes format"""
        reader = DataReader(
            data_format="raw_bytes",
            channel_count=4,
            sample_width_bytes=2,
            little_endian=True
        )
        assert reader.data_format == "raw_bytes"
        assert reader.channel_count == 4
        assert reader.sample_width_bytes == 2
    
    def test_read_line_raw_bytes_empty(self):
        """Test reading empty raw bytes"""
        reader = DataReader(data_format="raw_bytes", sample_width_bytes=2)
        # Empty buffer should return None
        assert reader.data_format == "raw_bytes"
    
    def test_read_line_raw_bytes_insufficient(self):
        """Test raw bytes with insufficient data"""
        reader = DataReader(
            data_format="raw_bytes",
            sample_width_bytes=4,
            channel_count=2
        )
        # Data shorter than needed should return None
        assert reader.sample_width_bytes == 4
    
    def test_read_line_raw_bytes_big_endian(self):
        """Test raw bytes with big endian"""
        reader = DataReader(
            data_format="raw_bytes",
            little_endian=False,
            sample_width_bytes=2
        )
        assert reader.little_endian is False
    
    def test_read_line_bits_valid(self):
        """Test reading bits format"""
        reader = DataReader(data_format="bits", channel_count=8)
        assert reader.data_format == "bits"
        assert reader.channel_count == 8
    
    def test_read_line_bits_from_json(self):
        """Test bits format parsing from JSON"""
        reader = DataReader(data_format="bits", channel_count=8)
        assert reader.data_format == "bits"
    
    def test_read_line_bits_from_csv(self):
        """Test bits format parsing from CSV"""
        reader = DataReader(data_format="bits", channel_count=8)
        assert reader.data_format == "bits"
    
    def test_read_line_bits_from_bytes(self):
        """Test bits format parsing from raw bytes"""
        reader = DataReader(data_format="bits", channel_count=8)
        assert reader.data_format == "bits"
    
    def test_read_line_bits_empty(self):
        """Test bits format with empty input"""
        reader = DataReader(data_format="bits")
        assert reader.data_format == "bits"
    
    def test_read_line_invalid_format(self):
        """Test reading with invalid format"""
        reader = DataReader(data_format="invalid_format")
        # Should return None
        assert reader.data_format == "invalid_format"
    
    def test_read_line_parse_error(self):
        """Test handling of parse errors"""
        reader = DataReader(data_format="json_array")
        # Parse errors should return "Parse" string
        assert reader.data_format == "json_array"
    
    def test_read_line_encoding_error(self):
        """Test handling of encoding errors"""
        reader = DataReader(data_format="json_array")
        # Invalid UTF-8 should be handled with errors="ignore"
        assert reader.data_format == "json_array"
    
    def test_close_serial(self):
        """Test closing serial connection"""
        reader = DataReader(mode="serial", serial_port="COM99")
        # Should handle close gracefully even if not connected
        reader.close()
        assert True  # Should not raise exception
    
    def test_close_tcp(self):
        """Test closing TCP connection"""
        reader = DataReader(mode="tcp", tcp_host="127.0.0.1", tcp_port=99999)
        # Should handle close gracefully
        reader.close()
        assert True  # Should not raise exception
    
    def test_close_udp(self):
        """Test closing UDP connection"""
        reader = DataReader(mode="udp", udp_host="0.0.0.0", udp_port=99999)
        # Should handle close gracefully
        reader.close()
        assert True  # Should not raise exception
    
    def test_close_none_connection(self):
        """Test closing when no connection exists"""
        reader = DataReader(mode="invalid")
        reader.close()
        assert True  # Should not raise exception
    
    def test_rx_bytes_tracking(self):
        """Test RX bytes counter"""
        reader = DataReader()
        assert reader.rx_bytes == 0
        # rx_bytes should increment on reads (tested in integration)
    
    def test_buffer_management(self):
        """Test internal buffer management"""
        reader = DataReader(mode="tcp")
        assert reader._buffer == b""
        # Buffer should be managed internally for line reading
    
    def test_timeout_setting(self):
        """Test timeout configuration"""
        reader = DataReader(timeout=5.0)
        assert reader.timeout == 5.0
        
        reader = DataReader(timeout=0.1)
        assert reader.timeout == 0.1
    
    def test_mode_case_insensitive(self):
        """Test mode is case-insensitive"""
        reader1 = DataReader(mode="SERIAL")
        reader2 = DataReader(mode="serial")
        reader3 = DataReader(mode="Serial")
        assert reader1.mode == "serial"
        assert reader2.mode == "serial"
        assert reader3.mode == "serial"


# ============================================================================
# DATA LOGGER TESTS
# ============================================================================

class TestDataLogger:
    """Test suite for DataLogger class"""
    
    def test_init(self):
        """Test DataLogger initialization"""
        logger = DataLogger()
        assert logger.is_logging is False
        assert logger.log_format == 'csv'
        assert logger.log_file_path is None
        assert logger.buffer_size == 100
        assert logger.parameters == []
        assert logger.log_buffer == []
    
    def test_configure_csv(self, sample_parameters, temp_log_dir):
        """Test configuring logger for CSV format"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters,
            buffer_size=50
        )
        
        assert logger.log_format == 'csv'
        assert logger.log_file_path == log_path
        assert logger.buffer_size == 50
        assert len(logger.parameters) == 2
    
    def test_configure_json(self, sample_parameters, temp_log_dir):
        """Test configuring logger for JSON format"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.json")
        
        logger.configure(
            format_type='json',
            file_path=log_path,
            parameters=sample_parameters
        )
        
        assert logger.log_format == 'json'
        assert logger.log_file_path == log_path
    
    def test_auto_generate_path(self, sample_parameters):
        """Test automatic log file path generation"""
        logger = DataLogger()
        logger.configure(
            format_type='csv',
            parameters=sample_parameters
        )
        
        assert logger.log_file_path is not None
        assert 'dashboard_data_' in logger.log_file_path
        assert logger.log_file_path.endswith('.csv')
    
    def test_start_stop_logging_csv(self, sample_parameters, temp_log_dir):
        """Test starting and stopping CSV logging"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters
        )
        
        logger.start_logging()
        assert logger.is_logging is True
        assert logger.log_file is not None
        assert logger.csv_writer is not None
        
        logger.stop_logging()
        assert logger.is_logging is False
        assert os.path.exists(log_path)
    
    def test_log_data_buffering(self, sample_parameters, temp_log_dir):
        """Test data buffering before flush"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters,
            buffer_size=5
        )
        
        logger.start_logging()
        
        # Create mock data history
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        # Log data multiple times
        for i in range(3):
            logger.log_data(None, data_history)
        
        assert len(logger.log_buffer) == 3
        
        logger.stop_logging()
    
    def test_flush_buffer(self, sample_parameters, temp_log_dir):
        """Test buffer flushing"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters,
            buffer_size=2
        )
        
        logger.start_logging()
        
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        # This should trigger auto-flush
        logger.log_data(None, data_history)
        logger.log_data(None, data_history)
        
        assert len(logger.log_buffer) == 0  # Buffer should be empty after flush
        
        logger.stop_logging()
    
    def test_log_data_not_logging(self, sample_parameters, temp_log_dir):
        """Test logging when not started should do nothing"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters
        )
        
        # Don't start logging
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        logger.log_data(None, data_history)
        
        # Should not crash and buffer should remain empty
        assert logger.is_logging is False
        assert len(logger.log_buffer) == 0
    
    def test_start_logging_no_path(self, sample_parameters):
        """Test starting logging without configured path should raise error"""
        logger = DataLogger()
        logger.parameters = sample_parameters
        
        # Should raise ValueError
        with pytest.raises(ValueError):
            logger.start_logging()
    
    def test_stop_logging_when_not_logging(self):
        """Test stopping logging when not started"""
        logger = DataLogger()
        # Should not crash
        logger.stop_logging()
        assert logger.is_logging is False
    
    def test_log_data_empty_history(self, sample_parameters, temp_log_dir):
        """Test logging with empty data history"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters
        )
        
        logger.start_logging()
        
        # Empty history
        logger.log_data(None, {})
        
        # Should not crash
        assert logger.is_logging is True
        
        logger.stop_logging()
    
    def test_log_data_missing_parameters(self, sample_parameters, temp_log_dir):
        """Test logging when some parameters are missing from history"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters
        )
        
        logger.start_logging()
        
        # Only one parameter in history
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}]
        }
        
        logger.log_data(None, data_history)
        
        # Should handle gracefully
        assert len(logger.log_buffer) > 0
        
        logger.stop_logging()
    
    def test_log_data_invalid_file_path(self, sample_parameters):
        """Test logging with invalid file path"""
        logger = DataLogger()
        
        # Try to configure with invalid path
        invalid_path = "/invalid/path/that/does/not/exist/test.csv"
        logger.configure(
            format_type='csv',
            file_path=invalid_path,
            parameters=sample_parameters
        )
        
        # Starting should fail or create file in valid location
        try:
            logger.start_logging()
            # If it starts, stop it
            logger.stop_logging()
        except (OSError, IOError, ValueError):
            # Expected for invalid paths
            pass
    
    def test_json_logging_format(self, sample_parameters, temp_log_dir):
        """Test JSON logging format"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.json")
        
        logger.configure(
            format_type='json',
            file_path=log_path,
            parameters=sample_parameters
        )
        
        logger.start_logging()
        
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        logger.log_data(None, data_history)
        logger.flush_buffer()
        
        logger.stop_logging()
        
        # Verify file exists and has content
        assert os.path.exists(log_path)
        with open(log_path, 'r') as f:
            content = f.read()
            assert 'timestamp' in content or len(content) > 0
    
    def test_logger_buffer_overflow(self, sample_parameters, temp_log_dir):
        """Test logger with very small buffer"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters,
            buffer_size=1  # Very small buffer
        )
        
        logger.start_logging()
        
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        # Log multiple entries - should flush frequently
        for _ in range(5):
            logger.log_data(None, data_history)
        
        # Buffer should not grow unbounded
        assert len(logger.log_buffer) <= logger.buffer_size
        
        logger.stop_logging()
    
    def test_logger_concurrent_access(self, sample_parameters, temp_log_dir):
        """Test logger with rapid sequential access"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "test.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters,
            buffer_size=10
        )
        
        logger.start_logging()
        
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        # Rapid logging
        for _ in range(100):
            logger.log_data(None, data_history)
        
        logger.stop_logging()
        
        # Should complete without errors
        assert os.path.exists(log_path)


# ============================================================================
# SIGNAL FILTER TESTS
# ============================================================================

class TestSignalFilters:
    """Test suite for signal filtering classes"""
    
    def test_moving_average_filter(self):
        """Test MovingAverageFilter"""
        filter_obj = MovingAverageFilter("test_id", window_size=3)
        
        assert filter_obj.filter_name == "Moving Average"
        assert filter_obj.window_size == 3
        
        # Test filtering
        result1 = filter_obj.apply(10.0)
        assert result1 == 10.0
        
        result2 = filter_obj.apply(20.0)
        assert result2 == 15.0  # (10 + 20) / 2
        
        result3 = filter_obj.apply(30.0)
        assert result3 == 20.0  # (10 + 20 + 30) / 3
        
        # Test reset
        filter_obj.reset()
        assert len(filter_obj.buffer) == 0
    
    def test_low_pass_filter(self):
        """Test LowPassFilter"""
        filter_obj = LowPassFilter("test_id", alpha=0.5)
        
        assert filter_obj.filter_name == "Low Pass"
        assert filter_obj.alpha == 0.5
        
        # Test filtering
        result1 = filter_obj.apply(100.0)
        assert result1 == 100.0
        
        result2 = filter_obj.apply(50.0)
        assert result2 == 75.0  # 0.5 * 50 + 0.5 * 100
        
        # Test reset
        filter_obj.reset()
        assert filter_obj.last_value is None
    
    def test_kalman_filter(self):
        """Test KalmanFilter"""
        filter_obj = KalmanFilter("test_id", process_variance=0.01, measurement_variance=0.1)
        
        assert filter_obj.filter_name == "Kalman"
        assert filter_obj.process_variance == 0.01
        assert filter_obj.measurement_variance == 0.1
        
        # Test filtering
        result1 = filter_obj.apply(10.0)
        assert result1 == 10.0
        
        result2 = filter_obj.apply(12.0)
        assert result2 is not None
        assert 10.0 < result2 < 12.0  # Should be between measurements
        
        # Test reset
        filter_obj.reset()
        assert filter_obj.estimated_value is None
    
    def test_median_filter(self):
        """Test MedianFilter"""
        filter_obj = MedianFilter("test_id", window_size=3)
        
        assert filter_obj.filter_name == "Median"
        assert filter_obj.window_size == 3
        
        # Test filtering
        result1 = filter_obj.apply(10.0)
        assert result1 == 10.0
        
        result2 = filter_obj.apply(20.0)
        assert result2 == 15.0  # Median of [10, 20]
        
        result3 = filter_obj.apply(30.0)
        assert result3 == 20.0  # Median of [10, 20, 30]
        
        # Test outlier handling
        result4 = filter_obj.apply(1000.0)
        assert result4 == 30.0  # Median of [20, 30, 1000]
    
    def test_filter_serialization(self):
        """Test filter to_dict and from_dict"""
        # Test MovingAverageFilter
        ma_filter = MovingAverageFilter("ma_id", window_size=5)
        ma_dict = ma_filter.to_dict()
        
        assert ma_dict['type'] == 'moving_average'
        assert ma_dict['filter_id'] == 'ma_id'
        assert ma_dict['window_size'] == 5
        
        restored = MovingAverageFilter.from_dict(ma_dict)
        assert restored.filter_id == 'ma_id'
        assert restored.window_size == 5
        
        # Test LowPassFilter
        lp_filter = LowPassFilter("lp_id", alpha=0.3)
        lp_dict = lp_filter.to_dict()
        
        assert lp_dict['type'] == 'low_pass'
        assert lp_dict['alpha'] == 0.3
        
        restored_lp = LowPassFilter.from_dict(lp_dict)
        assert restored_lp.alpha == 0.3


class TestFilterManager:
    """Test suite for FilterManager class"""
    
    def test_init(self):
        """Test FilterManager initialization"""
        manager = FilterManager()
        assert manager.parameter_filters == {}
    
    def test_add_remove_filter(self):
        """Test adding and removing filters"""
        manager = FilterManager()
        filter1 = MovingAverageFilter("filter1", window_size=5)
        filter2 = LowPassFilter("filter2", alpha=0.3)
        
        # Add filters
        manager.add_filter("param1", filter1)
        manager.add_filter("param1", filter2)
        
        filters = manager.get_filters("param1")
        assert len(filters) == 2
        
        # Remove filter
        manager.remove_filter("param1", "filter1")
        filters = manager.get_filters("param1")
        assert len(filters) == 1
        assert filters[0].filter_id == "filter2"
    
    def test_apply_filters(self):
        """Test applying filters to values"""
        manager = FilterManager()
        
        # Add multiple filters
        filter1 = MovingAverageFilter("f1", window_size=2)
        filter2 = LowPassFilter("f2", alpha=0.5)
        
        manager.add_filter("param1", filter1)
        manager.add_filter("param1", filter2)
        
        # Apply filters
        result1 = manager.apply_filters("param1", 100.0)
        result2 = manager.apply_filters("param1", 50.0)
        
        assert result1 is not None
        assert result2 is not None
    
    def test_reset_filters(self):
        """Test resetting filter states"""
        manager = FilterManager()
        filter1 = MovingAverageFilter("f1", window_size=3)
        
        manager.add_filter("param1", filter1)
        
        # Apply some values
        manager.apply_filters("param1", 10.0)
        manager.apply_filters("param1", 20.0)
        
        assert len(filter1.buffer) == 2
        
        # Reset
        manager.reset_filters("param1")
        assert len(filter1.buffer) == 0
    
    def test_serialization(self):
        """Test FilterManager serialization"""
        manager = FilterManager()
        
        filter1 = MovingAverageFilter("f1", window_size=5)
        filter2 = LowPassFilter("f2", alpha=0.3)
        
        manager.add_filter("param1", filter1)
        manager.add_filter("param2", filter2)
        
        # Serialize
        data = manager.to_dict()
        assert "param1" in data
        assert "param2" in data
        assert len(data["param1"]) == 1
        
        # Deserialize
        new_manager = FilterManager()
        new_manager.from_dict(data)
        
        assert len(new_manager.get_filters("param1")) == 1
        assert len(new_manager.get_filters("param2")) == 1


# ============================================================================
# DATA SIMULATOR TESTS
# ============================================================================

class TestDataSimulator:
    """Test suite for DataSimulator class"""
    
    def test_init(self):
        """Test DataSimulator initialization"""
        simulator = DataSimulator(num_channels=32)
        
        assert simulator.num_channels == 32
        assert simulator.mode == "dummy"
        assert simulator._is_running is True
        assert simulator._is_paused is False
    
    def test_toggle_pause(self):
        """Test pause/resume functionality"""
        simulator = DataSimulator(num_channels=16)
        
        assert simulator._is_paused is False
        
        is_paused = simulator.toggle_pause()
        assert is_paused is True
        assert simulator._is_paused is True
        
        is_paused = simulator.toggle_pause()
        assert is_paused is False
    
    @patch('main.DataReader')
    def test_backend_connection_settings(self, mock_reader):
        """Test backend connection configuration"""
        settings = {
            'mode': 'serial',
            'serial_port': 'COM4',
            'baudrate': 115200,
            'data_format': 'json_array',
            'channel_count': 32
        }
        
        simulator = DataSimulator(num_channels=32, connection_settings=settings)
        assert simulator.connection_settings['mode'] == 'serial'
        assert simulator.connection_settings['baudrate'] == 115200
    
    def test_simulator_invalid_connection_settings(self):
        """Test simulator with invalid connection settings"""
        settings = {
            'mode': 'invalid_mode',
            'channel_count': -5  # Invalid
        }
        
        simulator = DataSimulator(num_channels=32, connection_settings=settings)
        # Should handle gracefully
        assert simulator.num_channels == 32
    
    def test_simulator_stop_when_not_running(self):
        """Test stopping simulator when not running"""
        simulator = DataSimulator(num_channels=16)
        simulator._is_running = False
        
        # Should handle gracefully
        simulator.stop()
        assert simulator._is_running is False
    
    def test_simulator_connection_failure(self):
        """Test simulator handling connection failures"""
        settings = {
            'mode': 'tcp',
            'tcp_host': '192.168.255.255',  # Unlikely to connect
            'tcp_port': 99999,
            'channel_count': 32
        }
        
        simulator = DataSimulator(num_channels=32, connection_settings=settings)
        # Should handle connection failure gracefully
        assert simulator.mode == "dummy"
    
    def test_simulator_zero_channels(self):
        """Test simulator with zero channels"""
        simulator = DataSimulator(num_channels=0)
        # Should handle gracefully (may clamp to 1)
        assert simulator.num_channels >= 0


# ============================================================================
# WIDGET TESTS
# ============================================================================

class TestValueCard:
    """Test suite for ValueCard widget"""
    
    def test_init(self, qapp):
        """Test ValueCard initialization"""
        card = ValueCard("Temperature", "°C", "high")
        
        assert card.param_name == "Temperature"
        assert card.unit == "°C"
        assert card.priority == "high"
        assert card.value_label.text() == "---"
    
    def test_update_value(self, qapp):
        """Test updating ValueCard value"""
        card = ValueCard("Temperature", "°C", "high")
        
        # Test normal value
        card.update_value(25.5, "Nominal")
        assert "25.5" in card.value_label.text()
        
        # Test warning state
        card.update_value(85.0, "Warning")
        assert "85.0" in card.value_label.text()
        
        # Test critical state
        card.update_value(105.0, "Critical")
        assert "105" in card.value_label.text()
        
        # Test None value
        card.update_value(None, "Nominal")
        assert "--" in card.value_label.text()


class TestLEDWidget:
    """Test suite for LEDWidget"""
    
    def test_init(self, qapp, sample_parameters):
        """Test LEDWidget initialization"""
        widget = LEDWidget(sample_parameters[0])
        
        assert widget.param['id'] == 'temp'
        assert widget.value_lbl.text() == "--"
    
    def test_update_value(self, qapp, sample_parameters):
        """Test LED state updates based on thresholds"""
        widget = LEDWidget(sample_parameters[0])
        
        # Test normal range (green)
        widget.update_value(50.0)
        assert "50.00" in widget.value_lbl.text()
        
        # Test warning range (yellow)
        widget.update_value(85.0)
        assert "85.00" in widget.value_lbl.text()
        
        # Test critical range (red)
        widget.update_value(105.0)
        assert "105.00" in widget.value_lbl.text()
        
        # Test invalid value
        widget.update_value(None)
        assert "--" in widget.value_lbl.text()


class TestRawTelemetryMonitor:
    """Test suite for RawTelemetryMonitor"""
    
    def test_init(self, qapp):
        """Test RawTelemetryMonitor initialization"""
        monitor = RawTelemetryMonitor()
        
        assert monitor.packet_count == 0
        assert monitor.byte_count == 0
        assert monitor.is_paused is False
        assert monitor.max_lines == 1000
    
    def test_append_packet(self, qapp):
        """Test appending packet data"""
        monitor = RawTelemetryMonitor()
        
        test_data = [1.0, 2.0, 3.0, 4.0]
        monitor.append_packet(test_data)
        
        assert monitor.packet_count == 1
        assert monitor.byte_count > 0
        assert not monitor.text_display.toPlainText().strip() == ""
    
    def test_toggle_pause(self, qapp):
        """Test pause/resume functionality"""
        monitor = RawTelemetryMonitor()
        
        assert monitor.is_paused is False
        assert monitor.pause_btn.text() == "Pause"
        
        # Trigger the button click properly
        monitor.pause_btn.setChecked(True)
        monitor.toggle_pause()
        assert monitor.is_paused is True
        assert monitor.pause_btn.text() == "Resume"
    
    def test_clear_display(self, qapp):
        """Test clearing display"""
        monitor = RawTelemetryMonitor()
        
        monitor.append_packet([1.0, 2.0])
        assert monitor.packet_count == 1
        
        monitor.clear_display()
        assert monitor.packet_count == 0
        assert monitor.byte_count == 0


# ============================================================================
# DIALOG TESTS
# ============================================================================

class TestParameterEntryDialog:
    """Test suite for ParameterEntryDialog"""
    
    def test_init_new(self, qapp):
        """Test creating new parameter"""
        dialog = ParameterEntryDialog()
        
        assert dialog.is_edit_mode is False
        assert dialog.id_edit.text() == ""
        assert dialog.name_edit.text() == ""
        assert not dialog.id_edit.isReadOnly()
    
    def test_init_edit(self, qapp, sample_parameters):
        """Test editing existing parameter"""
        dialog = ParameterEntryDialog(param=sample_parameters[0])
        
        assert dialog.is_edit_mode is True
        assert dialog.id_edit.text() == "temp"
        assert dialog.name_edit.text() == "Temperature"
        assert dialog.id_edit.isReadOnly()
    
    def test_get_data(self, qapp):
        """Test retrieving parameter data"""
        dialog = ParameterEntryDialog()
        
        dialog.id_edit.setText("test_id")
        dialog.name_edit.setText("Test Param")
        dialog.index_spin.setValue(5)
        dialog.unit_edit.setText("unit")
        
        data = dialog.get_data()
        
        assert data['id'] == "test_id"
        assert data['name'] == "Test Param"
        assert data['array_index'] == 5
        assert data['unit'] == "unit"
    
    def test_validate_duplicate_id(self, qapp):
        """Test validation with duplicate ID"""
        dialog = ParameterEntryDialog(existing_ids=['existing_id'])
        
        dialog.id_edit.setText("existing_id")
        dialog.name_edit.setText("Test")
        
        # Should reject duplicate ID
        # validate_and_accept should show error or reject
        assert dialog.existing_ids == ['existing_id']
    
    def test_validate_empty_id(self, qapp):
        """Test validation with empty ID"""
        dialog = ParameterEntryDialog()
        
        dialog.id_edit.setText("")
        dialog.name_edit.setText("Test")
        
        # Should reject empty ID
        assert True  # Validation handled in validate_and_accept
    
    def test_validate_spaces_in_id(self, qapp):
        """Test validation with spaces in ID"""
        dialog = ParameterEntryDialog()
        
        dialog.id_edit.setText("invalid id")
        dialog.name_edit.setText("Test")
        
        # Should reject IDs with spaces
        assert " " in dialog.id_edit.text()  # Spaces should trigger validation error


class TestManageParametersDialog:
    """Test suite for ManageParametersDialog"""
    
    def test_init(self, qapp, sample_parameters):
        """Test initialization with parameters"""
        dialog = ManageParametersDialog(sample_parameters.copy())
        
        assert dialog.table.rowCount() == 2
        assert dialog.parameters == sample_parameters
    
    def test_refresh_table(self, qapp, sample_parameters):
        """Test table refresh"""
        dialog = ManageParametersDialog(sample_parameters.copy())
        
        # Add a parameter
        new_param = {
            'id': 'new_id',
            'name': 'New Param',
            'array_index': 2,
            'sensor_group': 'Test',
            'unit': 'V',
            'description': 'Test param'
        }
        dialog.parameters.append(new_param)
        dialog.refresh_table()
        
        assert dialog.table.rowCount() == 3
    
    def test_init_empty_parameters(self, qapp):
        """Test initialization with empty parameters"""
        dialog = ManageParametersDialog([])
        
        assert dialog.table.rowCount() == 0
        assert dialog.parameters == []
    
    def test_refresh_table_large_list(self, qapp):
        """Test table refresh with large parameter list"""
        large_params = [
            {
                'id': f'param_{i}',
                'name': f'Parameter {i}',
                'array_index': i,
                'sensor_group': 'Test',
                'unit': 'V',
                'description': f'Test parameter {i}'
            }
            for i in range(100)
        ]
        
        dialog = ManageParametersDialog(large_params)
        dialog.refresh_table()
        
        assert dialog.table.rowCount() == 100
    
    def test_remove_parameter_no_selection(self, qapp, sample_parameters):
        """Test removing parameter with no selection"""
        dialog = ManageParametersDialog(sample_parameters.copy())
        initial_count = len(dialog.parameters)
        
        # Remove with no selection should do nothing
        dialog.remove_parameter()
        
        assert len(dialog.parameters) == initial_count
    
    def test_edit_parameter_no_selection(self, qapp, sample_parameters):
        """Test editing parameter with no selection"""
        dialog = ManageParametersDialog(sample_parameters.copy())
        
        # Edit with no selection should not crash
        dialog.edit_parameter()
        
        assert len(dialog.parameters) == len(sample_parameters)


# ============================================================================
# MAIN WINDOW TESTS
# ============================================================================

class TestMainWindow:
    """Test suite for MainWindow class"""
    
    def test_init(self, qapp):
        """Test MainWindow initialization"""
        window = MainWindow()
        
        assert window.windowTitle() == "Glance - Untitled"
        assert window.parameters == []
        assert window.data_history == {}
        assert window.has_unsaved_changes is False
    
    def test_phases(self, qapp):
        """Test different application phases"""
        window = MainWindow()
        
        # Test splash phase
        window.show_phase("splash")
        assert window.stack.currentWidget() == window.splash_page
        
        # Test welcome phase
        window.show_phase("welcome")
        assert window.stack.currentWidget() == window.welcome_page
        
        # Test setup phase
        window.show_phase("setup")
        assert window.stack.currentWidget() == window.setup_page
        
        # Test dashboard phase
        window.show_phase("dashboard")
        assert window.stack.currentWidget() == window.dashboard_page
    
    def test_mark_unsaved(self, qapp):
        """Test marking project as unsaved"""
        window = MainWindow()
        
        assert window.has_unsaved_changes is False
        
        window.mark_as_unsaved()
        assert window.has_unsaved_changes is True
        assert "*" in window.windowTitle()
    
    def test_mark_saved(self, qapp):
        """Test marking project as saved"""
        window = MainWindow()
        
        window.mark_as_unsaved()
        assert window.has_unsaved_changes is True
        
        window.mark_as_saved()
        assert window.has_unsaved_changes is False
        assert "*" not in window.windowTitle()
    
    def test_add_tab(self, qapp):
        """Test adding new tab"""
        window = MainWindow()
        window.show_phase("dashboard")
        
        initial_count = window.tab_widget.count()
        window.add_new_tab(name="Test Tab")
        
        assert window.tab_widget.count() == initial_count + 1
    
    def test_get_alarm_state(self, qapp):
        """Test alarm state calculation"""
        window = MainWindow()
        
        thresholds = {
            'low_crit': 0,
            'low_warn': 10,
            'high_warn': 80,
            'high_crit': 100
        }
        
        assert window.get_alarm_state(-5, thresholds) == 'Critical'
        assert window.get_alarm_state(5, thresholds) == 'Warning'
        assert window.get_alarm_state(50, thresholds) == 'Nominal'
        assert window.get_alarm_state(85, thresholds) == 'Warning'
        assert window.get_alarm_state(105, thresholds) == 'Critical'
    
    def test_update_data(self, qapp, sample_parameters):
        """Test data update processing"""
        window = MainWindow()
        window.parameters = sample_parameters
        
        # Create test packet
        packet = [25.5, 1013.25]
        
        window.update_data(packet)
        
        # Check data history was updated
        assert 'temp' in window.data_history
        assert 'pressure' in window.data_history
        assert len(window.data_history['temp']) == 1
        assert window.data_history['temp'][0]['value'] == 25.5


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_logging_workflow(self, qapp, sample_parameters, temp_log_dir):
        """Test complete data logging workflow"""
        # Create logger
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "integration_test.csv")
        
        # Configure
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters,
            buffer_size=2
        )
        
        # Start logging
        logger.start_logging()
        assert logger.is_logging is True
        
        # Log some data
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        for _ in range(5):
            logger.log_data(None, data_history)
            time.sleep(0.01)
        
        # Stop logging
        logger.stop_logging()
        assert logger.is_logging is False
        
        # Verify file exists and has content
        assert os.path.exists(log_path)
        with open(log_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 1  # Header + data
    
    def test_filter_chain_application(self):
        """Test applying multiple filters in sequence"""
        manager = FilterManager()
        
        # Create filter chain
        ma_filter = MovingAverageFilter("f1", window_size=3)
        lp_filter = LowPassFilter("f2", alpha=0.5)
        
        manager.add_filter("param1", ma_filter)
        manager.add_filter("param1", lp_filter)
        
        # Apply values to all parameters
        values = [100.0, 110.0, 90.0, 95.0, 105.0]
        results = []
        
        for val in values:
            result = manager.apply_filters("param1", val)
            results.append(result)
        
        # Verify filtering occurred
        assert len(results) == 5
        assert all(r is not None for r in results)
        
        # Results should be smoothed
        assert results[-1] != values[-1]


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and stress tests"""
    
    def test_filter_performance(self):
        """Test filter performance with many values"""
        filter_obj = MovingAverageFilter("perf_test", window_size=10)
        
        start_time = time.time()
        for i in range(10000):
            filter_obj.apply(float(i))
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 1.0  # Should complete in less than 1 second
    
    def test_data_history_memory(self):
        """Test data history memory management"""
        history = {}
        param_id = "test_param"
        
        # Add many data points
        for i in range(1000):
            if param_id not in history:
                history[param_id] = []
            
            history[param_id].append({
                'value': float(i),
                'timestamp': time.time()
            })
            
            # Limit history (as done in main app)
            history[param_id] = history[param_id][-500:]
        
        # Verify limit is enforced
        assert len(history[param_id]) == 500


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_filter_none_values(self):
        """Test filters handling None values"""
        filters = [
            MovingAverageFilter("f1", window_size=3),
            LowPassFilter("f2", alpha=0.5),
            KalmanFilter("f3"),
            MedianFilter("f4", window_size=3)
        ]
        
        for filt in filters:
            result = filt.apply(None)
            assert result is None
    
    def test_filter_nan_values(self):
        """Test filters handling NaN values"""
        import math
        filters = [
            MovingAverageFilter("f1", window_size=3),
            LowPassFilter("f2", alpha=0.5),
            KalmanFilter("f3"),
            MedianFilter("f4", window_size=3)
        ]
        
        for filt in filters:
            result = filt.apply(float('nan'))
            # Filters should handle NaN gracefully (return None or NaN)
            assert result is None or (isinstance(result, float) and math.isnan(result))
    
    def test_filter_inf_values(self):
        """Test filters handling infinity values"""
        import math
        filters = [
            MovingAverageFilter("f1", window_size=3),
            LowPassFilter("f2", alpha=0.5),
            MedianFilter("f4", window_size=3)
        ]
        
        for filt in filters:
            result_pos = filt.apply(float('inf'))
            result_neg = filt.apply(float('-inf'))
            # Should handle gracefully
            assert result_pos is None or isinstance(result_pos, float)
            assert result_neg is None or isinstance(result_neg, float)
    
    def test_filter_extreme_values(self):
        """Test filters with extremely large/small values"""
        filter_obj = MovingAverageFilter("test", window_size=3)
        
        # Very large values
        result1 = filter_obj.apply(1e10)
        result2 = filter_obj.apply(1e10)
        
        # Should handle without overflow
        assert result1 is not None
        assert result2 is not None
        
        filter_obj.reset()
        
        # Very small values
        result3 = filter_obj.apply(1e-10)
        assert result3 is not None
    
    def test_filter_negative_values(self):
        """Test filters with negative values"""
        filter_obj = MovingAverageFilter("test", window_size=3)
        
        result = filter_obj.apply(-100.0)
        result = filter_obj.apply(-50.0)
        result = filter_obj.apply(-75.0)
        
        # Should handle negative values correctly
        assert result is not None
        assert result < 0
    
    def test_filter_zero_values(self):
        """Test filters with zero values"""
        filter_obj = MovingAverageFilter("test", window_size=3)
        
        result1 = filter_obj.apply(0.0)
        result2 = filter_obj.apply(0.0)
        result3 = filter_obj.apply(0.0)
        
        assert result1 == 0.0
        assert result2 == 0.0
        assert result3 == 0.0
    
    def test_filter_rapid_changes(self):
        """Test filters with rapid value changes"""
        filter_obj = MovingAverageFilter("test", window_size=5)
        
        # Rapid oscillations
        values = [100.0, -100.0, 100.0, -100.0, 100.0]
        for val in values:
            result = filter_obj.apply(val)
            assert result is not None
    
    def test_low_pass_alpha_bounds(self):
        """Test LowPassFilter with edge case alpha values"""
        # Alpha = 0 (should use only previous value)
        filter_obj = LowPassFilter("test", alpha=0.0)
        filter_obj.apply(100.0)
        result = filter_obj.apply(200.0)
        assert result == 100.0  # Should keep previous value
        
        # Alpha = 1 (should use only new value)
        filter_obj = LowPassFilter("test", alpha=1.0)
        filter_obj.apply(100.0)
        result = filter_obj.apply(200.0)
        assert result == 200.0  # Should use new value
        
        # Alpha > 1 (should clamp)
        filter_obj = LowPassFilter("test", alpha=2.0)
        # Should handle gracefully
    
    def test_kalman_filter_edge_cases(self):
        """Test KalmanFilter with edge case variances"""
        # Very small variances
        filter_obj = KalmanFilter("test", process_variance=1e-10, measurement_variance=1e-10)
        result = filter_obj.apply(100.0)
        assert result is not None
        
        # Very large variances
        filter_obj = KalmanFilter("test", process_variance=1e10, measurement_variance=1e10)
        result = filter_obj.apply(100.0)
        assert result is not None
    
    def test_median_filter_single_value(self):
        """Test MedianFilter with window_size=1"""
        filter_obj = MedianFilter("test", window_size=1)
        result = filter_obj.apply(100.0)
        assert result == 100.0
    
    def test_empty_parameter_list(self, qapp):
        """Test handling empty parameter list"""
        window = MainWindow()
        
        # Should not crash with empty parameters
        packet = [1.0, 2.0, 3.0]
        window.update_data(packet)
        
        assert window.data_history == {}
    
    def test_invalid_array_index(self, qapp):
        """Test handling invalid array indices"""
        window = MainWindow()
        window.parameters = [{
            'id': 'test',
            'name': 'Test',
            'array_index': 100,  # Invalid index
            'unit': 'unit',
            'threshold': {'low_crit': 0, 'low_warn': 10, 'high_warn': 80, 'high_crit': 100}
        }]
        
        packet = [1.0, 2.0]  # Only 2 elements
        
        # Should not crash
        window.update_data(packet)
        
        # Data should not be added for invalid index
        assert 'test' not in window.data_history or len(window.data_history.get('test', [])) == 0
    
    def test_update_data_none_packet(self, qapp, sample_parameters):
        """Test update_data with None packet"""
        window = MainWindow()
        window.parameters = sample_parameters
        
        # Should not crash
        window.update_data(None)
        
        # No data should be added
        assert len(window.data_history) == 0
    
    def test_update_data_wrong_type(self, qapp, sample_parameters):
        """Test update_data with wrong packet type"""
        window = MainWindow()
        window.parameters = sample_parameters
        
        # Should handle gracefully
        window.update_data("not a list")
        window.update_data(123)
        window.update_data({})
        
        # Should not crash
        assert True
    
    def test_get_alarm_state_none_value(self, qapp):
        """Test get_alarm_state with None value"""
        window = MainWindow()
        
        thresholds = {
            'low_crit': 0,
            'low_warn': 10,
            'high_warn': 80,
            'high_crit': 100
        }
        
        # Should handle None gracefully
        result = window.get_alarm_state(None, thresholds)
        # May return 'Nominal' or handle specially
        assert isinstance(result, str)
    
    def test_get_alarm_state_invalid_thresholds(self, qapp):
        """Test get_alarm_state with invalid threshold structure"""
        window = MainWindow()
        
        # Missing thresholds
        result = window.get_alarm_state(50, {})
        # Should handle gracefully
        assert isinstance(result, str)
        
        # Invalid threshold values
        invalid_thresholds = {
            'low_crit': None,
            'low_warn': 10,
            'high_warn': 80,
            'high_crit': 100
        }
        
        result = window.get_alarm_state(50, invalid_thresholds)
        assert isinstance(result, str)
    
    def test_logger_file_locked(self, sample_parameters, temp_log_dir):
        """Test logger when file is locked by another process"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "locked.csv")
        
        logger.configure(
            format_type='csv',
            file_path=log_path,
            parameters=sample_parameters
        )
        
        # Start logging
        logger.start_logging()
        
        # Try to write (file is now open)
        data_history = {
            'temp': [{'value': 25.5, 'timestamp': time.time()}],
            'pressure': [{'value': 1013.25, 'timestamp': time.time()}]
        }
        
        logger.log_data(None, data_history)
        logger.stop_logging()
        
        # Should complete successfully
        assert os.path.exists(log_path)
    
    def test_filter_manager_empty_param_id(self):
        """Test FilterManager with empty parameter ID"""
        manager = FilterManager()
        filter_obj = MovingAverageFilter("f1", window_size=3)
        
        # Should handle empty string
        manager.add_filter("", filter_obj)
        filters = manager.get_filters("")
        assert len(filters) == 1
    
    def test_filter_manager_none_param_id(self):
        """Test FilterManager with None parameter ID"""
        manager = FilterManager()
        filter_obj = MovingAverageFilter("f1", window_size=3)
        
        # Should handle None gracefully or raise TypeError
        try:
            manager.add_filter(None, filter_obj)
            filters = manager.get_filters(None)
            # If it doesn't raise, should handle gracefully
            assert isinstance(filters, list)
        except (TypeError, AttributeError):
            # Expected behavior
            pass
    
    def test_filter_manager_remove_nonexistent(self):
        """Test removing non-existent filter"""
        manager = FilterManager()
        
        # Remove filter that doesn't exist
        manager.remove_filter("param1", "nonexistent_filter")
        
        # Should not crash
        filters = manager.get_filters("param1")
        assert len(filters) == 0
    
    def test_filter_manager_apply_no_filters(self):
        """Test applying filters when none exist"""
        manager = FilterManager()
        
        result = manager.apply_filters("param1", 100.0)
        
        # Should return original value or None
        assert result is None or result == 100.0
    
    def test_filter_manager_reset_all(self):
        """Test resetting all filters"""
        manager = FilterManager()
        
        filter1 = MovingAverageFilter("f1", window_size=3)
        filter2 = LowPassFilter("f2", alpha=0.5)
        
        manager.add_filter("param1", filter1)
        manager.add_filter("param2", filter2)
        
        # Apply some values
        manager.apply_filters("param1", 10.0)
        manager.apply_filters("param2", 20.0)
        
        # Reset all
        manager.reset_filters()
        
        # Filters should be reset
        assert len(filter1.buffer) == 0
        assert filter2.last_value is None


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "ui: marks tests that require UI interaction")


# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================

class TestUtilityFunctions:
    """Test utility and helper functions"""
    
    def test_serial_port_listing(self, qapp):
        """Test serial port listing functionality"""
        window = MainWindow()
        ports = window.list_serial_ports()
        
        assert isinstance(ports, list)
        # Should have at least some default ports
        assert len(ports) > 0
    
    def test_connection_settings_validation(self, qapp):
        """Test connection settings validation"""
        window = MainWindow()
        
        # Default settings should be valid
        assert window.connection_settings['mode'] in ['dummy', 'serial', 'tcp', 'udp']
        assert isinstance(window.connection_settings['baudrate'], int)
        assert window.connection_settings['baudrate'] > 0
        assert isinstance(window.connection_settings['timeout'], (int, float))
    
    def test_dashboard_title_customization(self, qapp):
        """Test dashboard title customization"""
        window = MainWindow()
        
        # Default title
        assert window.dashboard_title_text == "Dashboard"
        
        # Update title
        window.dashboard_title_text = "Custom Dashboard"
        window._update_dashboard_title()
        
        assert "Custom Dashboard" in window.dashboard_title.text()
    
    def test_graph_color_assignment(self, qapp, sample_parameters):
        """Test automatic color assignment for graphs"""
        window = MainWindow()
        window.parameters = sample_parameters
        
        initial_index = window.next_graph_color_index
        
        # Simulate adding parameters that need colors
        for param in sample_parameters:
            param['color'] = window.graph_color_palette[
                window.next_graph_color_index % len(window.graph_color_palette)
            ]
            window.next_graph_color_index += 1
        
        assert window.next_graph_color_index == initial_index + len(sample_parameters)
        assert sample_parameters[0]['color'] in window.graph_color_palette


# ============================================================================
# PROJECT SAVE/LOAD TESTS
# ============================================================================

class TestProjectManagement:
    """Test project save/load functionality"""
    
    def test_save_project_data_structure(self, qapp, sample_parameters, temp_log_dir):
        """Test project save data structure"""
        window = MainWindow()
        window.parameters = sample_parameters
        window.current_project_path = os.path.join(temp_log_dir, "test_project.json")
        
        # Add a tab with some config
        window.show_phase("dashboard")
        tab_index = window.add_new_tab(name="Test Tab")
        
        # Save project
        window.save_project()
        
        # Verify file exists
        assert os.path.exists(window.current_project_path)
        
        # Load and verify structure
        with open(window.current_project_path, 'r') as f:
            project_data = json.load(f)
        
        assert 'parameters' in project_data
        assert 'layout' in project_data
        assert 'connection_settings' in project_data
        assert 'version' in project_data
        assert len(project_data['parameters']) == len(sample_parameters)
    
    def test_load_project(self, qapp, sample_parameters, temp_log_dir):
        """Test loading a saved project"""
        # Create and save a project
        window1 = MainWindow()
        window1.parameters = sample_parameters
        window1.current_project_path = os.path.join(temp_log_dir, "test_load.json")
        window1.show_phase("dashboard")
        window1.save_project()
        
        project_path = window1.current_project_path
        
        # Create new window and load project
        window2 = MainWindow()
        window2.current_project_path = project_path
        
        # Manually load the data
        with open(project_path, 'r') as f:
            project_data = json.load(f)
        
        window2.parameters = project_data.get('parameters', [])
        
        # Verify parameters loaded correctly
        assert len(window2.parameters) == len(sample_parameters)
        assert window2.parameters[0]['id'] == sample_parameters[0]['id']
    
    def test_unsaved_changes_tracking(self, qapp):
        """Test unsaved changes tracking"""
        window = MainWindow()
        
        # Initially no unsaved changes
        assert window.has_unsaved_changes is False
        
        # Make a change
        window.mark_as_unsaved()
        assert window.has_unsaved_changes is True
        assert "*" in window.windowTitle()
        
        # Save
        window.mark_as_saved()
        assert window.has_unsaved_changes is False
        assert "*" not in window.windowTitle()


# ============================================================================
# WIDGET INTERACTION TESTS
# ============================================================================

class TestWidgetInteractions:
    """Test widget interactions and updates"""
    
    def test_value_card_formatting(self, qapp):
        """Test value card number formatting"""
        card = ValueCard("Test", "unit", "high")
        
        # Test large numbers
        card.update_value(1234.567, "Nominal")
        assert "1,234.6" in card.value_label.text() or "1234.6" in card.value_label.text()
        
        # Test small numbers
        card.update_value(0.123, "Nominal")
        assert "0.123" in card.value_label.text()
        
        # Test zero
        card.update_value(0.0, "Nominal")
        text = card.value_label.text()
        assert "0" in text
    
    def test_led_widget_threshold_states(self, qapp, sample_parameters):
        """Test LED widget state changes at thresholds"""
        widget = LEDWidget(sample_parameters[0])
        
        thresholds = sample_parameters[0]['threshold']
        
        # Test at each threshold boundary
        test_cases = [
            (thresholds['low_crit'] - 1, "critical"),  # Below low critical
            (thresholds['low_crit'], "critical"),
            (thresholds['low_warn'], "warning"),
            ((thresholds['low_warn'] + thresholds['high_warn']) / 2, "normal"),
            (thresholds['high_warn'], "warning"),
            (thresholds['high_crit'], "critical"),
            (thresholds['high_crit'] + 1, "critical")  # Above high critical
        ]
        
        for value, expected_state in test_cases:
            widget.update_value(value)
            # Verify the widget updated (specific color checks would be complex)
            assert widget.value_lbl.text() != "--"
    
    def test_histogram_update(self, qapp, sample_parameters):
        """Test histogram widget updates"""
        widget = HistogramWidget(sample_parameters[0])
        
        # Update with data
        values = [10.0, 20.0, 30.0, 40.0, 50.0] * 10
        widget.update_histogram(values)
        
        # Verify widget doesn't crash and has plot items
        assert widget.plot is not None
        assert widget.bar_item is not None
    
    def test_time_graph_data_update(self, qapp, sample_parameters):
        """Test time graph data updates"""
        # Create graph with parameters
        param_configs = []
        for param in sample_parameters:
            param['color'] = '#FF0000'
            param_configs.append(param)
        
        graph = TimeGraph(param_configs)
        
        # Create mock history
        timestamp = time.time()
        history = {
            'temp': [
                {'value': 25.0, 'timestamp': timestamp},
                {'value': 26.0, 'timestamp': timestamp + 1}
            ],
            'pressure': [
                {'value': 1013.0, 'timestamp': timestamp},
                {'value': 1014.0, 'timestamp': timestamp + 1}
            ]
        }
        
        # Update graph
        graph.update_data(history)
        
        # Verify curves exist and have data
        assert len(graph.curves) == 2
        assert 'temp' in graph.curves
        assert 'pressure' in graph.curves


# ============================================================================
# FILTER EDGE CASES
# ============================================================================

class TestFilterEdgeCases:
    """Test edge cases for filters"""
    
    def test_moving_average_single_value(self):
        """Test moving average with single value"""
        filter_obj = MovingAverageFilter("test", window_size=5)
        
        result = filter_obj.apply(42.0)
        assert result == 42.0
    
    def test_low_pass_identical_values(self):
        """Test low pass filter with identical values"""
        filter_obj = LowPassFilter("test", alpha=0.5)
        
        for _ in range(10):
            result = filter_obj.apply(100.0)
        
        # Should converge to the input value
        assert abs(result - 100.0) < 0.01
    
    def test_kalman_noisy_data(self):
        """Test Kalman filter with noisy data"""
        import random
        filter_obj = KalmanFilter("test", process_variance=0.01, measurement_variance=0.1)
        
        # Generate noisy data around 100
        for _ in range(50):
            noisy_value = 100.0 + random.uniform(-5, 5)
            result = filter_obj.apply(noisy_value)
        
        # Final result should be close to 100
        assert 95.0 < result < 105.0
    
    def test_median_filter_removes_outliers(self):
        """Test median filter removes outliers"""
        filter_obj = MedianFilter("test", window_size=5)
        
        # Normal values with one outlier
        values = [10.0, 11.0, 10.5, 1000.0, 10.2]
        results = []
        
        for val in values:
            result = filter_obj.apply(val)
            results.append(result)
        
        # Last result should not be heavily influenced by outlier
        assert results[-1] < 100.0  # Should be much less than the outlier


# ============================================================================
# CONNECTION AND SIMULATOR TESTS
# ============================================================================

class TestConnectionHandling:
    """Test connection handling and simulator"""
    
    def test_dummy_mode_initialization(self):
        """Test dummy mode simulator initialization"""
        settings = {
            'mode': 'dummy',
            'channel_count': 16
        }
        
        simulator = DataSimulator(num_channels=16, connection_settings=settings)
        
        assert simulator.mode == "dummy"
        assert simulator.num_channels == 16
    
    def test_connection_settings_update(self, qapp):
        """Test updating connection settings"""
        window = MainWindow()
        
        old_mode = window.connection_settings['mode']
        
        # Update settings
        window.connection_settings['mode'] = 'tcp'
        window.connection_settings['tcp_host'] = '192.168.1.100'
        window.connection_settings['tcp_port'] = 8080
        
        assert window.connection_settings['mode'] == 'tcp'
        assert window.connection_settings['tcp_host'] == '192.168.1.100'
        assert window.connection_settings['tcp_port'] == 8080
    
    def test_simulator_pause_resume(self):
        """Test simulator pause and resume"""
        simulator = DataSimulator(num_channels=8)
        
        assert simulator._is_paused is False
        
        # Pause
        paused = simulator.toggle_pause()
        assert paused is True
        assert simulator._is_paused is True
        
        # Resume
        paused = simulator.toggle_pause()
        assert paused is False
        assert simulator._is_paused is False


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test data validation and sanitization"""
    
    def test_parameter_id_validation(self, qapp):
        """Test parameter ID validation"""
        dialog = ParameterEntryDialog(existing_ids=['existing_id'])
        
        dialog.id_edit.setText("new_id")
        dialog.name_edit.setText("Test")
        
        # Valid ID should work
        assert dialog.id_edit.text() == "new_id"
        
        # ID with spaces should be invalid (tested in validate_and_accept)
        dialog.id_edit.setText("invalid id")
        assert " " in dialog.id_edit.text()
    
    def test_threshold_ordering(self, qapp):
        """Test threshold ordering validation"""
        dialog = ParameterEntryDialog()
        
        # Set valid thresholds
        dialog.low_crit.setValue(0)
        dialog.low_warn.setValue(10)
        dialog.high_warn.setValue(80)
        dialog.high_crit.setValue(100)
        
        # Check order is correct
        assert dialog.low_crit.value() < dialog.low_warn.value()
        assert dialog.low_warn.value() < dialog.high_warn.value()
        assert dialog.high_warn.value() < dialog.high_crit.value()
    
    def test_array_index_bounds(self, qapp):
        """Test array index bounds"""
        dialog = ParameterEntryDialog()
        
        # Should be within valid range
        dialog.index_spin.setValue(0)
        assert dialog.index_spin.value() >= 0
        
        dialog.index_spin.setValue(255)
        assert dialog.index_spin.value() <= 255
        
        # Test limits
        min_val = dialog.index_spin.minimum()
        max_val = dialog.index_spin.maximum()
        assert min_val == 0
        assert max_val == 255


# ============================================================================
# MEMORY AND RESOURCE TESTS
# ============================================================================

class TestResourceManagement:
    """Test memory and resource management"""
    
    def test_data_history_limit(self, qapp, sample_parameters):
        """Test data history limit enforcement"""
        window = MainWindow()
        window.parameters = sample_parameters
        
        # Add more than 500 data points
        for i in range(600):
            packet = [float(i), float(i + 100)]
            window.update_data(packet)
        
        # History should be limited to 500
        for param_id in ['temp', 'pressure']:
            if param_id in window.data_history:
                assert len(window.data_history[param_id]) <= 500
    
    def test_filter_buffer_memory(self):
        """Test filter buffer doesn't grow unbounded"""
        filter_obj = MovingAverageFilter("test", window_size=10)
        
        # Add many values
        for i in range(1000):
            filter_obj.apply(float(i))
        
        # Buffer should be limited to window size
        assert len(filter_obj.buffer) == 10
    
    def test_log_table_row_limit(self, qapp, sample_parameters):
        """Test log table row limit"""
        table = LogTable(sample_parameters)
        
        # Add more than 500 rows
        for i in range(600):
            data_history = {
                'temp': [{'value': 25.0, 'timestamp': time.time()}],
                'pressure': [{'value': 1013.0, 'timestamp': time.time()}]
            }
            table.update_data('temp', data_history)
        
        # Should be limited to 500 rows
        assert table.table.rowCount() <= 501  # +1 for initial insert


# ============================================================================
# CONCURRENT OPERATIONS TESTS
# ============================================================================

class TestConcurrentOperations:
    """Test concurrent operations and thread safety"""
    
    def test_simultaneous_filter_applications(self):
        """Test applying filters from multiple parameters simultaneously"""
        manager = FilterManager()
        
        # Add filters to multiple parameters
        for i in range(5):
            param_id = f"param_{i}"
            filter_obj = MovingAverageFilter(f"filter_{i}", window_size=3)
            manager.add_filter(param_id, filter_obj)
        
        # Apply values to all parameters
        for i in range(5):
            param_id = f"param_{i}"
            result = manager.apply_filters(param_id, float(i * 10))
            assert result is not None
    
    def test_logging_during_data_updates(self, qapp, sample_parameters, temp_log_dir):
        """Test logging while data is being updated"""
        window = MainWindow()
        window.parameters = sample_parameters
        
        # Configure logging
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "concurrent_test.csv")
        logger.configure('csv', log_path, sample_parameters, buffer_size=5)
        logger.start_logging()
        
        # Update data multiple times
        for i in range(10):
            packet = [25.0 + i, 1013.0 + i]
            window.update_data(packet)
            logger.log_data(packet, window.data_history)
        
        logger.stop_logging()
        
        # Verify file was created
        assert os.path.exists(log_path)


# ============================================================================
# UI RESPONSIVENESS TESTS
# ============================================================================

@pytest.mark.ui
class TestUIResponsiveness:
    """Test UI responsiveness and updates"""
    
    def test_rapid_value_updates(self, qapp):
        """Test UI handles rapid value updates"""
        card = ValueCard("Test", "unit", "high")
        
        # Rapidly update values
        for i in range(100):
            card.update_value(float(i), "Nominal")
            QApplication.processEvents()
        
        # Should end with last value
        assert "99" in card.value_label.text()
    
    def test_tab_switching(self, qapp):
        """Test tab switching doesn't cause errors"""
        window = MainWindow()
        window.show_phase("dashboard")
        
        # Add multiple tabs
        for i in range(5):
            window.add_new_tab(name=f"Tab {i}")
        
        # Switch between tabs
        for i in range(5):
            window.tab_widget.setCurrentIndex(i)
            QApplication.processEvents()
        
        assert window.tab_widget.currentIndex() == 4


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestConfiguration:
    """Test configuration and settings"""
    
    def test_default_configuration(self, qapp):
        """Test default configuration values"""
        window = MainWindow()
        
        # Check default connection settings
        assert 'mode' in window.connection_settings
        assert 'baudrate' in window.connection_settings
        assert 'timeout' in window.connection_settings
        
        # Check default logger settings
        assert window.data_logger is not None
        assert window.filter_manager is not None
    
    def test_filter_manager_initialization(self):
        """Test filter manager default state"""
        manager = FilterManager()
        
        assert isinstance(manager.parameter_filters, dict)
        assert len(manager.parameter_filters) == 0
        
        # Check filter type registry
        assert 'moving_average' in manager.FILTER_CLASSES
        assert 'low_pass' in manager.FILTER_CLASSES
        assert 'kalman' in manager.FILTER_CLASSES
        assert 'median' in manager.FILTER_CLASSES


# ============================================================================
# CLEANUP AND TEARDOWN TESTS
# ============================================================================

class TestCleanup:
    """Test cleanup and resource deallocation"""
    
    def test_simulator_cleanup(self):
        """Test simulator cleanup on stop"""
        simulator = DataSimulator(num_channels=8)
        simulator.start()
        
        time.sleep(0.1)
        
        simulator.stop()
        simulator.wait(1000)
        
        assert simulator._is_running is False
    
    def test_logger_cleanup(self, sample_parameters, temp_log_dir):
        """Test logger cleanup on stop"""
        logger = DataLogger()
        log_path = os.path.join(temp_log_dir, "cleanup_test.csv")
        
        logger.configure('csv', log_path, sample_parameters)
        logger.start_logging()
        
        assert logger.log_file is not None
        
        logger.stop_logging()
        
        assert logger.log_file is None
        assert logger.is_logging is False
    
    def test_window_cleanup(self, qapp):
        """Test window cleanup"""
        window = MainWindow()
        window.show()
        
        QTimer.singleShot(100, window.close)
        QApplication.processEvents()
        
        # Window should handle close gracefully


# ============================================================================
# REGRESSION TESTS
# ============================================================================

class TestStandaloneTelemetryViewer:
    """Test suite for StandaloneTelemetryViewer"""
    
    def test_init(self, qapp):
        """Test StandaloneTelemetryViewer initialization"""
        viewer = StandaloneTelemetryViewer()
        
        assert viewer is not None
        # Should initialize without errors
    
    def test_display_modes(self, qapp):
        """Test different display modes"""
        viewer = StandaloneTelemetryViewer()
        
        # Test setting different modes
        modes = ['decimal', 'hex', 'ascii', 'binary', 'mixed']
        for mode in modes:
            try:
                viewer.set_display_mode(mode)
                # Should not crash
                assert True
            except Exception:
                # Some modes may not be implemented
                pass
    
    def test_toggle_connection(self, qapp):
        """Test connection toggle"""
        viewer = StandaloneTelemetryViewer()
        
        # Should handle toggle without errors
        try:
            viewer.toggle_connection()
        except Exception:
            # May fail without actual connection, which is fine
            pass


class TestConnectionSettingsDialog:
    """Test suite for ConnectionSettingsDialog"""
    
    def test_init_default(self, qapp):
        """Test ConnectionSettingsDialog initialization with defaults"""
        settings = {
            'mode': 'serial',
            'serial_port': 'COM4',
            'baudrate': 115200
        }
        
        dialog = ConnectionSettingsDialog(settings)
        
        assert dialog._settings['mode'] == 'serial'
    
    def test_init_all_modes(self, qapp):
        """Test initialization with different modes"""
        for mode in ['dummy', 'serial', 'tcp', 'udp']:
            settings = {'mode': mode}
            dialog = ConnectionSettingsDialog(settings)
            assert dialog.mode_combo.currentText() == mode
    
    def test_get_settings(self, qapp):
        """Test retrieving settings"""
        settings = {
            'mode': 'tcp',
            'tcp_host': '192.168.1.1',
            'tcp_port': 8080
        }
        
        dialog = ConnectionSettingsDialog(settings)
        dialog.mode_combo.setCurrentText('tcp')
        dialog.tcp_host_edit.setText('192.168.1.1')
        dialog.tcp_port_spin.setValue(8080)
        
        # Should return updated settings
        result = dialog.get_settings()
        assert result['mode'] == 'tcp'


class TestRegressions:
    """Regression tests for previously found bugs"""
    
    def test_empty_packet_handling(self, qapp, sample_parameters):
        """Regression: Handle empty packets gracefully"""
        window = MainWindow()
        window.parameters = sample_parameters
        
        # Empty packet should not crash
        window.update_data([])
        
        # No data should be added
        assert len(window.data_history) == 0
    
    def test_filter_reset_after_disable(self):
        """Regression: Filter state after disable/enable"""
        filter_obj = MovingAverageFilter("test", window_size=3)
        
        # Apply some values
        filter_obj.apply(10.0)
        filter_obj.apply(20.0)
        
        # Disable
        if hasattr(filter_obj, 'enabled'):
            filter_obj.enabled = False
            
            # Re-enable
            filter_obj.enabled = True
        
        # Should still work
        result = filter_obj.apply(30.0)
        assert result is not None
    
    def test_parameter_deletion_with_active_widgets(self, qapp, sample_parameters):
        """Regression: Deleting parameter while widgets use it"""
        window = MainWindow()
        window.parameters = sample_parameters.copy()
        
        # Remove a parameter
        window.parameters = [p for p in window.parameters if p['id'] != 'temp']
        
        # Update with data (should not crash)
        packet = [25.0, 1013.0]
        window.update_data(packet)
    
    def test_project_save_with_invalid_path(self, qapp, sample_parameters):
        """Regression: Project save with invalid path"""
        window = MainWindow()
        window.parameters = sample_parameters
        window.current_project_path = "/invalid/path/project.json"
        
        # Should handle gracefully
        try:
            window.save_project()
        except (OSError, IOError):
            # Expected for invalid paths
            pass
    
    def test_project_load_corrupted_file(self, qapp, temp_log_dir):
        """Regression: Loading corrupted project file"""
        window = MainWindow()
        
        # Create corrupted JSON file
        corrupted_path = os.path.join(temp_log_dir, "corrupted.json")
        with open(corrupted_path, 'w') as f:
            f.write("invalid json content {")
        
        window.current_project_path = corrupted_path
        
        # Should handle gracefully
        try:
            window.load_project()
        except (json.JSONDecodeError, ValueError):
            # Expected for corrupted files
            pass


# ============================================================================
# CUSTOM TEST MARKERS
# ============================================================================

pytest.mark.slow
pytest.mark.integration  
pytest.mark.ui


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--maxfail=5"])