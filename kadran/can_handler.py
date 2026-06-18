"""
can_handler.py — CAN Bus thread and signal decoding.
"""

import threading
import time
import logging

try:
    import can
    CAN_AVAILABLE = False  # can0 donanımı olmadığı için simülatörü zorla
except ImportError:
    CAN_AVAILABLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CAN sinyal haritası
# ---------------------------------------------------------------------------
CAN_MAP = {
    0x100: [
        {"name": "speed",        "start_bit": 0,  "length": 16, "scale": 0.1,  "offset": 0},
        {"name": "acceleration", "start_bit": 16, "length": 8,  "scale": 0.5,  "offset": 0},
    ],
    0x101: [
        {"name": "battery",      "start_bit": 0,  "length": 8,  "scale": 1,    "offset": 0},
    ],
    0x102: [
        {"name": "motor_temp",   "start_bit": 0,  "length": 8,  "scale": 1,    "offset": -40},
    ],
    0x103: [
        {"name": "current",      "start_bit": 0,  "length": 16, "scale": 0.1,  "offset": 0},
    ],
    0x104: [
        {"name": "consumption",  "start_bit": 0,  "length": 16, "scale": 0.1,  "offset": 0},
    ],
    0x105: [
        {"name": "pack_voltage",     "start_bit": 0,  "length": 16, "scale": 0.1,   "offset": 0},
        {"name": "cell_min_voltage", "start_bit": 16, "length": 16, "scale": 0.001, "offset": 0},
        {"name": "cell_max_voltage", "start_bit": 32, "length": 16, "scale": 0.001, "offset": 0},
    ],
    0x106: [
        {"name": "cell_max_temp",    "start_bit": 0,  "length": 8,  "scale": 1,    "offset": -40},
    ],
}

# ---------------------------------------------------------------------------
# Varsayılan veri deposu
# ---------------------------------------------------------------------------
DEFAULT_STORE = {
    "speed":            0.0,
    "battery":          100.0,
    "motor_temp":       25.0,
    "current":          0.0,
    "consumption":      0.0,
    "acceleration":     0.0,
    "gear":             "P",
    "range":            0.0,
    "total_km":         0.0,
    "avg_consumption":  0.0,
    "pack_voltage":     380.0,
    "cell_min_voltage": 3.85,
    "cell_max_voltage": 3.95,
    "cell_max_temp":    35.0,
}


def decode_signal(data: bytes, start_bit: int, length: int,
                  scale: float, offset: float) -> float:
    raw = int.from_bytes(data, byteorder="little")
    value = (raw >> start_bit) & ((1 << length) - 1)
    return value * scale + offset


def process_can_message(msg, data_store: dict, lock: threading.Lock) -> None:
    if msg.arbitration_id in CAN_MAP:
        with lock:
            for signal in CAN_MAP[msg.arbitration_id]:
                value = decode_signal(
                    msg.data,
                    signal["start_bit"],
                    signal["length"],
                    signal["scale"],
                    signal["offset"],
                )
                data_store[signal["name"]] = value


# ---------------------------------------------------------------------------
# CAN thread
# ---------------------------------------------------------------------------
class CANHandler:
    BUS_TIMEOUT     = 0.05
    RECONNECT_DELAY = 2.0

    def __init__(self, data_store: dict, lock: threading.Lock):
        self._data_store = data_store
        self._lock       = lock
        self._stop_event = threading.Event()
        self._thread     = threading.Thread(
            target=self._run, daemon=True, name="CAN-reader"
        )
        self._can_ok  = False
        self._last_rx = 0.0

    def start(self) -> None:
        self._thread.start()
        logger.info("CAN handler thread started")

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=3)
        logger.info("CAN handler thread stopped")

    @property
    def is_alive(self) -> bool:
        return self._can_ok and (time.time() - self._last_rx < 2.0)

    def _run(self) -> None:
        if not CAN_AVAILABLE:
            logger.warning("Simülatör modunda çalışıyor (CAN donanımı yok)")
            self._run_simulator()
            return

        while not self._stop_event.is_set():
            bus = None
            try:
                bus = can.interface.Bus(channel="can0", bustype="socketcan")
                self._can_ok = True
                logger.info("CAN bus bağlandı: can0")
                while not self._stop_event.is_set():
                    msg = bus.recv(timeout=self.BUS_TIMEOUT)
                    if msg is not None:
                        process_can_message(msg, self._data_store, self._lock)
                        self._last_rx = time.time()
            except Exception as exc:
                logger.error("CAN hatası: %s — %.1fs sonra tekrar denenecek", exc, self.RECONNECT_DELAY)
                self._can_ok = False
            finally:
                if bus is not None:
                    try:
                        bus.shutdown()
                    except Exception:
                        pass
            if not self._stop_event.is_set():
                time.sleep(self.RECONNECT_DELAY)

    def _run_simulator(self) -> None:
        """Gerçekçi demo verisi üretir — donanım olmadan test için."""
        import math
        t        = 0.0
        total_km = 0.0
        dt       = 0.05   # 50 ms

        while not self._stop_event.is_set():
            t += dt

            speed        = max(0.0, 80 + 60 * math.sin(t / 15) + 10 * math.sin(t / 3))
            battery      = max(0.0, min(100.0, 75 - t * 0.02))
            motor_temp   = 55 + 20 * math.sin(t / 30)
            current      = 150 + 80 * math.sin(t / 10)
            consumption  = max(0.0, 18 + 8 * math.sin(t / 20))
            accel        = 0.3 * math.sin(t / 5) + 0.05 * math.sin(t / 1.5)
            total_km    += speed * dt / 3600.0

            # Yeni batarya sinyalleri
            pack_voltage     = 380 + 20 * math.sin(t / 40)
            cell_min_voltage = 3.75 + 0.08 * math.sin(t / 30)
            cell_max_voltage = 3.92 + 0.05 * math.sin(t / 25)
            cell_max_temp    = 38 + 12 * math.sin(t / 35)

            with self._lock:
                self._data_store["speed"]            = speed
                self._data_store["battery"]          = battery
                self._data_store["motor_temp"]       = motor_temp
                self._data_store["current"]          = current
                self._data_store["consumption"]      = consumption
                self._data_store["acceleration"]     = accel
                self._data_store["total_km"]         = total_km
                self._data_store["pack_voltage"]     = pack_voltage
                self._data_store["cell_min_voltage"] = cell_min_voltage
                self._data_store["cell_max_voltage"] = cell_max_voltage
                self._data_store["cell_max_temp"]    = cell_max_temp

            self._can_ok  = True
            self._last_rx = time.time()
            time.sleep(dt)
