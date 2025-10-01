# Dashboard Builder

**Professional Real-Time Telemetry Visualization Platform**

A sophisticated data visualization dashboard application built with PySide6 (Qt6) for monitoring and analyzing real-time sensor data, system metrics, and telemetry streams. Developed by **Team Ignition Software Department** at Vellore Institute of Technology, Chennai.

---

## Table of Contents

1. [About](#about)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Quick Start Guide](#quick-start-guide)
6. [User Guide](#user-guide)
7. [Configuration Reference](#configuration-reference)
8. [Data Logging](#data-logging)
9. [Troubleshooting](#troubleshooting)
10. [Development](#development)
11. [About Team Ignition](#about-team-ignition)
12. [License](#license)

---

## About

Dashboard Builder is a professional-grade telemetry visualization platform designed for real-time monitoring of sensor data from rockets, drones, embedded systems, and other data-acquisition applications. The application provides a flexible, widget-based dashboard system with support for multiple data sources and comprehensive logging capabilities.

### Key Capabilities

- **Real-time visualization** of sensor data streams
- **Multiple data source support** (Serial, TCP, UDP, Dummy)
- **Customizable widget system** with 7+ widget types
- **Comprehensive data logging** (CSV, JSON)
- **Professional UI/UX** with dark theme
- **Project save/load** for reusable configurations

---

## Features

### Widget Types

| Widget | Description | Use Case |
|--------|-------------|----------|
| **Value Card** | Large numeric display with alarm states | Critical parameters (temperature, pressure) |
| **Time Graph** | Multi-parameter line chart with time axis | Trend analysis over time |
| **Gauge** | Circular gauge with threshold indicators | Visual ranges (speed, altitude) |
| **Histogram** | Distribution visualization | Statistical analysis |
| **LED Indicator** | Status light with color-coded states | Binary or threshold-based status |
| **Log Table** | Scrolling tabular data | Detailed data inspection |
| **Map Widget** | GPS coordinate visualization | Location tracking |

### Data Sources

- **Serial (RS232/RS485)**: Direct hardware connections
- **TCP/IP**: Network-based remote monitoring
- **UDP**: Fast, real-time streaming
- **Dummy Data**: Built-in simulator for testing

### Data Formats

- JSON arrays: `[23.5, 65.2, 1013.25, ...]`
- CSV: `23.5,65.2,1013.25,...`
- Raw bytes: Binary data interpretation
- Custom: User-defined parsing

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4 GB
- **Display**: 1280x720 resolution

### Recommended Requirements

- **OS**: Windows 11, Linux (Ubuntu 22.04+), macOS 12+
- **Python**: 3.10 or higher
- **RAM**: 8 GB or more
- **Display**: 1920x1080 or higher resolution
- **Network**: Ethernet for TCP/UDP sources

---

## Installation

### Step 1: Install Python

Ensure Python 3.8+ is installed on your system:

```bash
python --version
```

If not installed, download from [python.org](https://www.python.org/downloads/).

### Step 2: Clone Repository

```bash
git clone https://github.com/teamignitionvitc/Dashboard-Builder.git
cd Dashboard-Builder
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `PySide6` - Qt6 bindings for UI
- `pyqtgraph` - High-performance plotting
- `numpy` - Numerical computing
- `pyserial` - Serial communication (optional)

**Optional packages:**
- `PySide6-WebEngine` - For GPS map widgets

### Step 4: Verify Installation

```bash
python main.py
```

The application should launch with the welcome screen.

---

## Quick Start Guide

### 1. Launch Application

```bash
python main.py
```

### 2. Create New Dashboard

1. Click **"Create New Dashboard"** on the welcome screen
2. You'll enter the **4-phase dashboard creation wizard**

### 3. Configure Connection (Setup Phase)

#### For Testing (No Hardware):
- Select **Connection Mode**: `dummy`
- Click **"Start Dashboard"**

#### For Serial Hardware:
- Select **Connection Mode**: `serial`
- Choose **Serial Port** from dropdown (auto-detected)
- Set **Baudrate** (e.g., `115200`)
- Configure **Data Format** (e.g., `json_array`)
- Set **Channel Count** (e.g., `32`)
- Click **"Start Dashboard"**

#### For Network Sources:
- Select **Connection Mode**: `tcp` or `udp`
- Enter **Host** (e.g., `192.168.1.100`)
- Enter **Port** (e.g., `9000`)
- Configure **Data Format**
- Click **"Start Dashboard"**

### 4. Configure Parameters

Before or after starting the dashboard:
1. Go to **Edit** → **Manage Parameters**
2. Click **"Add..."** to create a new parameter
3. Fill in parameter details:
   - **ID**: Unique identifier (e.g., `temp_sensor`)
   - **Name**: Display name (e.g., `Temperature`)
   - **Array Index**: Position in data array (e.g., `0`)
   - **Unit**: Measurement unit (e.g., `°C`)
   - **Thresholds**: Alarm levels
4. Click **OK** to save
5. Repeat for all parameters
6. Click **Close**

### 5. Add Widgets

1. Click **"Add Widget..."** button or use **Edit** → **Add Widget**
2. Select **Widget Type** from dropdown
3. Choose **Parameters** to display
4. Configure widget-specific options
5. Click **OK**

The widget will appear in your dashboard and automatically update with live data.

### 6. Save Project

1. Go to **File** → **Save Project**
2. Choose location and filename (`.json` extension)
3. Click **Save**

Your dashboard configuration is now saved and can be reloaded anytime.

---

## User Guide

### Dashboard Interface

#### Top Bar (Header)
- **Dashboard Title**: Customizable title (right-click to edit)
- **Connection Status**: Real-time connection indicator
- **Stream Status**: STREAMING, PAUSED, or AWAITING PARAMETERS
- **Logging Status**: Shows if data logging is active
- **Pause Button**: Pause/resume data stream

#### Status Bar (Bottom)
- **System Clock**: Current date and time
- **Connection Details**: Active connection information
- **Uptime**: Dashboard runtime
- **RX**: Total bytes received
- **Packets**: Total packet count
- **Rate**: Packets per second

#### Main Area
- **Tabbed Dashboard**: Multiple dashboard views
- **Dockable Widgets**: Drag to rearrange
- **Context Menus**: Right-click on widgets for options

### Working with Parameters

#### Parameter Properties

| Property | Description | Example |
|----------|-------------|---------|
| **ID** | Unique identifier (no spaces) | `accel_x` |
| **Name** | Display name | `Acceleration X` |
| **Array Index** | Position in data packet | `3` |
| **Sensor Group** | Categorization | `IMU` |
| **Unit** | Measurement unit | `m/s²` |
| **Description** | Detailed info | `X-axis acceleration from IMU` |
| **Thresholds** | Alarm levels | Low Crit: -20, High Crit: 20 |

#### Managing Parameters

**To Add a Parameter:**
1. **Edit** → **Manage Parameters** → **Add...**
2. Fill in all fields
3. Set threshold values in ascending order
4. Click **OK**

**To Edit a Parameter:**
1. **Edit** → **Manage Parameters**
2. Select parameter from list
3. Click **Edit...**
4. Modify fields
5. Click **OK**

**To Delete a Parameter:**
1. **Edit** → **Manage Parameters**
2. Select parameter
3. Click **Remove**
4. Confirm deletion

### Working with Widgets

#### Adding Widgets

**Method 1: Menu**
1. **Edit** → **Add Widget...**
2. Select widget type
3. Choose parameters
4. Configure options
5. Click **OK**

**Method 2: Toolbar Button**
1. Click **"Add Widget"** button
2. Follow same steps as above

#### Widget Configuration

**Value Card:**
- Select **1 parameter**
- Choose **priority** (High, Medium, Low)
- Sets border color based on priority

**Time Graph:**
- Select **1+ parameters**
- Each parameter gets unique color
- Auto-scaling Y-axis
- Zoomable and pannable

**Gauge Widget:**
- Select **1 parameter**
- Configure min/max values
- Set threshold indicators

**Histogram:**
- Select **1 parameter**
- Choose bin count (10-100)
- Shows distribution of recent values

**LED Indicator:**
- Select **1 parameter**
- Color changes based on thresholds:
  - Blue: Below low_warn
  - Green: Normal range
  - Yellow: High warning
  - Red: Critical

**Log Table:**
- Select **1+ parameters**
- Shows timestamped data
- Search and highlight functionality

**Map Widget:**
- Select **exactly 2 parameters** (Latitude, Longitude)
- Real-time position tracking
- Zoom controls
- Requires `PySide6-WebEngine`

#### Managing Widgets

**Rename Widget:**
1. Right-click on widget title bar
2. Select **"Rename Widget"**
3. Enter new name
4. Click **OK**

**Float/Dock Widget:**
1. Right-click on widget
2. Select **"Float / Dock"**
3. Widget toggles between floating window and docked state

**Close Widget:**
1. Right-click on widget
2. Select **"Close Widget"**
3. Widget is removed from dashboard

**Tile Widgets Evenly:**
1. Right-click on any widget
2. Select **"Tile Evenly"**
3. All widgets arrange in grid layout

### Working with Tabs

#### Creating Tabs

1. **View** → **Add Tab**
2. Enter tab name
3. Click **OK**

New tab appears with empty dashboard.

#### Renaming Tabs

1. **View** → **Rename Current Tab**
2. Enter new name
3. Click **OK**

#### Closing Tabs

Click **X** button on tab (if closable).

**Note**: First tab is usually not closable by default.

### Data Stream Control

#### Pause/Resume Stream

**Method 1**: Click **"Pause Stream"** button in header
**Method 2**: Press **Space** bar

When paused:
- Data stops updating
- Button changes to **"Resume Stream"**
- Status shows **PAUSED**

#### Raw Telemetry Monitor

View raw incoming data packets:

1. **View** → **Raw Telemetry Monitor**
2. Monitor window opens showing:
   - Packet timestamps
   - Packet numbers
   - Raw data values
   - Packet rate statistics

**Features:**
- **Pause**: Stop display updates
- **Clear**: Clear display buffer
- **Auto-scroll**: Automatically scroll to newest data
- **Show Hex**: Toggle hex/decimal display
- **Save to File**: Export raw data log

---

## Configuration Reference

### Connection Settings

Access via **File** → **Connection Settings...**

#### Serial Configuration

```
Mode: serial
Serial Port: COM4 (Windows) or /dev/ttyUSB0 (Linux)
Baudrate: 115200
Timeout: 1.0 seconds
Data Format: json_array
Channel Count: 32
Sample Width: 2 bytes
Endianness: little
```

#### TCP Configuration

```
Mode: tcp
TCP Host: 192.168.1.100
TCP Port: 9000
Timeout: 1.0 seconds
Data Format: json_array
Channel Count: 32
```

#### UDP Configuration

```
Mode: udp
UDP Host: 0.0.0.0 (listen all interfaces)
UDP Port: 9000
Timeout: 1.0 seconds
Data Format: json_array
Channel Count: 32
```

### Data Format Configuration

#### JSON Array Format
```json
[23.5, 65.2, 1013.25, 9.8, 0.5, -1.2, ...]
```
- Array of numeric values
- Index maps to parameter array_index
- Most flexible format

#### CSV Format
```
23.5,65.2,1013.25,9.8,0.5,-1.2,...
```
- Comma-separated values
- Configure custom separator if needed
- Good for simple logging

#### Raw Bytes Format
- Binary data interpretation
- Configure sample width (1-8 bytes)
- Configure endianness (little/big)
- Useful for compact transmission

### Project File Structure

Project files (`.json`) contain:

```json
{
  "parameters": [...],
  "layout": {...},
  "connection_settings": {...},
  "logging_settings": {...},
  "configured_widgets": [...],
  "dashboard_title_text": "Dashboard",
  "dashboard_title_alignment": "1",
  "version": "1.0",
  "created": "2025-01-15T10:30:00"
}
```

---

## Data Logging

### Configuring Data Logging

1. **Data Logging** → **Configure Logging...**
2. Configure settings:
   - **Format**: CSV or JSON
   - **File Path**: Output location (auto-generated if blank)
   - **Parameters**: Select which parameters to log
   - **Buffer Size**: 10-1000 (higher = less frequent disk writes)
3. Click **OK**

### Starting/Stopping Logging

**Start Logging:**
- **Data Logging** → **Start Logging**
- Status bar shows: **Logging: ON (filename)**

**Stop Logging:**
- **Data Logging** → **Stop Logging**
- Data flushed to disk
- Status bar shows: **Logging: OFF**

### Log File Formats

#### CSV Format

```csv
timestamp,elapsed_time,temp_sensor_Temperature,humidity_Humidity
2025-01-15 10:30:00.123,0.000,23.500,65.200
2025-01-15 10:30:01.223,1.100,23.600,65.100
2025-01-15 10:30:02.323,2.200,23.700,65.000
```

**Columns:**
- `timestamp`: ISO 8601 formatted timestamp
- `elapsed_time`: Seconds since logging started
- `{param_id}_{param_name}`: One column per logged parameter

#### JSON Format

```json
# Dashboard Data Log
# Format: JSON Lines (one JSON object per line)
# Parameters: temp_sensor, humidity
# Start Time: 2025-01-15T10:30:00

{"timestamp": "2025-01-15T10:30:00.123", "elapsed_time": 0.0, "parameters": {"temp_sensor": 23.5, "humidity": 65.2}}
{"timestamp": "2025-01-15T10:30:01.223", "elapsed_time": 1.1, "parameters": {"temp_sensor": 23.6, "humidity": 65.1}}
```

**Format:** JSON Lines (one object per line)

### Buffer Size Recommendations

| Data Rate | Buffer Size | Disk Write Frequency |
|-----------|-------------|---------------------|
| 1-10 Hz | 100 | Every 10-100 seconds |
| 10-50 Hz | 200-500 | Every 4-50 seconds |
| 50+ Hz | 500-1000 | Every 10-20 seconds |

**Note**: Larger buffers reduce disk I/O but increase memory usage and potential data loss on crash.

---

## Troubleshooting

### Connection Issues

#### Serial Port Not Found

**Symptoms**: Port doesn't appear in dropdown

**Solutions**:
1. Check device is connected
2. Install device drivers
3. Check port permissions (Linux: `sudo usermod -a -G dialout $USER`)
4. Click "Refresh" button to update port list
5. Try manual entry of port name

#### Serial Connection Failed

**Symptoms**: "Disconnected (Serial)" status

**Solutions**:
1. Verify baud rate matches device
2. Close other applications using the port
3. Check cable connection
4. Try different timeout value
5. Verify data format matches device output

#### Network Connection Issues

**Symptoms**: "Disconnected (TCP/UDP)" status

**Solutions**:
1. Verify IP address and port
2. Check firewall settings
3. Ping host to verify connectivity
4. For UDP: Ensure device is sending to correct port
5. For TCP: Verify server is listening

### Data Display Issues

#### No Data Appearing in Widgets

**Checklist**:
- [ ] Connection status shows "Connected"
- [ ] Stream status shows "STREAMING" (not paused)
- [ ] Parameters are properly configured
- [ ] Array indices match data structure
- [ ] Data format matches incoming data
- [ ] Check Raw Telemetry Monitor for incoming packets

#### Incorrect Data Values

**Solutions**:
1. Verify array index mapping
2. Check data format configuration
3. Verify endianness for raw bytes
4. Check for parameter ID conflicts
5. Inspect raw data in Telemetry Monitor

#### Widgets Not Updating

**Solutions**:
1. Check if stream is paused
2. Verify parameter IDs in widget configuration
3. Restart application
4. Check system resources (CPU/memory)

### Performance Issues

#### High CPU Usage

**Solutions**:
1. Reduce number of active widgets
2. Increase data logging buffer size
3. Use simpler widget types (Value Cards vs. Graphs)
4. Close unused tabs
5. Reduce graph history length

#### High Memory Usage

**Solutions**:
1. Clear old data periodically (restart application)
2. Reduce data logging buffer size
3. Limit number of parameters
4. Close unused widgets
5. Monitor with Task Manager/Activity Monitor

#### Slow UI Response

**Solutions**:
1. Reduce widget update frequency
2. Simplify dashboard layout
3. Close background applications
4. Upgrade hardware if possible

### Data Logging Issues

#### Cannot Start Logging

**Symptoms**: Error message when starting

**Solutions**:
1. Configure logging first (Data Logging → Configure)
2. Check write permissions to output directory
3. Verify disk space available
4. Close file if open in another application
5. Try different output location

#### Missing Data in Log Files

**Solutions**:
1. Ensure logging was started
2. Stop logging to flush buffer before checking file
3. Verify parameters are selected in configuration
4. Check buffer size isn't too large
5. Verify disk space didn't run out

### Application Crashes

#### On Startup

**Solutions**:
1. Check Python version (3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Delete config files in user directory
4. Check console for error messages

#### During Operation

**Solutions**:
1. Check console for error messages
2. Verify data format matches incoming data
3. Check for corrupted project file
4. Monitor system resources
5. Report issue with error log

---

## Development

### Project Structure

```
Dashboard-Builder/
├── main.py                      # Application entry point
├── backend.py                   # Data reader and parser
├── requirements.txt             # Python dependencies
├── README.md                    # This documentation
├── LICENSE                      # License file
├── app/
│   ├── __init__.py
│   ├── widgets.py               # Custom widget implementations
│   ├── dialogs.py               # Dialog windows
│   └── ui/
│       ├── __init__.py
│       └── main_window.py       # Main window implementation
├── public/
│   └── ign_logo_wht.png         # Team logo
└── examples/
    └── preset1.json             # Example configuration
```

### Adding Custom Widgets

1. Create widget class in `app/widgets.py`
2. Inherit from `QWidget` or `QFrame`
3. Implement `update_value()` or `update_data()` method
4. Add to `AddWidgetDialog` in `app/dialogs.py`
5. Update `add_widget_to_dashboard()` in `main.py`

### Adding Data Formats

1. Update `backend.py` `DataReader` class
2. Add format to `parse_line()` method
3. Update connection settings dialog
4. Document format in README

### Building Executable

#### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Dashboard Builder" main.py
```

Executable will be in `dist/` directory.

---

## About Team Ignition

**Team Ignition** is the official student rocketry team of **Vellore Institute of Technology, Chennai**, founded with the vision of advancing aerospace innovation through hands-on learning and experimentation.

### Our Mission

We design, build, and launch model and experimental rockets, developing every subsystem in-house — from **propulsion and avionics to payloads and recovery systems**. Our projects range from solid and hybrid rocket motor development to **flight computers, payloads like CubeSats and CanSats, and ground-support software applications**.

### What We Do

By combining engineering rigor with creativity, we actively participate in **national and international rocketry competitions**, while also conducting workshops, seminars, and outreach programs to inspire future engineers.

As a **student-led, self-funded team**, we place strong emphasis on innovation, collaboration, and technical excellence. Every project we take on — whether hardware or software — contributes to our goal of pushing boundaries in rocketry and aerospace research, while also equipping our members with practical, industry-relevant skills.

### Connect With Us

- **Website**: [teamignition.space](https://teamignition.space)
- **GitHub**: [github.com/teamignitionvitc](https://github.com/teamignitionvitc)
- **Twitter**: [@ignitiontech23](https://x.com/ignitiontech23)
- **LinkedIn**: [Team Ignition](https://www.linkedin.com/in/teamignition/)
- **Instagram**: [@ignition_vitc](https://www.instagram.com/ignition_vitc)

### Software Department

This Dashboard Builder was developed by the **Software Department** of Team Ignition as part of our ground-support equipment suite for rocket telemetry and monitoring.

---

## License

This project is licensed under the **GNU General Public License v3.0** with additional restrictions.

### Additional Restriction

This software may not be used for commercial purposes without explicit written permission from the authors (Team Ignition Software Department).

### Full License

```
Copyright (c) 2025 Ignition Software Department

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3, with the additional restriction
that this software may not be used for commercial purposes without
explicit written permission from the authors.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

---

## Support and Contributions

### Getting Help

1. Check this README documentation
2. Review [Troubleshooting](#troubleshooting) section
3. Check existing GitHub issues
4. Create new issue with:
   - System information (OS, Python version)
   - Steps to reproduce problem
   - Error messages/logs
   - Screenshots if applicable

### Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Issue Reporting

Please report issues on GitHub with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- System information
- Relevant logs/screenshots

---

## Acknowledgments

- Built with PySide6 (Qt6)
- Plotting powered by pyqtgraph
- Serial communication via pyserial
- Developed by Team Ignition Software Department
- Tested by Team Ignition members during rocket ground operations

---

## Version History

### v2.0.0 (Current)
- Complete UI/UX redesign with 4-phase wizard
- Enhanced parameter management system
- Comprehensive data logging (CSV/JSON)
- Raw telemetry monitor
- Connection status monitoring
- Professional dark theme
- Improved widget configuration
- Better error handling and validation
- Dashboard title customization
- Performance optimizations

### v1.0.0
- Initial release
- Basic dashboard functionality
- Serial and network data sources
- Core widget types
- Simple parameter configuration

---

**Dashboard Builder** - Professional telemetry visualization by Team Ignition
*Advancing aerospace innovation through software excellence*