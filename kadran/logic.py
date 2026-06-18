"""
logic.py — Business logic, smoothing, state classification.
Runs in the UI thread (fast, no I/O).
"""

import threading
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict


# ---------------------------------------------------------------------------
# State enum
# ---------------------------------------------------------------------------
class State(Enum):
    NORMAL   = auto()
    WARNING  = auto()
    CRITICAL = auto()


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
MOTOR_TEMP_WARNING  = 90.0
MOTOR_TEMP_CRITICAL = 110.0
BATTERY_WARNING     = 20.0

# Assumed battery capacity kWh for range estimation
BATTERY_CAPACITY_KWH = 60.0

LERP_ALPHA = 0.12   # smoothing factor (lower = smoother / slower)


# ---------------------------------------------------------------------------
# Smoothed vehicle state
# ---------------------------------------------------------------------------
@dataclass
class VehicleState:
    # Smoothed display values
    speed:           float = 0.0
    battery:         float = 100.0
    motor_temp:      float = 25.0
    current:         float = 0.0
    consumption:     float = 0.0
    acceleration:    float = 0.0
    range_km:        float = 0.0
    total_km:        float = 0.0
    avg_consumption: float = 0.0
    gear:            str   = "P"

    # States
    motor_state:   State = State.NORMAL
    battery_state: State = State.NORMAL
    pack_voltage:     float = 0.0
    cell_min_voltage: float = 0.0
    cell_max_voltage: float = 0.0
    cell_max_temp:    float = 25.0
    # Meta
    can_alive: bool = False


# ---------------------------------------------------------------------------
# Logic processor
# ---------------------------------------------------------------------------
class LogicProcessor:
    """
    Reads raw values from the shared data_store (with lock), applies
    LERP smoothing, derives computed fields, and classifies states.
    Call update() once per frame from the UI thread.
    """

    def __init__(self, data_store: Dict, lock: threading.Lock):
        self._data_store = data_store
        self._lock = lock
        self._state = VehicleState()
        self._odometer_accum = 0.0   # distance accumulator (km)

    @property
    def state(self) -> VehicleState:
        return self._state

    def update(self, can_alive: bool) -> VehicleState:
        # 1. Snapshot raw data under lock
        with self._lock:
            raw = dict(self._data_store)

        s = self._state

        # 2. LERP smoothing
        s.speed        = _lerp(s.speed,        raw.get("speed",        s.speed))
        s.battery      = _lerp(s.battery,      raw.get("battery",      s.battery))
        s.motor_temp   = _lerp(s.motor_temp,   raw.get("motor_temp",   s.motor_temp))
        s.current      = _lerp(s.current,      raw.get("current",      s.current))
        s.consumption  = _lerp(s.consumption,  raw.get("consumption",  s.consumption))
        s.acceleration = _lerp(s.acceleration, raw.get("acceleration", s.acceleration))
        s.pack_voltage     = _lerp(s.pack_voltage,     raw.get("pack_voltage",     s.pack_voltage))
        s.cell_min_voltage = _lerp(s.cell_min_voltage, raw.get("cell_min_voltage", s.cell_min_voltage))
        s.cell_max_voltage = _lerp(s.cell_max_voltage, raw.get("cell_max_voltage", s.cell_max_voltage))
        s.cell_max_temp    = _lerp(s.cell_max_temp,    raw.get("cell_max_temp",    s.cell_max_temp))
        s.total_km     = raw.get("total_km", s.total_km)     # no smoothing for odometer
        s.gear         = raw.get("gear", s.gear)

        # 3. Computed fields
        if s.consumption > 0.1:
            # remaining kWh → km
            remaining_kwh = (s.battery / 100.0) * BATTERY_CAPACITY_KWH
            s.range_km = remaining_kwh / s.consumption * 100.0   # kWh/100km → km
        else:
            s.range_km = 0.0

        if s.total_km > 0.1:
            # Rough average: total energy used ÷ distance
            # We don't store cumulative energy; approximate from current consumption
            s.avg_consumption = s.consumption  # simplified

        # 4. State classification
        if s.motor_temp > MOTOR_TEMP_CRITICAL:
            s.motor_state = State.CRITICAL
        elif s.motor_temp > MOTOR_TEMP_WARNING:
            s.motor_state = State.WARNING
        else:
            s.motor_state = State.NORMAL

        if s.battery < BATTERY_WARNING:
            s.battery_state = State.WARNING
        else:
            s.battery_state = State.NORMAL

        # 5. CAN health flag
        s.can_alive = can_alive

        return s


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _lerp(current: float, target: float, alpha: float = LERP_ALPHA) -> float:
    return current + (target - current) * alpha


def state_color(state: State) -> tuple:
    """Return RGB tuple for a given state."""
    return {
        State.NORMAL:   (72, 199, 142),   # green
        State.WARNING:  (255, 193, 7),    # amber
        State.CRITICAL: (255, 82, 82),    # red
    }[state]
