<div align="center">

<img src="docs/public/Glance.png" alt="Glance Logo" width="400"/>


<h3>Professional Real-Time Telemetry Visualization Platform</h3>

<p>
  <img src="https://img.shields.io/badge/License-GPLv3%20with%20restrictions-blue.svg" alt="License"/>
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python Version"/>
  <img src="https://img.shields.io/badge/GUI-PySide6-green" alt="PySide6"/>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Platform"/>
</p>

<p><em>Data visualization dashboard for monitoring real-time sensor data, telemetry streams, and system metrics</em></p>

<p>
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="https://glance.teamignition.space/">Documentation</a> •
  <a href="#contributing">Contributing</a>
</p>

<hr/>

<img src="docs/public/ign_logo_wht.png" alt="Team Ignition Logo" width="150"/>

<p><strong>Developed by Team Ignition Software Department</strong><br/>
<em>Official Model Rocketry Team of Vellore Institute of Technology, Chennai</em></p>

</div>

---

## About

<table>
<tr>
<td width="60%">

**Glance** is a real-time telemetry visualization platform designed for rockets, drones, embedded systems, and advanced data-acquisition applications. Built with PySide6 (Qt6), it offers a modular, widget-based dashboard that adapts to diverse telemetry needs.

With multi-source connectivity, advanced signal filtering, powerful data logging, and professional UI/UX, Glance empowers engineers, researchers, and operators to gain actionable insights at a glance.

</td>
<td width="40%">

### Core Capabilities

<ul>
<li>Real-time multi-channel visualization</li>
<li>Serial, TCP, UDP connectivity</li>
<li>Advanced signal filtering (Kalman, Moving Average, Low-pass, Median)</li>
<li>7+ customizable widget types</li>
<li>CSV & JSON data logging</li>
<li>Professional dark theme UI</li>
<li>Project save/load system</li>
<li>Raw telemetry monitoring</li>
</ul>

</td>
</tr>
</table>

---

## Features

<details open>
<summary><h3>📊 Visualization & Display</h3></summary>

<table>
<tr>
<td width="50%">

**Interactive Graphs**
- Multi-parameter time-series plotting
- Zoom, pan, and crosshair inspection
- Auto-scaling with manual override
- Color-coded parameter traces
- Real-time legend updates

**Status Displays**
- Large-format value cards with alarm states
- Circular gauges with threshold zones
- LED indicators with color-coded status
- Statistical histograms for distribution analysis

</td>
<td width="50%">

**Data Tables & GPS**
- Searchable log tables with highlighting
- Timestamped data entries
- Multi-parameter comparison
- GPS mapping with satellite imagery
- Real-time location tracking
- Interactive map controls

**Advanced Features**
- Crosshair cursor with value readout
- Mouse-click data point selection
- Widget floating and docking
- Multi-tab dashboard support

</td>
</tr>
</table>

</details>

<details>
<summary><h3>🎛️ Signal Processing</h3></summary>

<table>
<tr>
<td width="50%">

**Available Filters**

<dl>
<dt><strong>Kalman Filter</strong></dt>
<dd>Optimal estimation for noisy signals with configurable process and measurement variance. Ideal for tracking applications and sensor fusion.</dd>

<dt><strong>Moving Average Filter</strong></dt>
<dd>Simple smoothing over configurable window size (2-100 samples). Effective for reducing random noise.</dd>

<dt><strong>Low-Pass Filter</strong></dt>
<dd>Exponential smoothing with adjustable alpha (0.01-1.0). Fast response with controllable lag.</dd>

<dt><strong>Median Filter</strong></dt>
<dd>Outlier rejection using median of N samples. Excellent for spike removal while preserving edges.</dd>
</dl>

</td>
<td width="50%">

**Filter Management**

- Per-parameter filter chains
- Enable/disable filters without restart
- Real-time filter parameter adjustment
- Filter state reset capability
- Visual filter status indicators
- Import/export filter configurations

**Processing Features**

- Apply filters to any parameter
- Chain multiple filters per parameter
- Raw and filtered data logging
- Zero-lag display options
- Configurable buffer management

</td>
</tr>
</table>

</details>

<details>
<summary><h3>🔌 Connectivity & Data Sources</h3></summary>

<table>
<tr>
<td width="50%">

**Serial Communication**
- RS232, RS485, USB-Serial support
- Auto-detection of available ports
- Configurable baudrate (300-10M)
- Manual refresh of port list
- Timeout configuration

**Network Protocols**
- TCP client connections
- UDP listener mode
- Configurable host and port
- Connection status monitoring
- Automatic reconnection

</td>
<td width="50%">

**Data Format Support**
- JSON array parsing
- CSV delimited data
- Raw binary bytes
- Bit-level data extraction
- Custom format definitions
- Little/big endian support
- Configurable channel count (1-1024)

**Simulation Mode**
- Built-in dummy data generator
- No hardware required for testing
- Configurable sine wave patterns
- Random noise injection

</td>
</tr>
</table>

</details>

<details>
<summary><h3>💾 Data Logging & Export</h3></summary>

<table>
<tr>
<td width="50%">

**Logging Features**
- CSV and JSON format support
- Parameter-selective logging
- Configurable buffer sizes (10-1000)
- Auto-generated timestamped filenames
- Manual buffer flush controls
- Organized logs directory structure

**Data Management**
- Raw and filtered value storage
- Millisecond-precision timestamps
- Elapsed time tracking
- Incremental file writing
- Low memory footprint

</td>
<td width="50%">

**Export Options**
- Standard CSV for Excel/MATLAB
- JSON Lines format for programming
- Human-readable timestamps
- Parameter metadata inclusion
- Configurable write frequency

**Performance**
- Buffered I/O for efficiency
- Configurable flush intervals
- Background writing
- No dropped packets during logging
- Minimal CPU overhead

</td>
</tr>
</table>

</details>

<details>
<summary><h3>🔍 Monitoring & Debugging</h3></summary>

<table>
<tr>
<td width="50%">

**Raw Telemetry Monitor**
- Decimal, hexadecimal, ASCII, binary, and mixed display modes
- Real-time packet inspection
- Packet statistics (count, rate, bytes)
- Pause and resume capability
- Search and highlight functionality
- Screenshot capture
- Save to file

**VS Code-like Status Bar**
- Segmented layout for clear information hierarchy
- Live clock display
- Connection status with interactive button
- Packet count and data received metrics
- Active parameters and widget count
- UI update rate (FPS)
- Data logging indicator
- Quick access to Raw Telemetry viewer

</td>
<td width="50%">

**Debug Tools**
- Connection diagnostics
- Data format validation
- Parameter mapping verification
- Real-time packet rate monitoring
- Error message display
- Connection retry logic

**Advanced Telemetry**
- Multiple display format switching
- Packet numbering
- Timestamp display options
- Byte rate calculation
- Error counting
- Custom search filters

</td>
</tr>
</table>

</details>

<details>
<summary><h3>🎨 User Interface</h3></summary>

<table>
<tr>
<td width="50%">

**Modern Design**
- Professional "Apple-like" dark theme
- High-contrast elements with SF Pro typography
- Custom styled widgets with glassmorphism effects
- Smooth animations and transitions
- Gradient accents and refined color palettes
- Responsive layout with segmented controls

**Dashboard Management**
- 4-phase creation wizard
- Professional Welcome Screen with system icons
- Setup wizard with validation
- Widget pre-configuration
- Live dashboard phase

</td>
<td width="50%">

**Layout Control**
- Drag-and-drop widget positioning
- Floating and docked modes
- Multi-tab support with rename
- Tile evenly function
- Right-click context menus
- Widget resize and minimize
- Customizable dashboard titles

**Workflow**
- Project save/load system
- Unsaved changes tracking
- Configuration validation
- Error prevention dialogs
- Keyboard shortcut support

</td>
</tr>
</table>

</details>

<details>
<summary><h3>⚙️ Technical Architecture</h3></summary>

<table>
<tr>
<td width="50%">

**Backend Core**
- **Threaded Acquisition**: `DataSimulator` runs in a dedicated `QThread`, ensuring the UI remains responsive even at high data rates (100Hz+).
- **Abstraction Layer**: `DataReader` provides a unified interface for Serial, TCP, and UDP sources, handling low-level socket/port management and error recovery.
- **Binary Parsing**: Uses Python's `struct` module for high-performance parsing of binary packets. Supports mixed data types (int, float, double) and bit-fields defined via user configuration.

**Data Flow**
1. **Source**: Hardware/Network sends data packet.
2. **Acquisition**: `DataReader` reads bytes/string.
3. **Parsing**: Data is converted to a normalized `list[float]`.
4. **Distribution**: `DataSimulator` emits `newData` Qt Signal.
5. **Processing**: Main thread applies active filters (Kalman/MA).
6. **Visualization**: Widgets update via optimized paint events.

</td>
<td width="50%">

**Data Logging Internals**
- **Buffered I/O**: `DataLogger` accumulates data in memory (default 100 samples) before performing a bulk write to disk. This minimizes filesystem overhead and prevents write-latency from affecting the acquisition loop.
- **Formats**:
  - **CSV**: Optimized for import into Excel/MATLAB.
  - **JSON Lines**: Stream-friendly format for programmatic analysis.

**Signal Processing**
- **Filter Chain**: Filters are implemented as independent objects inheriting from `SignalFilter`.
- **State Management**: Filters maintain their own internal state (buffers, covariance matrices) which persists across updates but can be reset dynamically.
- **Real-time**: All filtering occurs in the main event loop, designed for low-latency (<1ms) processing per packet.

</td>
</tr>
</table>

</details>

---

## Screenshots

<div align="center">

<table>
<tr>
<td width="50%">
<img src="docs/public/Doc%20Images/HomeScreen.png" alt="Welcome Screen"/>
<p><em>Modern welcome screen with quick-start options</em></p>
</td>
<td width="50%">
<img src="docs/public/Doc%20Images/Connection.png" alt="Connection Settings"/>
<p><em>Flexible data source configuration</em></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/public/Doc%20Images/parameters.png" alt="Parameter Management"/>
<p><em>Parameter configuration with array index mapping</em></p>
</td>
<td width="50%">
<img src="docs/public/Doc%20Images/logging.png" alt="Data Logging"/>
<p><em>Comprehensive data logging with format selection</em></p>
</td>
</tr>
<tr>
<td colspan="2">
<img src="docs/public/Doc%20Images/dashboard.png" alt="Dashboard View"/>
<p><em>Real-time multi-widget dashboard layout</em></p>
</td>
</tr>
</table>

</div>

---

## System Requirements

<table>
<tr>
<td width="50%">

### Minimum

<table>
<tr><th>Component</th><th>Requirement</th></tr>
<tr><td>Operating System</td><td>Windows 10/11<br/>Linux (Ubuntu 20.04+)<br/>macOS 10.15+</td></tr>
<tr><td>Python</td><td>3.8 or higher</td></tr>
<tr><td>RAM</td><td>4 GB</td></tr>
<tr><td>Display</td><td>1280x720</td></tr>
<tr><td>Storage</td><td>500 MB free</td></tr>
</table>

</td>
<td width="50%">

### Recommended

<table>
<tr><th>Component</th><th>Requirement</th></tr>
<tr><td>Operating System</td><td>Windows 11<br/>Linux (Ubuntu 22.04+)<br/>macOS 12+</td></tr>
<tr><td>Python</td><td>3.10 or higher</td></tr>
<tr><td>RAM</td><td>8 GB or more</td></tr>
<tr><td>Display</td><td>1920x1080 or higher</td></tr>
<tr><td>Storage</td><td>1 GB+ for logging</td></tr>
</table>

</td>
</tr>
</table>

---

## Installation

### Method 1: Download & Run (Recommended)

The easiest way to use Glance is to download the standalone executable for your system. No Python installation required.

| Platform | Download | Release Notes |
|----------|----------|---------------|
| **Windows** | [![Windows](https://img.shields.io/badge/Windows-Download_.exe-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/teamignitionvitc/Glance/releases/download/v1.0.0-alpha.1/Glance_Setup_Windows_v1.exe) | [v1.0.0-alpha.1](https://github.com/teamignitionvitc/Glance/releases/tag/v1.0.0-alpha.1) |
| **Linux** | [![Linux](https://img.shields.io/badge/Linux-Download_.tar.gz-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/teamignitionvitc/Glance/releases/download/v1.0.0-alpha.1/Glance_Linux_x64.tar.gz) | [v1.0.0-alpha.1](https://github.com/teamignitionvitc/Glance/releases/tag/v1.0.0-alpha.1) |

> **📘 Full Documentation:** For detailed setup guides and troubleshooting, see the [Official Documentation](docs/index.html).

### Method 2: Build from Source (Developers)

<details>
<summary><h3>Standard Installation</h3></summary>

```bash
# Clone the repository
git clone https://github.com/teamignitionvitc/Glance.git
cd Glance

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

</details>

<details>
<summary><h3>Virtual Environment (Recommended)</h3></summary>

```bash
# Clone repository
git clone https://github.com/teamignitionvitc/Glance.git
cd Glance

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

</details>

### Dependencies

<table>
<tr>
<td width="50%">

**Required**

```
PySide6>=6.4.0          # Qt6 UI framework
pyqtgraph>=0.13.0       # High-performance plotting
numpy>=1.21.0           # Numerical computing
pyserial>=3.5           # Serial communication
```

</td>
<td width="50%">

**Optional**

```
PySide6-WebEngine       # GPS map widgets
```

**Installation:**
```bash
pip install PySide6-WebEngine
```

</td>
</tr>
</table>

---

## Quick Start

<details open>
<summary><h3>1. Launch Application</h3></summary>

```bash
python main.py
```

</details>

<details>
<summary><h3>2. Choose Your Path</h3></summary>

<table>
<tr>
<td width="50%">

**First-Time Users**

1. Click **"Create New Dashboard"**
2. Follow the 4-phase wizard:
   - **Setup**: Configure connection
   - **Parameters**: Define data channels
   - **Widgets**: Pre-configure displays
   - **Dashboard**: Live monitoring

</td>
<td width="50%">

**Returning Users**

1. Click **"Load Project..."**
2. Select your `.json` configuration
3. Dashboard loads with:
   - Previous layout
   - Connection settings
   - Filter configurations
   - Logging preferences

</td>
</tr>
</table>

</details>

<details>
<summary><h3>3. Configure Connection</h3></summary>

<table>
<tr>
<th>Mode</th>
<th>Configuration</th>
</tr>
<tr>
<td><strong>Dummy (Testing)</strong></td>
<td>

```
Connection Mode: dummy
Data Format: json_array
Channel Count: 32
```

No hardware required

</td>
</tr>
<tr>
<td><strong>Serial</strong></td>
<td>

```
Connection Mode: serial
Serial Port: COM4 (auto-detected)
Baudrate: 115200
Data Format: json_array
Channel Count: 32
```

Use Refresh button to update port list

</td>
</tr>
<tr>
<td><strong>TCP/UDP</strong></td>
<td>

```
Connection Mode: tcp (or udp)
Host: 192.168.1.100
Port: 9000
Data Format: json_array
Channel Count: 32
```

Verify firewall settings

</td>
</tr>
</table>

</details>

<details>
<summary><h3>4. Define Parameters</h3></summary>

Navigate to **Edit → Manage Parameters** or press **Ctrl+P**

<table>
<tr>
<th>Property</th>
<th>Description</th>
<th>Example</th>
</tr>
<tr>
<td><strong>ID</strong></td>
<td>Unique identifier (no spaces)</td>
<td><code>temp_sensor</code></td>
</tr>
<tr>
<td><strong>Name</strong></td>
<td>Display name</td>
<td><code>Temperature</code></td>
</tr>
<tr>
<td><strong>Array Index</strong></td>
<td>Position in data packet (0-based)</td>
<td><code>0</code></td>
</tr>
<tr>
<td><strong>Sensor Group</strong></td>
<td>Category</td>
<td><code>Environmental</code></td>
</tr>
<tr>
<td><strong>Unit</strong></td>
<td>Measurement unit</td>
<td><code>°C</code></td>
</tr>
<tr>
<td><strong>Thresholds</strong></td>
<td>Alarm levels (ascending order)</td>
<td>Low Crit: -10<br/>Low Warn: 0<br/>High Warn: 80<br/>High Crit: 100</td>
</tr>
</table>

**Key Concept**: Array Index maps each parameter to a position in your incoming data array.

Example: If device sends `[23.5, 65.2, 1013.25, ...]`:
- Index 0 = Temperature (23.5)
- Index 1 = Humidity (65.2)
- Index 2 = Pressure (1013.25)

</details>

<details>
<summary><h3>5. Add Signal Filters (Optional)</h3></summary>

Navigate to **Filters → Add Filter to Parameter**

<table>
<tr>
<th>Filter Type</th>
<th>Use Case</th>
<th>Configuration</th>
</tr>
<tr>
<td><strong>Moving Average</strong></td>
<td>General smoothing</td>
<td>Window Size: 5-20</td>
</tr>
<tr>
<td><strong>Low Pass</strong></td>
<td>Fast response smoothing</td>
<td>Alpha: 0.3 (lower = smoother)</td>
</tr>
<tr>
<td><strong>Kalman</strong></td>
<td>Optimal estimation</td>
<td>Process Var: 0.01<br/>Measurement Var: 0.1</td>
</tr>
<tr>
<td><strong>Median</strong></td>
<td>Outlier rejection</td>
<td>Window Size: 5-11 (odd)</td>
</tr>
</table>

Filters can be chained and toggled without restarting.

</details>

<details>
<summary><h3>6. Add Widgets</h3></summary>

Click **"Add Widget..."** or press **Ctrl+W**

<table>
<tr>
<th>Widget Type</th>
<th>Parameters</th>
<th>Best For</th>
</tr>
<tr>
<td>Value Card</td>
<td>1+</td>
<td>Multiple critical values</td>
</tr>
<tr>
<td>Time Graph</td>
<td>1+</td>
<td>Trend analysis</td>
</tr>
<tr>
<td>Gauge</td>
<td>1</td>
<td>Visual range indication</td>
</tr>
<tr>
<td>Histogram</td>
<td>1</td>
<td>Distribution analysis</td>
</tr>
<tr>
<td>LED Indicator</td>
<td>1+</td>
<td>Multi-status monitoring with per-parameter thresholds</td>
</tr>
<tr>
<td>Log Table</td>
<td>1+</td>
<td>Detailed inspection</td>
</tr>
<tr>
<td>Map</td>
<td>2 (Lat, Lon)</td>
<td>GPS tracking</td>
</tr>
</table>

**Widget Management**:
- Right-click for context menu
- Rename, Float/Dock, Close options
- Tile Evenly for auto-arrangement

</details>

<details>
<summary><h3>7. Start Data Logging</h3></summary>

Navigate to **Data Logging → Configure Logging...** or press **Ctrl+L**

<table>
<tr>
<th>Setting</th>
<th>Options</th>
<th>Recommendation</th>
</tr>
<tr>
<td>Format</td>
<td>CSV, JSON</td>
<td>CSV for Excel/MATLAB<br/>JSON for programming</td>
</tr>
<tr>
<td>Parameters</td>
<td>Select from list</td>
<td>Choose relevant parameters only</td>
</tr>
<tr>
<td>Buffer Size</td>
<td>10-1000</td>
<td>100 for most applications</td>
</tr>
<tr>
<td>File Path</td>
<td>Auto or custom</td>
<td>Auto-generated in logs/ folder</td>
</tr>
</table>

Start logging with **Ctrl+Shift+L**, stop with **Ctrl+Alt+L**

</details>

<details>
<summary><h3>8. Monitor Raw Data</h3></summary>

Open **View → Raw Telemetry Monitor** or press **Ctrl+M**

<table>
<tr>
<th>Display Mode</th>
<th>Format</th>
<th>Use Case</th>
</tr>
<tr>
<td><strong>Decimal</strong></td>
<td>`[12, 255, 0]`</td>
<td>Standard byte values</td>
</tr>
<tr>
<td><strong>Hex</strong></td>
<td>`0C FF 00`</td>
<td>Protocol debugging</td>
</tr>
<tr>
<td><strong>ASCII</strong></td>
<td>`...`</td>
<td>Text-based protocols</td>
</tr>
<tr>
<td><strong>Binary</strong></td>
<td>`00001100 ...`</td>
<td>Bit-level analysis</td>
</tr>
</table>

</details>

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

Distributed under the **GNU General Public License v3.0**. See `LICENSE` for more information.

---

<div align="center">
<p>Copyright © 2025 Team Ignition Software Department</p>
</div>