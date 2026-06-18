# EV Dashboard — Raspberry Pi (1280×480)

## Files

| File | Role |
|------|------|
| `main.py` | Entry point, Pygame init, main loop |
| `can_handler.py` | CAN Bus thread, DBC-like decode, demo simulator |
| `logic.py` | LERP smoothing, state classification, derived fields |
| `ui.py` | All Pygame rendering (panels, bars, gears) |

## Setup

```bash
# Install dependencies
pip install pygame python-can

# Bring up the CAN interface (Raspberry Pi with MCP2515 or similar)
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0

# Run
python main.py
```

## Without hardware

When `python-can` is not installed, or `can0` is unavailable, the app
automatically falls back to a built-in simulator that generates realistic
EV telemetry so the UI can be developed and tested on any machine.

## Controls

| Key | Action |
|-----|--------|
| `ESC` / `Q` | Quit |

## Layout (1280×480)

```
┌──────────────┬────────────────────────────┬──────────────┐
│  DATA PANEL  │       SPEED  +  BARS       │  REAR CAM    │
│  (25% = 320) │       (50% = 640)          │  (25% = 320) │
│              │                            │              │
│  Page 0:     │  ┌──┐  [  000.0 km/h ]  ┌──┐│              │
│  consumption │  │  │                   │  ││              │
│  battery     │  │  │  consumption bar  │  ││              │
│  motor_temp  │  │kWh│  accel bar (±)   │ g ││              │
│  current     │  └──┘                   └──┘│              │
│              │    [ P ][ R ][ N ][ D ]    │              │
│  Page 1:     │                            │  Battery bar │
│  range       │                            │              │
│  total_km    │                            │              │
│  avg_consump.│                            │              │
├──────────────┴────────────────────────────┴──────────────┤
│  range remaining   │   trip distance            FPS      │
└────────────────────────────────────────────────────────────┘
```

## CAN Signal Map

| CAN ID | Signal | Bits | Scale | Offset |
|--------|--------|------|-------|--------|
| 0x100 | speed | 0–15 | 0.1 | 0 |
| 0x100 | acceleration | 16–23 | 0.5 | 0 |
| 0x101 | battery | 0–7 | 1 | 0 |
| 0x102 | motor_temp | 0–7 | 1 | −40 |
| 0x103 | current | 0–15 | 0.1 | 0 |
| 0x104 | consumption | 0–15 | 0.1 | 0 |
