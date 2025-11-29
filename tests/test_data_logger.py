import pytest
import os
import shutil
import time
from unittest.mock import patch
from datetime import datetime
from app.core.data_logger import DataLogger

class TestDataLogger:
    @pytest.fixture
    def logger(self):
        if not os.path.exists("test_logs"):
            os.makedirs("test_logs")
            print("Created test_logs directory")
        logger = DataLogger()
        yield logger
        # Cleanup
        if logger.is_logging:
            logger.stop_logging()
        if os.path.exists("test_logs"):
            shutil.rmtree("test_logs")
            print("Removed test_logs directory")

    def test_initialization(self, logger):
        assert logger.is_logging is False
        assert logger.log_file is None

    def test_configure_csv(self, logger):
        config = {
            'format_type': 'csv',
            'file_path': 'test_logs/test.csv',
            'buffer_size': 5,
            'parameters': [{'id': 'param1', 'name': 'P1'}, {'id': 'param2', 'name': 'P2'}]
        }
        logger.configure(**config)
        assert logger.log_format == 'csv'
        assert logger.log_file_path == 'test_logs/test.csv'
        assert logger.buffer_size == 5
        assert logger.parameters == [{'id': 'param1', 'name': 'P1'}, {'id': 'param2', 'name': 'P2'}]

    def test_start_stop_logging(self, logger):
        config = {
            'format_type': 'csv',
            'file_path': 'test_logs/test_start_stop.csv',
            'buffer_size': 1,
            'parameters': [{'id': 'param1', 'name': 'P1'}]
        }
        logger.configure(**config)
        
        logger.start_logging()
        assert logger.is_logging is True
        assert os.path.exists('test_logs/test_start_stop.csv')
        
        logger.stop_logging()
        assert logger.is_logging is False
        assert logger.log_file is None

    def test_log_data_csv(self, logger):
        config = {
            'format_type': 'csv',
            'file_path': 'test_logs/test_data.csv',
            'buffer_size': 1, # Write immediately
            'parameters': [{'id': 'p1', 'name': 'P1'}]
        }
        logger.configure(**config)
        logger.start_logging()
        
        # Log data
        data_history = {'p1': [{'value': 10.5, 'timestamp': time.time()}]}
        logger.log_data(None, data_history)
        
        # Verify file content
        with open('test_logs/test_data.csv', 'r') as f:
            lines = f.readlines()
            assert len(lines) >= 2 # Header + 1 data line
            assert 'p1' in lines[0]
            assert '10.5' in lines[1]

    def test_log_data_json(self, logger):
        config = {
            'format_type': 'json',
            'file_path': 'test_logs/test_data.json',
            'buffer_size': 1,
            'parameters': [{'id': 'p1'}] # JSON header needs dicts with 'id'
        }
        logger.configure(**config)
        logger.start_logging()
        
        data_history = {'p1': [{'value': 20.0, 'timestamp': 1234567890}]}
        
        # Mock time.time to return a fixed value
        with patch('time.time', return_value=1234567890.0):
            logger.log_data(None, data_history)
        
        with open('test_logs/test_data.json', 'r') as f:
            content = f.read()
            
        assert 'Dashboard Data Log' in content
        # Check for ISO format timestamp
        iso_ts = datetime.fromtimestamp(1234567890).isoformat()
        assert iso_ts in content
        assert '"p1": 20.0' in content
