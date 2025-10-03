<div align="center">

![Dashboard Builder Logo](public/Glance.png)

# Dashboard Builder

### Professional Real-Time Telemetry Visualization Platform

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green)](https://pypi.org/project/PySide6/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/teamignitionvitc/Dashboard-Builder)

*A sophisticated data visualization dashboard for monitoring real-time sensor data, telemetry streams, and system metrics*

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](https://glance.teamignition.space/) • [Contributing](#-contributing)

---

![Team Ignition Logo](public/ign_logo_wht.png)

**Developed by Team Ignition Software Department**  
*Official Model Rocketry Team of Vellore Institute of Technology, Chennai*

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [User Guide](#-user-guide)
- [Data Sources](#-data-sources)
- [Widget Types](#-widget-types)
- [Data Logging](#-data-logging)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [About Team Ignition](#-about-team-ignition)
- [License](#-license)
- [Support](#-support)

---

## 🚀 About

**Glance** is a sophisticated real-time telemetry visualization platform designed for rockets, drones, embedded systems, and advanced data-acquisition applications. Built with PySide6 (Qt6), it offers a modular, widget-based dashboard that adapts to diverse telemetry needs. With multi-source connectivity, powerful data logging, and professional UI/UX, Glance empowers engineers, researchers, and operators to gain actionable insights — all at a single glance.
### Key Capabilities

- ⚡ **Real-time visualization** of multi-channel sensor data
- 🔌 **Multiple data sources**: Serial, TCP, UDP, Dummy simulation
- 🎨 **7+ widget types**: Graphs, gauges, tables, maps, and more
- 💾 **Comprehensive logging**: CSV and JSON with configurable buffers
- 🎯 **Professional UI/UX**: Modern dark theme with intuitive controls
- 💼 **Project management**: Save and reload complete configurations

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 📊 Visualization

- Multi-parameter time-series graphs
- Real-time value cards with alarm states
- Circular gauges with threshold indicators
- Statistical histograms
- LED status indicators
- GPS mapping (with optional WebEngine)
- Searchable data tables

</td>
<td width="50%">

### 🔧 Technical

- Serial (RS232/RS485) communication
- TCP/IP and UDP network protocols
- JSON, CSV, and raw binary parsing
- Configurable data formats
- Buffer management for performance
- Automatic port detection
- Raw telemetry monitoring

</td>
</tr>
<tr>
<td width="50%">

### 📝 Data Management

- CSV and JSON data logging
- Configurable buffer sizes
- Parameter-selective logging
- Auto-generated filenames
- Timestamped entries
- Buffer flushing controls

</td>
<td width="50%">

### 🎨 User Experience

- 4-phase dashboard wizard
- Drag-and-drop widget arrangement
- Multi-tab dashboard support
- Customizable dashboard titles
- Floating and docked widgets
- Right-click context menus
- Comprehensive keyboard shortcuts

</td>
</tr>
</table>

---

## 📸 Screenshots

<div align="center">

### Home Screen
![Welcome Screen](public/Doc%20Images/HomeScreen.png)
*Home Screen*

### Dashboard View
![Dashboard View](public/Doc%20Images/dashboard.png)
*Real-time telemetry visualization with multiple widgets*

### Parameter Management
![Parameter Management](public/Doc%20Images/parameters.png)
*Intuitive parameter configuration interface*

### Connection Settings
![Connection Settings](public/Doc%20Images/Connection.png)
*Flexible data source configuration*

### Data Logging
![Data Logging](public/Doc%20Images/logging.png)
*Comprehensive logging with format selection*

</div>

---

## 💻 System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+ |
| **Python** | 3.8 or higher |
| **RAM** | 4 GB |
| **Display** | 1280x720 resolution |
| **Storage** | 500 MB free space |

### Recommended Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 11, Linux (Ubuntu 22.04+), macOS 12+ |
| **Python** | 3.10 or higher |
| **RAM** | 8 GB or more |
| **Display** | 1920x1080 or higher |
| **Network** | Ethernet for TCP/UDP sources |
| **Storage** | 1 GB+ for data logging |

---

## 📦 Installation

### Method 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/teamignitionvitc/Dashboard-Builder.git
cd Dashboard-Builder

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

### Method 2: Virtual Environment (Recommended)

```bash
# Clone repository
git clone https://github.com/teamignitionvitc/Dashboard-Builder.git
cd Dashboard-Builder

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

### Required Dependencies

```
PySide6>=6.4.0          # Qt6 bindings for UI
pyqtgraph>=0.13.0       # High-performance plotting
numpy>=1.21.0           # Numerical computing
pyserial>=3.5           # Serial communication (optional)
```

### Optional Dependencies

```
PySide6-WebEngine       # For GPS map widgets (recommended)
```

To install optional dependencies:

```bash
pip install PySide6-WebEngine
```

---

## 🚀 Quick Start

### 1. Launch Application

```bash
python main.py
```

### 2. Choose Your Path

**For First-Time Users:**
- Click **"Create New Dashboard"**
- Follow the 4-phase setup wizard

**For Returning Users:**
- Click **"Load Project..."**
- Select your saved `.json` configuration

### 3. Configure Connection

#### Testing Without Hardware (Dummy Mode)
```
Connection Mode: dummy
Data Format: json_array
Channel Count: 32
```
Click **"Start Dashboard"**

#### Serial Hardware Connection
```
Connection Mode: serial
Serial Port: COM4 (auto-detected)
Baudrate: 115200
Data Format: json_array
Channel Count: 32
```
Click **"Start Dashboard"**

#### Network Connection (TCP/UDP)
```
Connection Mode: tcp (or udp)
Host: 192.168.1.100
Port: 9000
Data Format: json_array
Channel Count: 32
```
Click **"Start Dashboard"**

### 4. Define Parameters

Navigate to **Edit → Manage Parameters**

Example parameter configuration:
```
ID: temp_sensor
Name: Temperature
Array Index: 0
Sensor Group: Environmental
Unit: °C
Description: Ambient temperature sensor

Thresholds:
  Low Critical: -10
  Low Warning: 0
  High Warning: 80
  High Critical: 100
```

### 5. Add Widgets

Click **"Add Widget..."** and configure:
- Select widget type (Value Card, Time Graph, etc.)
- Choose parameters to display
- Configure widget-specific options

### 6. Save Your Work

**File → Save Project** to preserve your configuration

---

## 📖 User Guide

### Dashboard Interface

<p align="center">
  <img src="public/user_interface.gif" width="700"/>
</p>


### Working with Parameters

Parameters define the data channels you want to monitor. Each parameter maps to an index in your incoming data array.

**Parameter Properties:**

| Property | Description | Example |
|----------|-------------|---------|
| **ID** | Unique identifier (no spaces) | `accel_x` |
| **Name** | Human-readable display name | `Acceleration X` |
| **Array Index** | Position in data packet (0-based) | `3` |
| **Sensor Group** | Category for organization | `IMU` |
| **Unit** | Measurement unit | `m/s²` |
| **Description** | Detailed information | `X-axis acceleration from IMU` |
| **Thresholds** | Alarm level definitions | See below |

**Threshold Configuration:**

Thresholds must be in ascending order:
```
Low Critical < Low Warning < High Warning < High Critical
    -20    <     -10     <      10      <      20
```

### Widget Configuration Guide

#### 1. Value Card
```
Purpose: Display single parameter with large numeric value
Parameters: 1
Options: Priority (High/Medium/Low)
Best For: Critical parameters needing constant monitoring
```

#### 2. Time Graph
```
Purpose: Multi-parameter line chart over time
Parameters: 1+
Options: Auto-assigned colors per parameter
Best For: Trend analysis, comparing related parameters
Features: Zoom, pan, auto-scale, crosshair cursor
```

#### 3. Gauge Widget
```
Purpose: Visual representation with threshold zones
Parameters: 1
Options: Min/max values, threshold indicators
Best For: Parameters with defined operational ranges
```

#### 4. Histogram
```
Purpose: Statistical distribution visualization
Parameters: 1
Options: Bin count (10-100)
Best For: Analyzing data distribution patterns
```

#### 5. LED Indicator
```
Purpose: Binary or threshold-based status display
Parameters: 1
Color States:
  - Blue: Below low_warn
  - Green: Normal range (low_warn to high_warn)
  - Yellow: High warning (high_warn to high_crit)
  - Red: Critical (above high_crit or below low_crit)
Best For: Quick status monitoring
```

#### 6. Log Table
```
Purpose: Timestamped tabular data display
Parameters: 1+
Features: Search, highlight, scrolling history
Best For: Detailed data inspection, debugging
```

#### 7. Map Widget
```
Purpose: GPS coordinate visualization
Parameters: Exactly 2 (Latitude, Longitude)
Requirements: PySide6-WebEngine
Features: Real-time tracking, zoom, satellite view
Best For: Location monitoring, trajectory tracking
```

---

## 🔌 Data Sources

### Serial Communication

**Use Case**: Direct hardware connections via RS232, RS485, USB-Serial

**Configuration:**
```python
Mode: serial
Port: COM4 (Windows) or /dev/ttyUSB0 (Linux)
Baudrate: 9600, 115200, 230400, etc.
Timeout: 1.0 seconds
```

**Common Issues:**
- Port access denied → Check permissions (Linux: add user to dialout group)
- No data → Verify baudrate matches device
- Corrupted data → Check cable quality, try lower baudrate

### TCP/IP

**Use Case**: Network-based remote monitoring, Ethernet connections

**Configuration:**
```python
Mode: tcp
Host: 192.168.1.100 (device IP)
Port: 9000 (application port)
Timeout: 1.0 seconds
```

**Common Issues:**
- Connection refused → Verify server is listening on specified port
- No data → Check firewall settings
- Intermittent connection → Network stability, cable quality

### UDP

**Use Case**: Fast, real-time streaming where packet loss is acceptable

**Configuration:**
```python
Mode: udp
Host: 0.0.0.0 (listen on all interfaces)
Port: 9000 (listening port)
Timeout: 1.0 seconds
```

**Common Issues:**
- No packets received → Check firewall, verify sender configuration
- Packet loss → Expected with UDP; use TCP if critical
- Wrong data → Verify sender is transmitting to correct IP/port

### Dummy Data

**Use Case**: Testing, demonstrations, development

**Features:**
- Simulates 32-channel sensor array
- Sine wave patterns with random noise
- No external hardware required
- Configurable from 1-1024 channels

---

## 📊 Widget Types

### Value Card

<table>
<tr>
<td width="30%">

**Features:**
- Large numeric display
- Alarm state colors
- Priority border
- Unit display

</td>
<td width="70%">

**Alarm States:**
- 🟢 **Nominal**: Green background, value within normal range
- 🟡 **Warning**: Yellow background, approaching limits
- 🔴 **Critical**: Red background, exceeded safe limits

**Priority Levels:**
- High: Red border
- Medium: Blue border
- Low: No border

</td>
</tr>
</table>

### Time Graph

**Advanced Features:**
- **Zoom**: Mouse wheel or drag-select
- **Pan**: Click and drag
- **Crosshair**: Hover for value inspection
- **Legend**: Shows all plotted parameters
- **Auto-scale**: Y-axis adjusts to data range
- **Reset View**: Toolbar button to restore defaults

**Keyboard Shortcuts:**
- **Ctrl + Mouse Wheel**: Zoom Y-axis only
- **Shift + Mouse Wheel**: Zoom X-axis only
- **Right-click + Drag**: Pan view
- **Double-click**: Auto-scale to fit all data

### Gauge Widget

**Zones:**
- Red zone: Critical (beyond high_crit or below low_crit)
- Yellow zone: Warning (between warning and critical)
- Green zone: Normal (between low_warn and high_warn)
- Blue zone: Low (below low_warn)

**Visual Elements:**
- Needle indicator with smooth animation
- Colored arc segments
- Current value display
- Min/max labels

### Log Table

**Search Functionality:**
```
1. Select parameter from dropdown
2. Choose comparison operator (=, >, <, >=, <=)
3. Enter target value
4. Click "Search Last"
5. Matching row highlights in blue
```

**Features:**
- 500-row history buffer
- Automatic scrolling
- Timestamped entries
- Multi-parameter display

---

## 💾 Data Logging

### Configuration

Navigate to **Data Logging → Configure Logging...**

**Settings:**

| Setting | Description | Options |
|---------|-------------|---------|
| **Format** | Output file format | CSV, JSON |
| **File Path** | Output location | Auto-generated or custom |
| **Parameters** | Data to log | Select from configured parameters |
| **Buffer Size** | Entries before disk write | 10-1000 |

### Format Comparison

#### CSV Format

**Advantages:**
- Easy to import into Excel, MATLAB, Python
- Human-readable
- Widely supported

**Structure:**
```csv
timestamp,elapsed_time,temp_sensor_Temperature,humidity_Humidity
2025-01-15 10:30:00.123,0.000,23.500,65.200
2025-01-15 10:30:01.223,1.100,23.600,65.100
```

#### JSON Format

**Advantages:**
- Structured data format
- Easy to parse programmatically
- Self-documenting

**Structure:**
```json
{"timestamp": "2025-01-15T10:30:00.123", "elapsed_time": 0.0, "parameters": {"temp_sensor": 23.5, "humidity": 65.2}}
{"timestamp": "2025-01-15T10:30:01.223", "elapsed_time": 1.1, "parameters": {"temp_sensor": 23.6, "humidity": 65.1}}
```

### Buffer Size Guidelines

| Data Rate | Recommended Buffer | Write Frequency |
|-----------|-------------------|-----------------|
| 1-10 Hz | 100 | Every 10-100 sec |
| 10-50 Hz | 200-500 | Every 4-50 sec |
| 50-100 Hz | 500-1000 | Every 10-20 sec |
| 100+ Hz | 1000 | Every 10 sec |

**Tradeoffs:**
- **Larger buffer**: Less disk I/O, higher memory usage, more data lost if crash
- **Smaller buffer**: More frequent writes, lower memory, safer

---

## ⚙️ Configuration

### Project File Structure

Project files (`.json`) contain complete dashboard state:

```json
{
  "version": "1.0",
  "created": "2025-01-15T10:30:00",
  "parameters": [
    {
      "id": "temp_sensor",
      "name": "Temperature",
      "array_index": 0,
      "unit": "°C",
      "threshold": {
        "low_crit": -10,
        "low_warn": 0,
        "high_warn": 80,
        "high_crit": 100
      }
    }
  ],
  "connection_settings": {
    "mode": "serial",
    "serial_port": "COM4",
    "baudrate": 115200,
    "data_format": "json_array"
  },
  "layout": {
    "Main View": {
      "configs": {
        "widget_id": {
          "displayType": "Time Graph",
          "param_ids": ["temp_sensor"]
        }
      }
    }
  },
  "logging_settings": {
    "format": "csv",
    "selected_params": ["temp_sensor"],
    "buffer_size": 100
  }
}
```

### Data Format Examples

#### JSON Array
```json
[23.5, 65.2, 1013.25, 9.8, 0.5, -1.2, 12.3, 45.6]
```

#### CSV
```
23.5,65.2,1013.25,9.8,0.5,-1.2,12.3,45.6
```

#### Raw Bytes (Binary)
```
Configure:
  Sample Width: 2 bytes
  Endianness: little
  Channel Count: 8

Incoming: 0x17 0x5C 0x04 0x19 ...
Parsed: [23.5, 65.2, ...]
```

---

## 🔧 Troubleshooting

### Quick Diagnostic Checklist

```
☐ Connection shows "Connected"
☐ Stream shows "STREAMING" (not paused)
☐ Parameters properly configured
☐ Array indices correct
☐ Data format matches device
☐ Check Raw Telemetry Monitor
☐ Verify firewall settings
☐ Check cable connections
```

### Common Issues

<details>
<summary><b>Serial Port Not Detected</b></summary>

**Solutions:**
1. Click "Refresh" button in port selection
2. On Linux: `sudo usermod -a -G dialout $USER` (logout/login required)
3. On Windows: Check Device Manager for COM port number
4. Verify USB cable supports data (not just charging)
5. Try different USB port
6. Reinstall device drivers

</details>

<details>
<summary><b>No Data Appearing</b></summary>

**Diagnostic Steps:**
1. Open **View → Raw Telemetry Monitor** to verify incoming packets
2. Check connection status indicator (should be green)
3. Verify stream is not paused
4. Check parameter array indices match data structure
5. Verify data format configuration
6. Test with dummy data mode first

</details>

<details>
<summary><b>High CPU/Memory Usage</b></summary>

**Optimizations:**
1. Reduce number of active widgets (remove unused)
2. Increase data logging buffer size
3. Use simpler widget types (Value Cards vs Graphs)
4. Close unused tabs
5. Limit graph history depth
6. Reduce data rate if possible

</details>

<details>
<summary><b>Data Logging Not Working</b></summary>

**Checklist:**
1. Configure logging first (**Data Logging → Configure**)
2. Select at least one parameter
3. Check write permissions to output directory
4. Verify sufficient disk space
5. Close log file if open in another program
6. Stop logging to flush buffer before checking file

</details>

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Port access denied` | Insufficient permissions | Linux: add user to dialout group<br>Windows: close other programs using port |
| `Connection refused` | Server not listening | Verify IP/port, check firewall |
| `Module not found` | Missing dependency | Run `pip install -r requirements.txt` |
| `Invalid data format` | Format mismatch | Check device output format, adjust settings |

---

## 👨‍💻 Development

### Project Structure

```
Dashboard-Builder/
├── main.py                      # Application entry point
├── backend.py                   # Data reader and parser
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation
├── LICENSE                      # GPL v3.0 license
├── app/
│   ├── __init__.py
│   ├── widgets.py               # Widget implementations
│   ├── dialogs.py               # Dialog windows
│   └── ui/
│       ├── __init__.py
│       └── main_window.py       # Main window
├── public/
│   ├── Glance_nobg.png          # App logo
│   └── ign_logo_wht.png         # Team logo
├── examples/
│   └── preset1.json             # Example configuration
└── Documentation/
    └── index.html               # Built-in documentation
```

### Adding Custom Widgets

1. **Create widget class** in `app/widgets.py`:

```python
class CustomWidget(QWidget):
    def __init__(self, param_config):
        super().__init__()
        self.param = param_config
        # Initialize UI
    
    def update_value(self, value):
        # Update display with new data
        pass
```

2. **Register in `AddWidgetDialog`** (`app/dialogs.py`)

3. **Add handler** in `MainWindow.add_widget_to_dashboard()` (`main.py`)

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build Windows executable
pyinstaller --onefile --windowed --name "Dashboard Builder" \
    --icon=public/Glance_nobg.png \
    --add-data "public:public" \
    --add-data "Documentation:Documentation" \
    main.py

# Output in dist/ directory
```

### Code Style

- **PEP 8** compliance
- Type hints where applicable
- Docstrings for public methods
- Descriptive variable names

### Testing

```bash
# Run with dummy data for testing
python main.py
# Select "dummy" mode in connection settings
```

---

## 🏆 About Team Ignition

<div align="center">

![Team Ignition Logo](public/ign_logo_wht.png)

**Official Student Rocketry Team**  
Vellore Institute of Technology, Chennai

</div>

### Our Mission

Team Ignition is dedicated to advancing aerospace innovation through hands-on learning and experimentation. We design, build, and launch experimental rockets while developing every subsystem in-house — from **propulsion and avionics to recovery systems and ground-support equipment**.

### What We Do

- 🚀 **Design & Launch** model and experimental rockets
- 🔧 **Develop In-House** propulsion, avionics, payloads, and recovery systems
- 🏅 **Compete** in national and international rocketry competitions
- 📚 **Educate** through workshops, seminars, and outreach programs
- 💡 **Innovate** with cutting-edge aerospace technology

### Our Projects

- Solid and hybrid rocket motor development
- Flight computers and telemetry systems
- CubeSat and CanSat payloads
- Ground-support software applications
- Launch pad and recovery systems

### Connect With Us

<div align="center">

[![Website](https://img.shields.io/badge/Website-teamignition.space-blue?style=for-the-badge)](https://teamignition.space)
[![GitHub](https://img.shields.io/badge/GitHub-teamignitionvitc-black?style=for-the-badge&logo=github)](https://github.com/teamignitionvitc)
[![Twitter](https://img.shields.io/badge/Twitter-@ignitiontech23-blue?style=for-the-badge&logo=twitter)](https://x.com/ignitiontech23)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Team%20Ignition-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/teamignition/)
[![Instagram](https://img.shields.io/badge/Instagram-@ignition__vitc-E4405F?style=for-the-badge&logo=instagram)](https://www.instagram.com/ignition_vitc)

</div>

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** with additional restrictions.

### Additional Restriction

⚠️ **This software may not be used for commercial purposes without explicit written permission from the authors (Team Ignition Software Department).**

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

## 🤝 Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or testing — your help is valuable.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Contribution Guidelines

- Follow existing code style (PEP 8)
- Add tests for new features
- Update documentation as needed
- Write clear commit messages
- Keep pull requests focused

### Reporting Issues

Please report issues on GitHub with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Relevant logs/screenshots

---

## 📞 Support

### Getting Help

1. **Check Documentation**: Read this README and built-in docs
2. **Search Issues**: Look for similar problems on GitHub
3. **Ask Community**: Open a GitHub discussion
4. **Report Bugs**: Create a new issue with details

### Issue Template

```markdown
**System Information:**
- OS: Windows 11 / Ubuntu 22.04 / macOS 12
- Python Version: 3.10.5
- Application Version: 2.0.0

**Description:**
Clear description of the issue

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Screenshots/Logs:**
Attach relevant files
```

---

## 🙏 Acknowledgments

- Built with **PySide6** (Qt6) for professional UI
- Plotting powered by **pyqtgraph** for high performance
- Serial communication via **pyserial**
- Developed by **Team Ignition Software Department**
- Tested during rocket ground operations by Team Ignition

---

## 📊 Version History

### v2.0.0 (Current Release)

**Major Improvements:**
- ✨ Complete UI/UX redesign with 4-phase wizard
- 🔧 Enhanced parameter management system
- 💾 Comprehensive data logging (CSV/JSON)
- 📡 Raw telemetry monitor
- 📊 Real-time connection status monitoring
- 🎨 Professional dark theme
- ⚡ Performance optimizations
- 🔍 Better error handling and validation
- 📝 Dashboard title customization
- 🌐 Improved GPS mapping

### v1.0.0 (Initial Release)

- Basic dashboard functionality
- Serial and network data sources
- Core widget types (graphs, gauges, tables)
- Simple parameter configuration
- Project save/load

---

<div align="center">

### ⭐ Star this repository if you find it useful!

**Dashboard Builder** - Professional telemetry visualization by Team Ignition  
*Advancing aerospace innovation through software excellence*

---

Made with ❤️ by Team Ignition Software Department

[Report Bug](https://github.com/teamignitionvitc/Dashboard-Builder/issues) • [Request Feature](https://github.com/teamignitionvitc/Dashboard-Builder/issues) • [Documentation](https://glance.teamignition.space/)

</div>