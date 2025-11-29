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
        assert widget.param == param_config

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
