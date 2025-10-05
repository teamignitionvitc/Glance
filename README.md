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

**Status Bar Metrics**
- Live clock display
- Connection status with details
- Stream status (streaming/paused)
- Packet count and rate
- Total data received
- Session uptime
- Data logging indicator

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
- Professional dark theme
- High-contrast elements
- Custom styled widgets
- Smooth animations
- Gradient accents
- Responsive layout

**Dashboard Management**
- 4-phase creation wizard
- Welcome screen with quick actions
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
<img src="docs/public/Doc%20Images/dashboard.png" alt="Dashboard View"/>
<p><em>Real-time multi-widget dashboard layout</em></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/public/Doc%20Images/parameters.png" alt="Parameter Management"/>
<p><em>Parameter configuration with array index mapping</em></p>
</td>
<td width="50%">
<img src="docs/public/Doc%20Images/Connection.png" alt="Connection Settings"/>
<p><em>Flexible data source configuration</em></p>
</td>
</tr>
<tr>
<td colspan="2">
<img src="docs/public/Doc%20Images/logging.png" alt="Data Logging"/>
<p><em>Comprehensive data logging with format selection</em></p>
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

<details open>
<summary><h3>Method 1: Standard Installation</h3></summary>

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
<summary><h3>Method 2: Virtual Environment (Recommended)</h3></summary>

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
<td>1</td>
<td>Critical single values</td>
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
<td>1</td>
<td>Status monitoring</td>
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
<td>Decimal</td>
<td>Floating-point numbers</td>
<td>Standard viewing</td>
</tr>
<tr>
<td>Hexadecimal</td>
<td>Byte values (00-FF)</td>
<td>Binary debugging</td>
</tr>
<tr>
<td>ASCII</td>
<td>Text characters</td>
<td>Text protocols</td>
</tr>
<tr>
<td>Binary</td>
<td>Bit patterns</td>
<td>Low-level inspection</td>
</tr>
<tr>
<td>Mixed</td>
<td>Hex + ASCII</td>
<td>Comprehensive view</td>
</tr>
</table>

Features: Pause, search, save to file, screenshot

</details>

<details>
<summary><h3>9. Save Your Work</h3></summary>

**File → Save Project** or press **Ctrl+S**

Saved configuration includes:
- Parameter definitions and array mappings
- Signal filter configurations
- Connection settings
- Dashboard layout and widget positions
- Data logging preferences
- Dashboard title and customization

</details>

---

## Signal Filtering

<div align="center">
<h3>Industry-Standard Signal Processing Filters</h3>
<p><em>Clean noisy telemetry data with four configurable filter types</em></p>
</div>

<details>
<summary><h3>Moving Average Filter</h3></summary>

<table>
<tr>
<td width="40%">

**Overview**

General-purpose smoothing filter that averages the last N samples. Simple, effective, and easy to understand.

**Formula**

`y[n] = (x[n] + x[n-1] + ... + x[n-k+1]) / k`

where k = window size

</td>
<td width="60%">

**Configuration**

<table>
<tr><th>Parameter</th><th>Range</th><th>Effect</th></tr>
<tr><td>Window Size</td><td>2-100</td><td>Larger = smoother but more lag</td></tr>
</table>

**Recommended Settings**

<table>
<tr><th>Application</th><th>Window Size</th></tr>
<tr><td>Light smoothing</td><td>3-5</td></tr>
<tr><td>Moderate smoothing</td><td>10-20</td></tr>
<tr><td>Heavy smoothing</td><td>30-50</td></tr>
</table>

**Tradeoffs**

- ✓ Simple and predictable
- ✓ Effective for random noise
- ✗ Introduces lag
- ✗ Not optimal for all noise types

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Low-Pass Filter</h3></summary>

<table>
<tr>
<td width="40%">

**Overview**

Exponential smoothing filter with fast response and controllable lag. Single previous value storage makes it very efficient.

**Formula**

`y[n] = α × x[n] + (1-α) × y[n-1]`

where α = smoothing factor

</td>
<td width="60%">

**Configuration**

<table>
<tr><th>Parameter</th><th>Range</th><th>Effect</th></tr>
<tr><td>Alpha (α)</td><td>0.01-1.0</td><td>Lower = smoother, higher = faster</td></tr>
</table>

**Recommended Settings**

<table>
<tr><th>Application</th><th>Alpha Value</th></tr>
<tr><td>Light smoothing</td><td>0.7-0.9</td></tr>
<tr><td>Moderate smoothing</td><td>0.3-0.6</td></tr>
<tr><td>Heavy smoothing</td><td>0.05-0.2</td></tr>
</table>

**Tradeoffs**

- ✓ Very efficient (low memory)
- ✓ Adjustable response vs. smoothing
- ✗ Less effective than Kalman for complex noise
- ✗ Can't adapt to changing signal

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Kalman Filter</h3></summary>

<table>
<tr>
<td width="40%">

**Overview**

Optimal estimator for linear systems with Gaussian noise. Provides best balance between smoothing and responsiveness while adapting to signal dynamics.

**Characteristics**

- Optimal for many real-world applications
- Adapts to signal dynamics
- Provides estimate and uncertainty
- Industry standard for tracking

</td>
<td width="60%">

**Configuration**

<table>
<tr><th>Parameter</th><th>Range</th><th>Effect</th></tr>
<tr><td>Process Variance (Q)</td><td>0.001-10.0</td><td>Expected system noise</td></tr>
<tr><td>Measurement Variance (R)</td><td>0.001-10.0</td><td>Expected sensor noise</td></tr>
</table>

**Recommended Settings**

<table>
<tr><th>Scenario</th><th>Q Value</th><th>R Value</th></tr>
<tr><td>Low sensor noise</td><td>0.01</td><td>0.1</td></tr>
<tr><td>Moderate noise</td><td>0.05</td><td>0.5</td></tr>
<tr><td>High sensor noise</td><td>0.1</td><td>1.0</td></tr>
</table>

**Tuning Guide**

- Lower R = trust sensor more
- Lower Q = trust model more
- R/Q ratio controls smoothing vs. responsiveness

**Tradeoffs**

- ✓ Optimal estimation
- ✓ Balances responsiveness and smoothing
- ✓ Provides confidence estimates
- ✗ More complex to tune
- ✗ Slightly higher computational cost

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Median Filter</h3></summary>

<table>
<tr>
<td width="40%">

**Overview**

Non-linear filter that replaces each value with the median of surrounding samples. Excellent for removing outliers while preserving edges.

**Formula**

`y[n] = median(x[n-k/2], ..., x[n], ..., x[n+k/2])`

where k = window size

</td>
<td width="60%">

**Configuration**

<table>
<tr><th>Parameter</th><th>Range</th><th>Effect</th></tr>
<tr><td>Window Size</td><td>3-101 (odd)</td><td>Larger = more aggressive filtering</td></tr>
</table>

**Recommended Settings**

<table>
<tr><th>Application</th><th>Window Size</th></tr>
<tr><td>Light filtering</td><td>3-5</td></tr>
<tr><td>Moderate filtering</td><td>7-11</td></tr>
<tr><td>Heavy filtering</td><td>15-25</td></tr>
</table>

**Tradeoffs**

- ✓ Excellent spike/outlier removal
- ✓ Preserves edges and sharp transitions
- ✓ Non-linear (doesn't blur edges)
- ✗ Higher computational cost
- ✗ Can distort rapid but legitimate changes

</td>
</tr>
</table>

</details>

### Filter Management

<table>
<tr>
<td width="50%">

**Adding Filters**

1. Navigate to **Filters → Add Filter to Parameter**
2. Select filter type from submenu
3. Choose target parameter
4. Configure filter parameters
5. Filter activates immediately

**Per-Parameter Chains**

- Apply multiple filters to one parameter
- Filters process in order added
- Each filter sees output of previous filter

</td>
<td width="50%">

**Managing Filters**

1. Open **Filters → Manage Filters...** (Ctrl+F)
2. View filter tree (all parameters and filters)
3. Enable/disable individual filters
4. Remove unwanted filters
5. Reset filter state (clear buffer)

**Import/Export**

- Save filter configurations as JSON
- Share filter setups between projects
- Quick setup for similar applications

</td>
</tr>
</table>

---

## Widget Types

<details>
<summary><h3>Value Card</h3></summary>

<table>
<tr>
<td width="40%">

<dl>
<dt><strong>Purpose</strong></dt>
<dd>Display single parameter with large numeric value and alarm state indication</dd>

<dt><strong>Parameters</strong></dt>
<dd>1 (single parameter only)</dd>

<dt><strong>Best For</strong></dt>
<dd>Critical parameters requiring constant monitoring</dd>
</dl>

</td>
<td width="60%">

**Features**

- Large numeric display
- Unit label
- Color-coded alarm states
- Priority border indicator

**Alarm States**

<table>
<tr><th>State</th><th>Color</th><th>Condition</th></tr>
<tr><td>Nominal</td><td style="background:#1a1a1a; color:#21b35a">Green</td><td>Within normal range</td></tr>
<tr><td>Warning</td><td style="background:#1a1a1a; color:#ffbf00">Yellow</td><td>Approaching limits</td></tr>
<tr><td>Critical</td><td style="background:#1a1a1a; color:#ff3131">Red</td><td>Exceeded safe limits</td></tr>
</table>

**Priority Levels**

- High: Red border (most important)
- Medium: Blue border
- Low: No border

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Time Graph</h3></summary>

<table>
<tr>
<td width="40%">

<dl>
<dt><strong>Purpose</strong></dt>
<dd>Multi-parameter line chart showing data trends over time</dd>

<dt><strong>Parameters</strong></dt>
<dd>1+ (supports multiple parameters)</dd>

<dt><strong>Best For</strong></dt>
<dd>Trend analysis and comparing related parameters</dd>
</dl>

</td>
<td width="60%">

**Features**

- Auto-assigned colors per parameter
- Interactive legend
- Zoom and pan controls
- Crosshair cursor with value readout
- Auto-scaling Y-axis
- Reset view button
- Mouse-click data point selection

**Keyboard Controls**

<table>
<tr><th>Action</th><th>Control</th></tr>
<tr><td>Zoom Y-axis only</td><td>Ctrl + Mouse Wheel</td></tr>
<tr><td>Zoom X-axis only</td><td>Shift + Mouse Wheel</td></tr>
<tr><td>Pan view</td><td>Right-click + Drag</td></tr>
<tr><td>Auto-scale</td><td>Double-click</td></tr>
</table>

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Gauge Widget</h3></summary>

<table>
<tr>
<td width="40%">

<dl>
<dt><strong>Purpose</strong></dt>
<dd>Visual representation with threshold zones and needle indicator</dd>

<dt><strong>Parameters</strong></dt>
<dd>1 (single parameter only)</dd>

<dt><strong>Best For</strong></dt>
<dd>Parameters with defined operational ranges</dd>
</dl>

</td>
<td width="60%">

**Features**

- Smooth needle animation
- Color-coded arc segments
- Current value display
- Min/max labels
- Threshold zone indicators

**Zone Colors**

<table>
<tr><th>Zone</th><th>Color</th><th>Range</th></tr>
<tr><td>Critical Low</td><td style="background:#1a1a1a; color:#ff3131">Red</td><td>Below low_crit</td></tr>
<tr><td>Low</td><td style="background:#1a1a1a; color:#0078ff">Blue</td><td>low_crit to low_warn</td></tr>
<tr><td>Normal</td><td style="background:#1a1a1a; color:#21b35a">Green</td><td>low_warn to high_warn</td></tr>
<tr><td>Warning</td><td style="background:#1a1a1a; color:#ffbf00">Yellow</td><td>high_warn to high_crit</td></tr>
<tr><td>Critical High</td><td style="background:#1a1a1a; color:#ff3131">Red</td><td>Above high_crit</td></tr>
</table>

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Histogram Widget</h3></summary>

<table>
<tr>
<td width="40%">

<dl>
<dt><strong>Purpose</strong></dt>
<dd>Statistical distribution visualization of parameter values</dd>

<dt><strong>Parameters</strong></dt>
<dd>1 (single parameter only)</dd>

<dt><strong>Best For</strong></dt>
<dd>Analyzing data distribution patterns and detecting anomalies</dd>
</dl>

</td>
<td width="60%">

**Features**

- 20-bin distribution display
- Auto-scaling axes
- Real-time updates
- Color-coded bars

**Use Cases**

- Verify sensor calibration
- Detect bimodal distributions
- Identify noise characteristics
- Quality control monitoring

</td>
</tr>
</table>

</details>

<details>
<summary><h3>LED Indicator</h3></summary>

<table>
<tr>
<td width="40%">

<dl>
<dt><strong>Purpose</strong></dt>
<dd>Binary or threshold-based status display with color-coded LED</dd>

<dt><strong>Parameters</strong></dt>
<dd>1 (single parameter only)</dd>

<dt><strong>Best For</strong></dt>
<dd>Quick status monitoring and at-a-glance system health</dd>
</dl>

</td>
<td width="60%">

**LED States**

<table>
<tr><th>State</th><th>Color</th><th>Condition</th></tr>
<tr><td>Low</td><td style="background:#1a1a1a; color:#0078ff">Blue</td><td>Below low_warn</td></tr>
<tr><td>Normal</td><td style="background:#1a1a1a; color:#21b35a">Green</td><td>low_warn to high_warn</td></tr>
<tr><td>Warning</td><td style="background:#1a1a1a; color:#ffbf00">Yellow</td><td>high_warn to high_crit</td></tr>
<tr><td>Critical</td><td style="background:#1a1a1a; color:#ff3131">Red</td><td>Beyond critical limits</td></tr>
<tr><td>No Data</td><td style="background:#1a1a1a; color:#555555">Gray</td><td>No data received</td></tr>
</table>

**Features**

- Glowing LED with shadow effect
- Numeric value display
- Unit label
- Border styling

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Log Table</h3></summary>

<table>
<tr>
<td width="40%">

<dl>
<dt><strong>Purpose</strong></dt>
<dd>Timestamped tabular display of multi-parameter data</dd>

<dt><strong>Parameters</strong></dt>
<dd>1+ (supports multiple parameters)</dd>

<dt><strong>Best For</strong></dt>
<dd>Detailed data inspection and debugging</dd>
</dl>

</td>
<td width="60%">

**Features**

- 500-row history buffer
- Automatic scrolling
- Timestamped entries
- Search functionality
- Highlight matching rows

**Search Operators**

<table>
<tr><th>Operator</th><th>Function</th></tr>
<tr><td>=</td><td>Equal to (with tolerance)</td></tr>
<tr><td>></td><td>Greater than</td></tr>
<tr><td><</td><td>Less than</td></tr>
<tr><td>>=</td><td>Greater than or equal</td></tr>
<tr><td><=</td><td>Less than or equal</td></tr>
</table>

**Usage**

1. Select parameter from dropdown
2. Choose operator
3. Enter target value
4. Click "Search Last"
5. Matching row highlights in blue

</td>
</tr>
</table>

</details>

<details>
<summary><h3>Map Widget (GPS)</h3></summary>

<table>
<tr>
<td width="40%">

<dl>
<dt><strong>Purpose</strong></dt>
<dd>GPS coordinate visualization with satellite imagery</dd>

<dt><strong>Parameters</strong></dt>
<dd>Exactly 2 (Latitude and Longitude)</dd>

<dt><strong>Requirements</strong></dt>
<dd>PySide6-WebEngine (optional dependency)</dd>

<dt><strong>Best For</strong></dt>
<dd>Location monitoring and trajectory tracking</dd>
</dl>

</td>
<td width="60%">

**Features**

- Real-time tracking with rocket emoji marker
- Red trajectory path line
- Satellite imagery (Esri World Imagery)
- Interactive zoom and pan
- Magnifier button (zoom to rocket)
- Coordinate overlay display
- Conservative zoom limits to prevent empty tiles

**Map Controls**

- Scroll wheel: Zoom in/out
- Click and drag: Pan view
- Magnifier button: Jump to current position
- Max zoom: 17 (prevents over-zooming)

**Fallback Mode**

If WebEngine not available:
- Text-only coordinate display
- Numeric latitude/longitude
- Prompt to install WebEngine

</td>
</tr>
</table>

</details>

---

## Keyboard Shortcuts

<table>
<tr>
<th width="30%">Category</th>
<th width="35%">Action</th>
<th width="35%">Shortcut</th>
</tr>
<tr>
<td rowspan="6"><strong>File Operations</strong></td>
<td>New Dashboard</td>
<td><code>Ctrl+N</code></td>
</tr>
<tr>
<td>Load Project</td>
<td><code>Ctrl+O</code></td>
</tr>
<tr>
<td>Save Project</td>
<td><code>Ctrl+S</code></td>
</tr>
<tr>
<td>Save Project As</td>
<td><code>Ctrl+Shift+S</code></td>
</tr>
<tr>
<td>Connection Settings</td>
<td><code>Ctrl+Shift+C</code></td>
</tr>
<tr>
<td>Exit Application</td>
<td><code>Ctrl+Q</code></td>
</tr>
<tr>
<td rowspan="3"><strong>Edit Operations</strong></td>
<td>Manage Parameters</td>
<td><code>Ctrl+P</code></td>
</tr>
<tr>
<td>Add Widget</td>
<td><code>Ctrl+W</code></td>
</tr>
<tr>
<td>Remove Widget</td>
<td><code>Ctrl+Shift+W</code></td>
</tr>
<tr>
<td rowspan="2"><strong>Filters</strong></td>
<td>Manage Filters</td>
<td><code>Ctrl+F</code></td>
</tr>
<tr>
<td>Add Filter (opens menu)</td>
<td><em>Via menu only</em></td>
</tr>
<tr>
<td rowspan="3"><strong>Data Logging</strong></td>
<td>Configure Logging</td>
<td><code>Ctrl+L</code></td>
</tr>
<tr>
<td>Start Logging</td>
<td><code>Ctrl+Shift+L</code></td>
</tr>
<tr>
<td>Stop Logging</td>
<td><code>Ctrl+Alt+L</code></td>
</tr>
<tr>
<td rowspan="4"><strong>View Controls</strong></td>
<td>Add Tab</td>
<td><code>Ctrl+T</code></td>
</tr>
<tr>
<td>Rename Current Tab</td>
<td><code>Ctrl+R</code></td>
</tr>
<tr>
<td>Raw Telemetry Monitor</td>
<td><code>Ctrl+M</code></td>
</tr>
<tr>
<td>Pause/Resume Stream</td>
<td><code>Space</code></td>
</tr>
<tr>
<td rowspan="1"><strong>Help</strong></td>
<td>Documentation</td>
<td><code>F1</code></td>
</tr>
</table>

---

## Data Logging

<div align="center">
<h3>Comprehensive Data Recording System</h3>
<p><em>Log telemetry data to CSV or JSON with configurable parameters</em></p>
</div>

### Configuration

<table>
<tr>
<th width="25%">Setting</th>
<th width="35%">Options</th>
<th width="40%">Description</th>
</tr>
<tr>
<td><strong>Format</strong></td>
<td>CSV, JSON</td>
<td>Output file format</td>
</tr>
<tr>
<td><strong>File Path</strong></td>
<td>Auto-generated or custom</td>
<td>Location to save log file<br/><em>Auto: logs/dashboard_data_YYYYMMDD_HHMMSS.ext</em></td>
</tr>
<tr>
<td><strong>Parameters</strong></td>
<td>Select from configured</td>
<td>Choose which parameters to log</td>
</tr>
<tr>
<td><strong>Buffer Size</strong></td>
<td>10-1000 entries</td>
<td>Number of entries before disk write</td>
</tr>
</table>

### Format Comparison

<table>
<tr>
<td width="50%">

**CSV Format**

**Advantages**
- Excel/MATLAB compatible
- Human-readable
- Widely supported
- Easy column analysis

**Structure**
```csv
timestamp,elapsed_time,temp_sensor_Temperature,humidity_Humidity
2025-01-15 10:30:00.123,0.000,23.500,65.200
2025-01-15 10:30:01.223,1.100,23.600,65.100
```

**Use Cases**
- Spreadsheet analysis
- Statistical processing
- Quick data inspection
- Report generation

</td>
<td width="50%">

**JSON Format**

**Advantages**
- Structured data format
- Programmatic parsing
- Self-documenting
- Nested data support

**Structure**
```json
{"timestamp": "2025-01-15T10:30:00.123", "elapsed_time": 0.0, "parameters": {"temp_sensor": 23.5, "humidity": 65.2}}
{"timestamp": "2025-01-15T10:30:01.223", "elapsed_time": 1.1, "parameters": {"temp_sensor": 23.6, "humidity": 65.1}}
```

**Use Cases**
- Python/JavaScript analysis
- Database import
- API integration
- Complex data structures

</td>
</tr>
</table>

### Buffer Size Guidelines

<table>
<tr>
<th>Data Rate</th>
<th>Recommended Buffer</th>
<th>Write Frequency</th>
<th>Memory Impact</th>
</tr>
<tr>
<td>1-10 Hz</td>
<td>100</td>
<td>Every 10-100 sec</td>
<td>Low</td>
</tr>
<tr>
<td>10-50 Hz</td>
<td>200-500</td>
<td>Every 4-50 sec</td>
<td>Medium</td>
</tr>
<tr>
<td>50-100 Hz</td>
<td>500-1000</td>
<td>Every 10-20 sec</td>
<td>Medium-High</td>
</tr>
<tr>
<td>100+ Hz</td>
<td>1000</td>
<td>Every 10 sec</td>
<td>High</td>
</tr>
</table>

**Tradeoffs**

<table>
<tr>
<th>Buffer Size</th>
<th>Advantages</th>
<th>Disadvantages</th>
</tr>
<tr>
<td><strong>Larger (500-1000)</strong></td>
<td>
- Less disk I/O<br/>
- Better performance<br/>
- Lower CPU usage
</td>
<td>
- Higher memory usage<br/>
- More data lost if crash<br/>
- Longer flush times
</td>
</tr>
<tr>
<td><strong>Smaller (10-100)</strong></td>
<td>
- Lower memory usage<br/>
- Safer (less data loss)<br/>
- Faster flush
</td>
<td>
- More frequent writes<br/>
- Higher disk I/O<br/>
- Potential performance impact
</td>
</tr>
</table>

---

## Troubleshooting

### Quick Diagnostic Checklist

<table>
<tr>
<td width="50%">

**Connection Diagnostics**

- [ ] Connection shows "Connected" (green)
- [ ] Stream shows "STREAMING" (not paused)
- [ ] Correct connection mode selected
- [ ] Firewall allows communication
- [ ] Cables properly connected
- [ ] Device powered on

</td>
<td width="50%">

**Data Diagnostics**

- [ ] Parameters properly configured
- [ ] Array indices match data structure
- [ ] Data format matches device output
- [ ] Channel count correct
- [ ] Check Raw Telemetry Monitor
- [ ] Verify incoming packet structure

</td>
</tr>
</table>

### Common Issues

<details>
<summary><h4>Serial Port Not Detected</h4></summary>

**Symptoms**
- Port dropdown is empty
- Desired port not listed
- "Port access denied" error

**Solutions**

<table>
<tr>
<th>Platform</th>
<th>Solution</th>
</tr>
<tr>
<td><strong>Windows</strong></td>
<td>
1. Click "Refresh" button<br/>
2. Check Device Manager for COM port number<br/>
3. Close other programs using the port<br/>
4. Try different USB port<br/>
5. Reinstall device drivers
</td>
</tr>
<tr>
<td><strong>Linux</strong></td>
<td>
1. Add user to dialout group:<br/>
   <code>sudo usermod -a -G dialout $USER</code><br/>
2. Logout and login<br/>
3. Check port permissions:<br/>
   <code>ls -l /dev/ttyUSB0</code><br/>
4. Try without sudo first
</td>
</tr>
<tr>
<td><strong>macOS</strong></td>
<td>
1. Check /dev/tty.* and /dev/cu.* devices<br/>
2. Install FTDI/CH340 drivers if needed<br/>
3. Grant permissions in System Preferences
</td>
</tr>
</table>

</details>

<details>
<summary><h4>No Data Appearing</h4></summary>

**Diagnostic Steps**

1. **Check Raw Telemetry Monitor** (Ctrl+M)
   - Are packets arriving?
   - What format are they in?
   - Any error messages?

2. **Verify Connection**
   - Status bar shows "Connected"?
   - Green indicator in connection status?
   - Stream not paused?

3. **Check Parameter Configuration**
   - Array indices correct?
   - Match incoming data structure?
   - Parameters defined?

4. **Verify Data Format**
   - Format matches device output?
   - Channel count correct?
   - Endianness correct (for binary)?

5. **Test with Dummy Data**
   - Switch to dummy mode
   - If dummy works, issue is with connection/format
   - If dummy doesn't work, issue is with configuration

</details>

<details>
<summary><h4>High CPU/Memory Usage</h4></summary>

**Optimization Strategies**

<table>
<tr>
<th>Issue</th>
<th>Solution</th>
<th>Impact</th>
</tr>
<tr>
<td>Too many widgets</td>
<td>Remove unused widgets<br/>Close unnecessary tabs</td>
<td>High</td>
</tr>
<tr>
<td>Heavy widgets</td>
<td>Replace graphs with value cards<br/>Use LED indicators instead of gauges</td>
<td>Medium</td>
</tr>
<tr>
<td>High data rate</td>
<td>Reduce incoming sample rate<br/>Increase logging buffer size</td>
<td>High</td>
</tr>
<tr>
<td>Long graph history</td>
<td>Limit history buffer (500 default)<br/>Use fewer graph widgets</td>
<td>Medium</td>
</tr>
<tr>
<td>Many filters</td>
<td>Disable unused filters<br/>Use simpler filter types</td>
<td>Low</td>
</tr>
</table>

</details>

<details>
<summary><h4>Data Logging Not Working</h4></summary>

**Troubleshooting Checklist**

<table>
<tr>
<th>Check</th>
<th>Action</th>
</tr>
<tr>
<td>Configuration</td>
<td>Run <strong>Data Logging → Configure</strong><br/>Select at least one parameter</td>
</tr>
<tr>
<td>Permissions</td>
<td>Verify write access to logs/ directory<br/>Check disk space available</td>
</tr>
<tr>
<td>File Lock</td>
<td>Close log file if open in Excel/editor<br/>Stop logging before opening file</td>
</tr>
<tr>
<td>Status</td>
<td>Check status bar shows "Logging: ON"<br/>Verify filename displayed</td>
</tr>
<tr>
<td>Buffer</td>
<td>Wait for buffer to flush<br/>Or stop logging to force flush</td>
</tr>
</table>

</details>

<details>
<summary><h4>Connection Refused (TCP/UDP)</h4></summary>

**Network Troubleshooting**

1. **Verify Server**
   - Is server application running?
   - Listening on correct port?
   - Check with: `netstat -an | grep PORT`

2. **Firewall**
   - Windows: Check Windows Defender Firewall
   - Linux: Check iptables/ufw
   - Allow Python/Glance through firewall

3. **Network**
   - Ping server: `ping SERVER_IP`
   - Check connectivity
   - Verify correct IP address

4. **Port**
   - Port not in use by other application?
   - Port number correct (1-65535)?
   - Common ports: avoid 80, 443, 8080

</details>

### Error Messages

<table>
<tr>
<th width="30%">Error</th>
<th width="30%">Cause</th>
<th width="40%">Solution</th>
</tr>
<tr>
<td><code>Port access denied</code></td>
<td>Insufficient permissions</td>
<td>Linux: Add to dialout group<br/>Windows: Close other programs<br/>Run with proper permissions</td>
</tr>
<tr>
<td><code>Connection refused</code></td>
<td>Server not listening</td>
<td>Verify server running<br/>Check IP/port<br/>Review firewall settings</td>
</tr>
<tr>
<td><code>Module not found</code></td>
<td>Missing dependency</td>
<td>Run: <code>pip install -r requirements.txt</code><br/>Check virtual environment activated</td>
</tr>
<tr>
<td><code>Invalid data format</code></td>
<td>Format mismatch</td>
<td>Check device output format<br/>Adjust data format settings<br/>Use Raw Telemetry Monitor</td>
</tr>
<tr>
<td><code>Array index out of range</code></td>
<td>Index exceeds data length</td>
<td>Verify channel count<br/>Check parameter array indices<br/>Review incoming packet size</td>
</tr>
</table>

---

## Development

### Project Structure

```
Glance/
├── main.py                      # Application entry point & main window
├── backend.py                   # Data reader and protocol parser
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── LICENSE                      # GPL v3.0 license
├── app/
│   ├── __init__.py
│   ├── widgets.py               # Widget implementations (7+ types)
│   ├── dialogs.py               # Dialog windows and forms
│   └── ui/
│       ├── __init__.py
│       └── main_window.py       # Main window class
├── docs/
│   └── public/
│       ├── Glance_nobg.png      # Application logo
│       ├── Glance_nobg _jl.png  # Alternate logo
│       ├── ign_logo_wht.png     # Team Ignition logo
│       └── Doc Images/          # Documentation screenshots
├── logs/                        # Auto-generated log directory
├── examples/
│   └── preset1.json             # Example configuration
└── Documentation/
    └── index.html               # Built-in documentation (if available)
```

### Architecture Overview

<table>
<tr>
<td width="50%">

**Core Components**

<dl>
<dt><strong>main.py</strong></dt>
<dd>Main application window, UI phases, widget management, project save/load, filter management</dd>

<dt><strong>backend.py</strong></dt>
<dd>DataReader class for serial/TCP/UDP communication, protocol parsing, data buffering</dd>

<dt><strong>widgets.py</strong></dt>
<dd>7+ widget types: ValueCard, TimeGraph, Gauge, Histogram, LED, LogTable, MapWidget</dd>

<dt><strong>dialogs.py</strong></dt>
<dd>Configuration dialogs: ConnectionSettings, AddWidget, ParameterEntry, ManageParameters, DataLogging</dd>
</dl>

</td>
<td width="50%">

**Key Classes**

<dl>
<dt><strong>MainWindow</strong></dt>
<dd>Primary application window with 4-phase UI system</dd>

<dt><strong>DataSimulator</strong></dt>
<dd>QThread for background data acquisition</dd>

<dt><strong>DataLogger</strong></dt>
<dd>CSV/JSON logging with buffering</dd>

<dt><strong>FilterManager</strong></dt>
<dd>Signal processing filter chain management</dd>

<dt><strong>Filter Classes</strong></dt>
<dd>MovingAverageFilter, LowPassFilter, KalmanFilter, MedianFilter</dd>

<dt><strong>RawTelemetryMonitor</strong></dt>
<dd>Serial monitor-style packet inspection</dd>
</dl>

</td>
</tr>
</table>

### Adding Custom Widgets

<details>
<summary><h4>Step-by-Step Widget Creation</h4></summary>

**1. Create Widget Class** in `app/widgets.py`:

```python
class CustomWidget(QWidget):
    def __init__(self, param_config):
        super().__init__()
        self.param = param_config
        
        # Initialize UI
        layout = QVBoxLayout(self)
        self.value_label = QLabel("--")
        layout.addWidget(self.value_label)
    
    def update_value(self, value):
        """Update display with new data"""
        if value is not None:
            self.value_label.setText(f"{value:.2f}")
        else:
            self.value_label.setText("NO DATA")
```

**2. Register in `AddWidgetDialog`** (`app/dialogs.py`):

```python
# Add to display type options
self.display_type_combo.addItem("Custom Widget")

# Add to parameter count validation
elif selected_type == "Custom Widget" and len(selected_params) != 1:
    QMessageBox.warning(self, "Invalid Selection",
                       "Custom Widget requires exactly 1 parameter.")
    return
```

**3. Add Handler** in `MainWindow.add_widget_to_dashboard()` (`main.py`):

```python
elif config['displayType'] == 'Custom Widget' and len(param_configs) == 1:
    widget = CustomWidget(param_configs[0])
```

**4. Handle Updates** in `MainWindow.update_data()` (`main.py`):

```python
elif isinstance(widget, CustomWidget):
    widget.update_value(filtered_value)
```

</details>

### Building Executable

<details>
<summary><h4>PyInstaller Build Instructions</h4></summary>

**Install PyInstaller**

```bash
pip install pyinstaller
```

**Windows Executable**

```bash
pyinstaller --onefile --windowed \
    --name "Glance" \
    --icon=docs/public/Glance_nobg.png \
    --add-data "docs/public:public" \
    --add-data "Documentation:Documentation" \
    main.py
```

**Linux/macOS Executable**

```bash
pyinstaller --onefile --windowed \
    --name "Glance" \
    --icon=docs/public/Glance_nobg.png \
    --add-data "docs/public:public" \
    --add-data "Documentation:Documentation" \
    main.py
```

**Output**: Executable will be in `dist/` directory

</details>

### Code Style Guidelines

- **PEP 8** compliance for Python code
- Type hints for function parameters and returns
- Docstrings for public methods and classes
- Descriptive variable names (no single letters except loops)
- Comments for complex logic
- Consistent indentation (4 spaces)

### Testing

<details>
<summary><h4>Testing Procedures</h4></summary>

**Manual Testing with Dummy Data**

```bash
python main.py
# Select "dummy" mode in connection settings
# Verify all widgets update correctly
# Test all menu functions
# Check data logging
# Verify filters work
```

**Testing Custom Filters**

1. Add filter to parameter
2. View filtered vs raw data in graph
3. Compare logged data (raw values stored)
4. Enable/disable filter - verify instant response
5. Reset filter - verify buffer clears

**Network Testing**

```bash
# Start a simple TCP server for testing
python -c "import socket; s=socket.socket(); s.bind(('', 9000)); s.listen(1); c,a=s.accept(); [c.send(b'[1,2,3]\n') or __import__('time').sleep(0.1) for _ in range(100)]"
```

</details>

---

## About Team Ignition

<div align="center">

<img src="docs/public/ign_logo_wht.png" alt="Team Ignition Logo" width="200"/>

<h3>Official Student Rocketry Team</h3>
<p><strong>Vellore Institute of Technology, Chennai</strong></p>

</div>

### Our Mission

Team Ignition is dedicated to advancing aerospace innovation through hands-on learning and experimentation. We design, build, and launch experimental rockets while developing every subsystem in-house — from propulsion and avionics to recovery systems and ground-support equipment.

### What We Do

<table>
<tr>
<td width="50%">

**Design & Engineering**
- Solid and hybrid rocket motor development
- Flight computers and telemetry systems
- CubeSat and CanSat payloads
- Ground-support software applications
- Launch pad and recovery systems

</td>
<td width="50%">

**Compete & Innovate**
- National and international rocketry competitions
- Research and development projects
- Collaboration with industry partners
- Workshops and outreach programs
- Open-source software contributions

</td>
</tr>
</table>

### Our Projects

- **Propulsion**: Solid and hybrid rocket motors with in-house propellant development
- **Avionics**: Custom flight computers, telemetry systems, and ground control software
- **Payloads**: CubeSat/CanSat satellites, scientific instruments, and atmospheric sensors
- **Recovery**: Parachute systems, deployment mechanisms, and landing prediction software
- **Software**: Ground station applications, data visualization tools (like Glance), and simulation software

### Connect With Us

<div align="center">

<p>
  <a href="https://teamignition.space"><img src="https://img.shields.io/badge/Website-teamignition.space-blue?style=for-the-badge" alt="Website"/></a>
  <a href="https://github.com/teamignitionvitc"><img src="https://img.shields.io/badge/GitHub-teamignitionvitc-black?style=for-the-badge&logo=github" alt="GitHub"/></a>
</p>

<p>
  <a href="https://x.com/ignitiontech23"><img src="https://img.shields.io/badge/Twitter-@ignitiontech23-blue?style=for-the-badge&logo=twitter" alt="Twitter"/></a>
  <a href="https://www.linkedin.com/in/teamignition/"><img src="https://img.shields.io/badge/LinkedIn-Team%20Ignition-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/></a>
  <a href="https://www.instagram.com/ignition_vitc"><img src="https://img.shields.io/badge/Instagram-@ignition__vitc-E4405F?style=for-the-badge&logo=instagram" alt="Instagram"/></a>
</p>

</div>

---

## License

<table>
<tr>
<td width="70%">

This project is licensed under the **GNU General Public License v3.0** with additional restrictions.

### Additional Restriction

**This software may not be used for commercial purposes without explicit written permission from the authors (Team Ignition Software Department).**

For commercial licensing inquiries, please contact us through our website.

</td>
<td width="30%">

**License Summary**

- ✓ Use freely for non-commercial purposes
- ✓ Modify and distribute
- ✓ Private use
- ✗ Commercial use without permission
- ⚠ Must include license and copyright

[Full License Text](https://www.gnu.org/licenses/gpl-3.0.en.html)

</td>
</tr>
</table>

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

## Contributing

<div align="center">
<p><strong>We welcome contributions from the community!</strong></p>
<p>Whether you're fixing bugs, adding features, improving documentation, or testing — your help is valuable.</p>
</div>

### How to Contribute

<table>
<tr>
<td width="50%">

**Code Contributions**

1. Fork the repository
2. Create feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes
   ```bash
   git commit -m 'Add AmazingFeature'
   ```
4. Push to branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open Pull Request

</td>
<td width="50%">

**Other Ways to Help**

- Report bugs and issues
- Suggest new features
- Improve documentation
- Test on different platforms
- Share with others
- Provide feedback
- Create tutorials

</td>
</tr>
</table>

### Contribution Guidelines

<details>
<summary><h4>Code Standards</h4></summary>

- Follow PEP 8 style guide
- Add type hints where applicable
- Include docstrings for public methods
- Write clear commit messages
- Keep pull requests focused
- Update documentation as needed

</details>

<details>
<summary><h4>Testing Requirements</h4></summary>

Before submitting:
- Test with dummy data mode
- Verify all widgets function
- Check on target platform
- Ensure no new warnings/errors
- Update requirements.txt if needed

</details>

<details>
<summary><h4>Documentation</h4></summary>

- Update README for new features
- Add inline code comments
- Include usage examples
- Document configuration options
- Update screenshots if UI changed

</details>

### Reporting Issues

<table>
<tr>
<th width="30%">Include</th>
<th width="70%">Details</th>
</tr>
<tr>
<td><strong>System Info</strong></td>
<td>OS (Windows 11, Ubuntu 22.04, macOS 12), Python version, Application version</td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Clear explanation of the issue</td>
</tr>
<tr>
<td><strong>Steps to Reproduce</strong></td>
<td>1. Step one<br/>2. Step two<br/>3. Step three</td>
</tr>
<tr>
<td><strong>Expected Behavior</strong></td>
<td>What should happen</td>
</tr>
<tr>
<td><strong>Actual Behavior</strong></td>
<td>What actually happens</td>
</tr>
<tr>
<td><strong>Screenshots/Logs</strong></td>
<td>Attach relevant files</td>
</tr>
</table>

### Feature Requests

When suggesting new features:
- Explain the use case
- Describe expected behavior
- Consider implementation complexity
- Check if similar feature exists
- Discuss in issues first for major changes

---

## Support

### Getting Help

<table>
<tr>
<td width="25%"><strong>Documentation</strong></td>
<td width="75%">Read this README and built-in docs (F1)</td>
</tr>
<tr>
<td><strong>Search Issues</strong></td>
<td>Look for similar problems on <a href="https://github.com/teamignitionvitc/Glance/issues">GitHub Issues</a></td>
</tr>
<tr>
<td><strong>Ask Community</strong></td>
<td>Open a GitHub discussion for questions</td>
</tr>
<tr>
<td><strong>Report Bugs</strong></td>
<td>Create a new issue with details</td>
</tr>
<tr>
<td><strong>Contact Team</strong></td>
<td>Reach out via our <a href="https://teamignition.space">website</a></td>
</tr>
</table>

### Frequently Asked Questions

<details>
<summary><h4>Can I use Glance for commercial projects?</h4></summary>

You need explicit written permission from Team Ignition Software Department for commercial use. Contact us through our website for licensing inquiries.

</details>

<details>
<summary><h4>What data formats are supported?</h4></summary>

- JSON array: `[value1, value2, ...]`
- CSV: `value1,value2,...`
- Raw bytes: Binary data with configurable width
- Bits: Bit-level extraction

Custom formats can be implemented in `backend.py`.

</details>

<details>
<summary><h4>Does Glance work with Arduino/ESP32/Raspberry Pi?</h4></summary>

Yes! As long as your device sends data via:
- Serial (USB or UART)
- TCP/IP network
- UDP network

Configure the connection mode and data format to match your device's output.

</details>

<details>
<summary><h4>Can I add custom widgets?</h4></summary>

Yes! See the [Development](#development) section for instructions on creating custom widgets. You'll need to:
1. Create widget class in `widgets.py`
2. Register in `AddWidgetDialog`
3. Add handler in `MainWindow`

</details>

<details>
<summary><h4>How do I contribute to the project?</h4></summary>

See [Contributing](#contributing) section. Fork the repository, make your changes, and submit a pull request. We welcome bug fixes, features, documentation improvements, and testing.

</details>

---

## Acknowledgments

<table>
<tr>
<td width="50%">

**Built With**

- **PySide6** - Qt6 bindings for Python
- **pyqtgraph** - High-performance plotting
- **NumPy** - Numerical computing
- **pyserial** - Serial communication

</td>
<td width="50%">

**Developed By**

- **Team Ignition Software Department**
- Tested during rocket ground operations
- Designed for real-world telemetry applications
- Feedback from team members and competitions

</td>
</tr>
</table>

**Special Thanks**

- VIT Chennai for supporting our team
- Competition organizers for feedback
- Open-source community for excellent libraries
- All contributors and testers

---

## Version History

### v2.0.0 (Current Release)

<details open>
<summary><strong>Major Improvements</strong></summary>

<table>
<tr>
<td width="50%">

**UI/UX Enhancements**
- Complete redesign with 4-phase wizard
- Welcome screen with quick actions
- Modern dark theme with gradients
- Professional status bar with metrics
- Dashboard title customization
- Improved widget management

</td>
<td width="50%">

**New Features**
- Advanced signal filtering (Kalman, Moving Average, Low-pass, Median)
- Raw telemetry monitor with multiple display modes
- Comprehensive data logging (CSV/JSON)
- Array-index parameter mapping
- Filter chain management
- Connection diagnostics
- Keyboard shortcuts (20+)

</td>
</tr>
<tr>
<td colspan="2">

**Performance & Reliability**
- Optimized data handling for high-frequency streams
- Better error handling and validation
- Improved connection stability
- Enhanced project save/load system
- Unsaved changes tracking
- Buffer management for efficiency

</td>
</tr>
</table>

</details>

### v1.0.0 (Initial Release)

<details>
<summary><strong>Core Features</strong></summary>

- Basic dashboard functionality
- Serial and network data sources
- Core widget types (graphs, gauges, tables)
- Simple parameter configuration
- Project save/load

</details>

---

<div align="center">

<h2>⭐ Star this repository if you find it useful!</h2>

<p><strong>Glance</strong> - Professional telemetry visualization by Team Ignition<br/>
<em>Advancing aerospace innovation through software excellence</em></p>

<hr/>

<p>
  <a href="https://github.com/teamignitionvitc/Glance/issues">Report Bug</a> •
  <a href="https://github.com/teamignitionvitc/Glance/issues">Request Feature</a> •
  <a href="https://glance.teamignition.space/">Documentation</a>
</p>

<p><sub>Made with ❤️ by Team Ignition Software Department</sub></p>

<p><sub>Copyright © 2025 Team Ignition | VIT Chennai</sub></p>

</div>