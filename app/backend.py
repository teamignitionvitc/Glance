import json
import socket
from typing import Optional, List, Union

try:
    import serial  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    serial = None


class DataReader:
    """Flexible line-based reader supporting Serial, TCP, and UDP input.

    Supports formats: json_array, csv, raw_bytes, bits.
    """

    def __init__(
        self,
        mode: str = "serial",  # serial | tcp | udp
        serial_port: str = "COM4",
        baudrate: int = 115200,
        tcp_host: str = "127.0.0.1",
        tcp_port: int = 9000,
        udp_host: str = "0.0.0.0",
        udp_port: int = 9000,
        timeout: float = 1.0,
        data_format: str = "json_array",  # json_array | csv | raw_bytes | bits
        channel_count: int = 32,
        sample_width_bytes: int = 2,
        little_endian: bool = True,
        csv_separator: str = ",",
    ) -> None:
        self.mode = mode.lower()
        self.timeout = timeout
        self.rx_bytes: int = 0
        self._buffer = b""
        self.data_format = data_format
        self.channel_count = max(1, int(channel_count))
        self.sample_width_bytes = max(1, int(sample_width_bytes))
        self.little_endian = bool(little_endian)
        self.csv_separator = csv_separator or ","

        self.ser = None
        self.sock: Optional[socket.socket] = None

        if self.mode == "serial":
            if serial is None:
                print("pyserial not available; cannot open serial port")
                self.ser = None
            else:
                try:
                    self.ser = serial.Serial(port=serial_port, baudrate=baudrate, timeout=timeout)  # type: ignore
                except Exception as exc:
                    print("Could not open serial port", exc)
                    self.ser = None
        elif self.mode in ("tcp", "udp"):
            try:
                if self.mode == "tcp":
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(timeout)
                    s.connect((tcp_host, tcp_port))
                    self.sock = s
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(timeout)
                    s.bind((udp_host, udp_port))
                    self.sock = s
            except Exception as exc:
                print("Could not open network socket", exc)
                self.sock = None
        else:
            print(f"Unknown mode '{mode}', expected serial|tcp|udp")

    def _read_bytes(self) -> Optional[bytes]:
        try:
            if self.mode == "serial" and self.ser:
                data = self.ser.readline()
                if data:
                    self.rx_bytes += len(data)
                return data or None
            elif self.mode == "tcp" and self.sock:
                if b"\n" not in self._buffer:
                    chunk = self.sock.recv(4096)
                    if not chunk:
                        return None
                    self.rx_bytes += len(chunk)
                    self._buffer += chunk
                if b"\n" in self._buffer:
                    line, self._buffer = self._buffer.split(b"\n", 1)
                    return line + b"\n"
                return None
            elif self.mode == "udp" and self.sock:
                chunk, _ = self.sock.recvfrom(8192)
                if not chunk:
                    return None
                self.rx_bytes += len(chunk)
                return chunk
            else:
                return None
        except Exception:
            return None

    def read_line(self) -> Union[None, List[float], str]:
        raw = self._read_bytes()
        if raw is None:
            return None
        try:
            if self.data_format == "json_array":
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    return None
                cleaned = line.replace(";", ",")
                if cleaned and cleaned[0] == "[":
                    arr = json.loads(cleaned)
                    return [float(x) for x in arr]
                return None
            elif self.data_format == "csv":
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    return None
                line = line.replace(";", ",")
                parts = [p.strip() for p in line.split(self.csv_separator)]
                values = []
                for p in parts:
                    if p:
                        try:
                            values.append(float(p))
                        except ValueError:
                            pass
                if values:
                    return values
                return None
            elif self.data_format == "raw_bytes":
                buf = bytes(raw)
                width = self.sample_width_bytes
                total = len(buf) - (len(buf) % width)
                if total <= 0:
                    return None
                values: List[float] = []
                for i in range(0, min(total, self.channel_count * width), width):
                    chunk = buf[i:i+width]
                    val = int.from_bytes(chunk, byteorder="little" if self.little_endian else "big", signed=False)
                    values.append(float(val))
                return values if values else None
            elif self.data_format == "bits":
                base_val: Optional[int] = None
                try:
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if line and line[0] == "[":
                        arr = json.loads(line)
                        if isinstance(arr, list) and arr:
                            base_val = int(float(arr[0]))
                    elif line:
                        line = line.replace(";", ",")
                        parts = [p.strip() for p in line.split(self.csv_separator)]
                        if parts and parts[0]:
                            base_val = int(float(parts[0]))
                except Exception:
                    base_val = None
                if base_val is None:
                    buf = bytes(raw)
                    if len(buf) > 0:
                        base_val = int.from_bytes(buf, byteorder="little" if self.little_endian else "big", signed=False)
                if base_val is None:
                    return None
                bits: List[float] = []
                for b in range(self.channel_count):
                    bits.append(1.0 if (base_val >> b) & 1 else 0.0)
                return bits
            else:
                return None
        except Exception as e:
            print("Parse error:", e)
            return "Parse"

    def close(self) -> None:
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass


