# Dashboard Builder

A professional real-time data visualization dashboard application built with PySide6 (Qt6) for Python. This application allows you to create custom dashboards for monitoring sensor data, system metrics, and any real-time data streams.

## Features

### 📊 **Multi-Widget Dashboard System**
- **Value Cards**: Display real-time numeric values with customizable colors and decimal places
- **Time Graphs**: Line charts showing data trends over time with configurable time ranges
- **Log Tables**: Tabular data display with scrolling history
- **Gauge Widgets**: Circular gauges with customizable min/max values and thresholds
- **Histogram Widgets**: Data distribution visualization with configurable bin counts
- **LED Indicators**: Visual status indicators with customizable thresholds
- **Map Widgets**: GPS coordinate visualization (requires QWebEngineView)

### 🔌 **Multiple Data Sources**
- **Serial Communication**: RS232/RS485 serial port connections
- **TCP/IP**: Network socket connections for remote data
- **UDP**: UDP socket connections for real-time streaming
- **Dummy Data**: Built-in simulator for testing and development

### 📈 **Real-Time Data Streaming**
- Live data visualization with configurable update rates
- Connection status monitoring (Connected/Disconnected indicators)
- Stream pause/resume functionality
- Data health monitoring with automatic status updates

### 📋 **Parameter Management**
- Comprehensive parameter configuration system
- Support for array-indexed data mapping
- Sensor grouping and categorization
- Customizable display preferences (colors, decimal places, units)
- Alarm threshold configuration (low/high warning/critical levels)
- Parameter validation and conflict detection

### 📁 **Data Logging**
- **CSV Export**: Structured comma-separated value files
- **JSON Export**: Hierarchical JSON format with timestamps
- Configurable buffer sizes for performance optimization
- Selective parameter logging (choose which parameters to log)
- Automatic file naming with timestamps
- Real-time logging status indicators

### 🎨 **Professional UI/UX**
- **4-Phase Dashboard Creation Wizard**:
  1. Welcome screen with quick start options
  2. Connection setup and parameter configuration
  3. Widget pre-configuration (optional)
  4. Live dashboard with real-time data
- Modern dark theme with professional styling
- Tabbed interface for multiple dashboard views
- Dockable widgets and resizable layouts
- Context menus and keyboard shortcuts

### 🔧 **Advanced Configuration**
- Project save/load functionality
- Connection settings persistence
- Custom data format parsing
- Configurable channel counts and data formats
- Port auto-detection for serial connections
- Network timeout and retry settings

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies
Install required packages:
```bash
pip install -r requirements.txt
```

### Required Packages
- `PySide6` - Qt6 Python bindings
- `pyqtgraph` - High-performance plotting library
- `numpy` - Numerical computing
- `pyserial` - Serial communication (optional, for serial data sources)
- `QWebEngineView` - Web engine for map widgets (optional)

## Quick Start

### 1. Launch the Application
```bash
python main.py
```

### 2. Create Your First Dashboard
1. Click "Create New Dashboard" on the welcome screen
2. Configure your data source in the setup phase:
   - **Dummy Data**: For testing (no hardware required)
   - **Serial**: Select COM port and baud rate
   - **TCP/UDP**: Enter host and port settings
3. Add parameters to monitor your data fields
4. Optionally pre-configure widgets in the widgets phase
5. Enter the live dashboard to start monitoring

### 3. Add Widgets
- Use the "Add Widget" button or menu option
- Select widget type and configure specific options
- Choose parameters to display
- Widgets will automatically update with live data

### 4. Configure Data Logging
- Go to "Data Logging" menu → "Configure Logging"
- Select file format (CSV or JSON)
- Choose parameters to log
- Set buffer size for performance
- Start logging from the menu or use keyboard shortcuts

## Data Source Configuration

### Serial Communication
- **Port**: Auto-detected available serial ports
- **Baud Rate**: 300 to 10,000,000 bps
- **Timeout**: Configurable connection timeout
- **Data Format**: JSON, CSV, raw bytes, or custom

### Network Connections (TCP/UDP)
- **Host**: IP address or hostname
- **Port**: 1-65535
- **Timeout**: Network timeout settings
- **Protocol**: TCP (reliable) or UDP (fast, best-effort)

### Data Format Options
- **JSON Array**: `[value1, value2, value3, ...]`
- **CSV**: `value1,value2,value3,...`
- **Raw Bytes**: Binary data interpretation
- **Custom**: Define your own parsing format

## Parameter Configuration

Each parameter can be configured with:
- **Basic Info**: ID, name, description
- **Data Mapping**: Array index, sensor group
- **Display**: Unit, color, decimal places
- **Alarms**: Low/high warning and critical thresholds

Example parameter configuration:
```json
{
  "id": "temperature_sensor",
  "name": "Temperature",
  "array_index": 0,
  "sensor_group": "Environmental",
  "unit": "°C",
  "description": "Ambient temperature sensor",
  "color": "#FF3131",
  "decimals": 1,
  "threshold": {
    "low_crit": -10,
    "low_warn": 0,
    "high_warn": 80,
    "high_crit": 100
  }
}
```

## Widget Types and Options

### Value Card
- Real-time numeric display
- Customizable colors and formatting
- Alarm status indicators

### Time Graph
- Configurable time range (1 min to 24 hours)
- Multiple parameter overlay
- Zoom and pan functionality

### Gauge Widget
- Customizable min/max values
- Threshold visualization
- Circular or arc display

### Histogram Widget
- Configurable bin count (10-100)
- Real-time distribution updates
- Statistical overlay

### LED Indicator
- Threshold-based color changes
- Customizable on/off states
- Status text display

### Map Widget (GPS)
- Real-time position tracking
- Zoom controls
- Requires QWebEngineView

## Data Logging

### Supported Formats

#### CSV Format
```csv
timestamp,temperature_sensor,humidity_sensor,pressure_sensor
2024-01-15 10:30:00.123,23.5,65.2,1013.25
2024-01-15 10:30:01.124,23.6,65.1,1013.26
```

#### JSON Format
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "data": {
    "temperature_sensor": 23.5,
    "humidity_sensor": 65.2,
    "pressure_sensor": 1013.25
  }
}
```

### Logging Configuration
- **Buffer Size**: 10-1000 records (affects memory usage vs. disk I/O)
- **File Path**: Custom output location
- **Parameter Selection**: Choose which parameters to log
- **Format Selection**: CSV or JSON output

## Project Structure

```
Dashboard-Builder/
├── main.py                 # Main application entry point
├── backend.py              # Data reading and parsing engine
├── app/
│   ├── widgets.py          # Custom widget implementations
│   ├── dialogs.py          # Dialog windows and forms
│   └── ui/
│       └── main_window.py  # Main window UI components
├── requirements.txt        # Python dependencies
├── preset1.json           # Example configuration
└── README.md              # This file
```

## Keyboard Shortcuts

- `Ctrl+N` - New Dashboard
- `Ctrl+O` - Load Project
- `Ctrl+S` - Save Project
- `Ctrl+Shift+A` - Add Widget
- `Ctrl+Shift+P` - Manage Parameters
- `Ctrl+Shift+L` - Configure Logging
- `Space` - Pause/Resume Stream
- `F11` - Toggle Fullscreen

## Troubleshooting

### Common Issues

#### Serial Connection Problems
- Verify COM port is available and not in use
- Check baud rate matches device configuration
- Ensure proper drivers are installed
- Try different timeout values

#### Network Connection Issues
- Verify host IP address and port
- Check firewall settings
- Ensure network connectivity
- Validate data format matches expected input

#### Widget Display Issues
- Check parameter configuration
- Verify data is being received
- Ensure array indices match data structure
- Check for parameter ID conflicts

#### Data Logging Problems
- Verify write permissions to output directory
- Check disk space availability
- Ensure parameters are selected for logging
- Monitor buffer size for memory usage

### Performance Optimization

#### For High-Frequency Data
- Increase buffer size for logging
- Reduce widget update rates
- Use simpler widget types (Value Cards vs. Graphs)
- Limit number of active widgets

#### For Large Datasets
- Use CSV format for logging
- Implement data archiving
- Consider data compression
- Monitor memory usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information

## Version History

### v2.0.0 (Current)
- Complete UI/UX redesign with 4-phase wizard
- Enhanced parameter management system
- Comprehensive data logging (CSV/JSON)
- Connection status monitoring
- Professional dark theme
- Improved widget configuration
- Better error handling and validation

### v1.0.0
- Basic dashboard functionality
- Serial and network data sources
- Core widget types
- Simple parameter configuration