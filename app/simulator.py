import time
import math
import random
from PySide6.QtCore import QThread, Signal
from app.backend import DataReader


class DataSimulator(QThread):
    newData = Signal(list)

    def __init__(self, num_channels=32, connection_settings=None):
        super().__init__()
        self.num_channels = num_channels
        self._is_running = True
        self._is_paused = False
        self.mode = "backend"
        self.connection_settings = connection_settings or {
            'mode': 'serial',
            'serial_port': 'COM4',
            'baudrate': 115200,
            'tcp_host': '127.0.0.1',
            'tcp_port': 9000,
            'udp_host': '0.0.0.0',
            'udp_port': 9000,
            'timeout': 1.0,
            'data_format': 'json_array',
            'channel_count': 32,
            'sample_width_bytes': 2,
            'little_endian': True,
            'csv_separator': ',',
        }

    def run(self):
        while self._is_running:
            if not self._is_paused:
                if self.mode == "dummy":
                    packet = [0.0] * self.num_channels
                    timestamp = time.time()
                    for i in range(self.num_channels):
                        value = 50 + 40 * math.sin(timestamp / (10 + i % 5) + i)
                        if random.random() > 0.98:
                            value = random.uniform(-10, 120)
                        packet[i] = value
                    self.newData.emit(packet)
                elif self.mode == "backend":
                    if not hasattr(self, "reader"):
                        cs = self.connection_settings
                        self.reader = DataReader(
                            mode=cs.get('mode', 'serial'),
                            serial_port=cs.get('serial_port', 'COM4'),
                            baudrate=cs.get('baudrate', 115200),
                            tcp_host=cs.get('tcp_host', '127.0.0.1'),
                            tcp_port=cs.get('tcp_port', 9000),
                            udp_host=cs.get('udp_host', '0.0.0.0'),
                            udp_port=cs.get('udp_port', 9000),
                            timeout=cs.get('timeout', 1.0),
                            data_format=cs.get('data_format', 'json_array'),
                            channel_count=int(cs.get('channel_count', 32)),
                            sample_width_bytes=int(cs.get('sample_width_bytes', 2)),
                            little_endian=bool(cs.get('little_endian', True)),
                            csv_separator=cs.get('csv_separator', ',')
                        )
                    line = self.reader.read_line()
                    if isinstance(line, list):
                        packet = line
                        self.newData.emit(packet)
            time.sleep(0.1)

    def toggle_pause(self):
        self._is_paused = not self._is_paused
        return self._is_paused

    def stop(self):
        self._is_running = False


