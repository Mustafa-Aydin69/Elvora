"""
ui.py — Pygame rendering layer.
"""

import pygame
import math
import time
from typing import Tuple

from logic import VehicleState, State, state_color

# ---------------------------------------------------------------------------
# Renkler
# ---------------------------------------------------------------------------
C_BG          = (10,  12,  18)
C_PANEL_BG    = (15,  18,  28)
C_DIVIDER     = (30,  35,  50)
C_TEXT        = (220, 225, 240)
C_TEXT_DIM    = (90,  100, 130)
C_TEXT_LABEL  = (130, 140, 170)
C_ACCENT      = (0,   200, 255)
C_ACCENT2     = (0,   255, 180)
C_GREEN       = (72,  199, 142)
C_YELLOW      = (255, 193,   7)
C_RED         = (255,  82,  82)
C_SPEED       = (255, 255, 255)
C_GEAR_ACTIVE = (0,   200, 255)
C_GEAR_IDLE   = (40,   45,  65)
C_BAR_TRACK   = (25,   30,  45)

W, H     = 1280, 480
LEFT_W   = int(W * 0.25)           # 320
CENTER_W = int(W * 0.50)           # 640
RIGHT_W  = W - LEFT_W - CENTER_W   # 320

LEFT_X   = 0
CENTER_X = LEFT_W
RIGHT_X  = LEFT_W + CENTER_W

FPS   = 30
GEARS = ["P", "R", "N", "D"]

BOTTOM_H = 52   # alt şerit yüksekliği


# ---------------------------------------------------------------------------
# Font önbelleği
# ---------------------------------------------------------------------------
class Fonts:
    _cache: dict = {}

    @classmethod
    def get(cls, name: str, size: int) -> pygame.font.Font:
        key = (name, size)
        if key not in cls._cache:
            try:
                cls._cache[key] = pygame.font.SysFont(name, size, bold=False)
            except Exception:
                cls._cache[key] = pygame.font.SysFont("monospace", size)
        return cls._cache[key]

    @classmethod
    def mono(cls, size: int) -> pygame.font.Font:
        return cls.get("monospace", size)


# ---------------------------------------------------------------------------
# Ana UI sınıfı
# ---------------------------------------------------------------------------
class DashboardUI:

    def __init__(self, surface: pygame.Surface):
        self._surf = surface
        self._page = 0
        self._last_page_toggle = time.time()
        self._gear_rects: dict = {}

    # ------------------------------------------------------------------
    # Her kare çağrılır
    # ------------------------------------------------------------------
    def render(self, vs: VehicleState, fps: float) -> None:
        self._surf.fill(C_BG)
        self._draw_left(vs)
        self._draw_center(vs)
        self._draw_right(vs)
        self._draw_bottom(vs, fps)
        self._draw_dividers()
        if not vs.can_alive:
            self._draw_no_signal()

    # ------------------------------------------------------------------
    # Bölücü çizgiler
    # ------------------------------------------------------------------
    def _draw_dividers(self) -> None:
        content_h = H - BOTTOM_H
        pygame.draw.line(self._surf, C_DIVIDER, (CENTER_X, 0), (CENTER_X, content_h), 1)
        pygame.draw.line(self._surf, C_DIVIDER, (RIGHT_X,  0), (RIGHT_X,  content_h), 1)
        pygame.draw.line(self._surf, C_DIVIDER, (0, content_h), (W, content_h), 1)

    # ------------------------------------------------------------------
    # SOL PANEL
    # ------------------------------------------------------------------
    def _draw_left(self, vs: VehicleState) -> None:
        x0 = LEFT_X
        w  = LEFT_W
        content_h = H - BOTTOM_H
        pad = 14

        pygame.draw.rect(self._surf, C_PANEL_BG, (x0, 0, w, content_h))

        # Sayfa otomatik geçişi (8 saniyede bir)
        now = time.time()
        if now - self._last_page_toggle > 8.0:
            self._last_page_toggle = now
            self._page = 1 - self._page

        # Başlık
        page_names = ["BATARYA", "TELEMETRİ"]
        self._text(page_names[self._page], Fonts.mono(10), C_TEXT_DIM, x0 + pad, 8)
        dot = "● ○" if self._page == 0 else "○ ●"
        self._text(dot, Fonts.mono(9), C_ACCENT, x0 + w - 45, 10)

        y = 32

        if self._page == 0:
            # ── Sayfa 0: Batarya bilgileri ──────────────────────────────
            y = self._metric(x0, y, w, pad,
                             "PAKET GERİLİMİ",
                             f"{vs.pack_voltage:.1f}", "V",
                             vs.pack_voltage, 300, 430)

            y = self._metric(x0, y, w, pad,
                             "HÜCRE MIN",
                             f"{vs.cell_min_voltage:.3f}", "V",
                             vs.cell_min_voltage, 3.0, 4.2,
                             warn=3.3, crit=3.1, invert=True)

            y = self._metric(x0, y, w, pad,
                             "HÜCRE MAX",
                             f"{vs.cell_max_voltage:.3f}", "V",
                             vs.cell_max_voltage, 3.0, 4.2,
                             warn=4.0, crit=4.15)

            y = self._metric(x0, y, w, pad,
                             "SICAK HÜCRE",
                             f"{vs.cell_max_temp:.0f}", "°C",
                             vs.cell_max_temp, 0, 65,
                             warn=45, crit=55)

            y = self._metric(x0, y, w, pad,
                             "SOC",
                             f"{vs.battery:.0f}", "%",
                             vs.battery, 0, 100,
                             warn=20, crit=10, invert=True,
                             state=vs.battery_state)

            # ── Sayfa 1: Telemetri ──────────────────────────────────────
            y = self._metric(x0, y, w, pad,
                             "MOTOR SICAKLIĞI",
                             f"{vs.motor_temp:.0f}", "°C",
                             vs.motor_temp, 0, 130,
                             warn=90, crit=110,
                             state=vs.motor_state)
        else:
            y = self._metric(x0, y, w, pad,
                             "AKIM",
                             f"{vs.current:.0f}", "A",
                             vs.current, 0, 500,
                             warn=350, crit=450)

            y = self._metric(x0, y, w, pad,
                             "TÜKETİM",
                             f"{vs.consumption:.1f}", "kWh/100",
                             vs.consumption, 0, 40,
                             warn=25, crit=35)

            y = self._metric(x0, y, w, pad,
                             "TAHMINI MENZİL",
                             f"{vs.range_km:.0f}", "km",
                             vs.range_km, 0, 600)

    def _metric(self, x0, y, w, pad,
                label, val_str, unit,
                value, vmin, vmax,
                warn=None, crit=None,
                invert=False,
                state: State = State.NORMAL) -> int:
        """Etiket + değer + mini bar çizer. Yeni y konumunu döndürür."""
        bw = w - pad * 2

        # Etiket
        self._text(label, Fonts.mono(9), C_TEXT_LABEL, x0 + pad, y)
        y += 15

        # Değer
        color = state_color(state)
        self._text(val_str, Fonts.mono(20), color, x0 + pad, y)
        self._text(unit, Fonts.mono(9), C_TEXT_DIM, x0 + pad + 82, y + 7)
        y += 24

        # Mini bar
        bar_h = 4
        pygame.draw.rect(self._surf, C_BAR_TRACK,
                         pygame.Rect(x0 + pad, y, bw, bar_h), border_radius=2)
        span = vmax - vmin if vmax != vmin else 1
        frac = _clamp((value - vmin) / span, 0.0, 1.0)

        if warn is not None and crit is not None:
            if invert:
                fill_col = _gradient_color(1 - frac,
                                           1 - warn / vmax,
                                           1 - crit / vmax)
            else:
                fill_col = _gradient_color(frac, warn / vmax, crit / vmax)
        else:
            fill_col = C_ACCENT

        fill_w = int(bw * frac)
        if fill_w > 0:
            pygame.draw.rect(self._surf, fill_col,
                             pygame.Rect(x0 + pad, y, fill_w, bar_h),
                             border_radius=2)

        y += bar_h + 12
        return y

    # ------------------------------------------------------------------
    # ORTA PANEL
    # ------------------------------------------------------------------
    def _draw_center(self, vs: VehicleState) -> None:
        x0 = CENTER_X
        w  = CENTER_W
        content_h = H - BOTTOM_H

        # Hız (büyük rakam)
        speed_str = f"{vs.speed:05.1f}"
        font_big  = Fonts.mono(100)
        ts        = font_big.render(speed_str, True, C_SPEED)
        ts_x      = x0 + (w - ts.get_width()) // 2
        ts_y      = 50
        self._surf.blit(ts, (ts_x, ts_y))

        self._text("km/h", Fonts.mono(13), C_TEXT_DIM,
                   x0 + (w + ts.get_width()) // 2 - 48, ts_y + 80)

        # Dikey barlar
        bar_w = 26
        bar_h = 180
        bar_y = 70
        gap   = 28

        # Sol bar — tüketim
        self._draw_vbar(x0 + gap, bar_y, bar_w, bar_h,
                        vs.consumption, 0, 40, label="kWh", warn=0.6, crit=0.85)

        # Sağ bar — ivme (±)
        self._draw_vbar_bipolar(x0 + w - gap - bar_w, bar_y, bar_w, bar_h,
                                vs.acceleration, -1.5, 1.5, label="g")

        # Vites seçici
        self._draw_gears(x0, w, content_h, vs.gear)

    def _draw_vbar(self, x, y, bw, bh, value, vmin, vmax,
                   label="", warn=0.6, crit=0.85) -> None:
        pygame.draw.rect(self._surf, C_BAR_TRACK, (x, y, bw, bh), border_radius=6)
        frac   = _clamp((value - vmin) / (vmax - vmin), 0, 1)
        fill_h = int(bh * frac)
        color  = _gradient_color(frac, warn, crit)
        if fill_h > 0:
            pygame.draw.rect(self._surf, color,
                             pygame.Rect(x, y + bh - fill_h, bw, fill_h),
                             border_radius=6)
        for pct in (0.25, 0.5, 0.75):
            ty = y + bh - int(bh * pct)
            pygame.draw.line(self._surf, C_DIVIDER, (x - 4, ty), (x + bw + 4, ty), 1)
        self._text(label, Fonts.mono(9), C_TEXT_DIM, x, y + bh + 5)
        self._text(f"{value:.1f}", Fonts.mono(9), C_TEXT_DIM, x - 2, y + bh + 17)

    def _draw_vbar_bipolar(self, x, y, bw, bh, value, vmin, vmax, label="") -> None:
        pygame.draw.rect(self._surf, C_BAR_TRACK, (x, y, bw, bh), border_radius=6)
        mid_y  = y + bh // 2
        frac   = _clamp((value - vmin) / (vmax - vmin), 0, 1)
        if frac >= 0.5:
            fill_h = int(bh * (frac - 0.5))
            pygame.draw.rect(self._surf, C_ACCENT2,
                             pygame.Rect(x, mid_y - fill_h, bw, fill_h), border_radius=4)
        else:
            fill_h = int(bh * (0.5 - frac))
            pygame.draw.rect(self._surf, C_RED,
                             pygame.Rect(x, mid_y, bw, fill_h), border_radius=4)
        pygame.draw.line(self._surf, C_ACCENT, (x - 4, mid_y), (x + bw + 4, mid_y), 1)
        self._text(label, Fonts.mono(9), C_TEXT_DIM, x, y + bh + 5)
        self._text(f"{value:+.2f}", Fonts.mono(9), C_TEXT_DIM, x - 4, y + bh + 17)

    def _draw_gears(self, panel_x, panel_w, panel_h, active_gear: str) -> None:
        btn_w   = 52
        btn_h   = 44
        spacing = 8
        total_w = 4 * btn_w + 3 * spacing
        start_x = panel_x + (panel_w - total_w) // 2
        y       = panel_h - btn_h - 20

        for i, gear in enumerate(GEARS):
            gx       = start_x + i * (btn_w + spacing)
            active   = gear == active_gear
            bg_col   = C_GEAR_ACTIVE if active else C_GEAR_IDLE
            txt_col  = C_BG          if active else C_TEXT_DIM
            rect     = pygame.Rect(gx, y, btn_w, btn_h)
            pygame.draw.rect(self._surf, bg_col, rect, border_radius=8)
            if not active:
                pygame.draw.rect(self._surf, C_DIVIDER, rect, width=1, border_radius=8)
            ls = Fonts.mono(20).render(gear, True, txt_col)
            self._surf.blit(ls, (gx + (btn_w - ls.get_width()) // 2,
                                  y  + (btn_h - ls.get_height()) // 2))
            self._gear_rects[gear] = rect

    # ------------------------------------------------------------------
    # SAĞ PANEL
    # ------------------------------------------------------------------
    def _draw_right(self, vs: VehicleState) -> None:
        x0 = RIGHT_X
        w  = RIGHT_W
        content_h = H - BOTTOM_H

        pygame.draw.rect(self._surf, C_PANEL_BG, (x0, 0, w, content_h))

        # Kamera alanı
        cam_h = content_h - 70
        pygame.draw.rect(self._surf, (18, 22, 35),
                         (x0 + 12, 10, w - 24, cam_h - 10), border_radius=8)

        cx  = x0 + w // 2
        cy  = 10 + (cam_h - 10) // 2
        r   = 20
        col = (50, 60, 90)
        pygame.draw.circle(self._surf, col, (cx, cy), r, 1)
        pygame.draw.line(self._surf, col, (cx - r - 8, cy), (cx + r + 8, cy), 1)
        pygame.draw.line(self._surf, col, (cx, cy - r - 8), (cx, cy + r + 8), 1)
        self._text("ARKA KAMERA", Fonts.mono(9), C_TEXT_DIM, x0 + 18, cy + r + 12)

        # Batarya barı (sağ alt)
        by    = content_h - 52
        bx    = x0 + 14
        bw_   = w - 28
        self._text("BATARYA SOC", Fonts.mono(8), C_TEXT_DIM, bx, by)
        by += 13
        pygame.draw.rect(self._surf, C_BAR_TRACK, pygame.Rect(bx, by, bw_, 14), border_radius=4)
        frac    = _clamp(vs.battery / 100.0, 0, 1)
        bat_col = state_color(vs.battery_state)
        fill_w  = int(bw_ * frac)
        if fill_w > 0:
            pygame.draw.rect(self._surf, bat_col,
                             pygame.Rect(bx, by, fill_w, 14), border_radius=4)
        self._text(f"{vs.battery:.0f}%", Fonts.mono(10), bat_col,
                   bx + bw_ - 34, by)

    # ------------------------------------------------------------------
    # ALT ŞERİT (tam genişlik)
    # ------------------------------------------------------------------
    def _draw_bottom(self, vs: VehicleState, fps: float) -> None:
        by = H - BOTTOM_H
        pygame.draw.rect(self._surf, C_PANEL_BG, (0, by, W, BOTTOM_H))

        items = [
            ("MENZİL",    f"{vs.range_km:.0f} km",           C_ACCENT),
            ("TRIP",      f"{vs.total_km:.1f} km",            C_TEXT),
            ("PAKET V",   f"{vs.pack_voltage:.1f} V",         C_ACCENT2),
            ("HÜCRE MIN", f"{vs.cell_min_voltage:.3f} V",     C_GREEN),
            ("HÜCRE MAX", f"{vs.cell_max_voltage:.3f} V",     C_YELLOW),
            ("SICAK H.",  f"{vs.cell_max_temp:.0f} °C",       C_YELLOW),
            ("SOC",       f"{vs.battery:.0f} %",              state_color(vs.battery_state)),
        ]

        col_w = (W - 80) // len(items)
        for i, (lbl, val, col) in enumerate(items):
            bx = 20 + i * col_w
            self._text(lbl, Fonts.mono(8),  C_TEXT_DIM, bx, by + 6)
            self._text(val, Fonts.mono(16), col,        bx, by + 20)

        # FPS sağ köşe
        self._text(f"{fps:.0f} fps", Fonts.mono(8), C_TEXT_DIM, W - 50, by + 36)

    # ------------------------------------------------------------------
    # Sinyalsiz uyarısı
    # ------------------------------------------------------------------
    def _draw_no_signal(self) -> None:
        overlay = pygame.Surface((W, 26), pygame.SRCALPHA)
        overlay.fill((180, 0, 0, 150))
        self._surf.blit(overlay, (0, 0))
        self._text("⚠  CAN SİNYALİ YOK — SİMÜLATÖR MODU",
                   Fonts.mono(11), (255, 210, 210), W // 2 - 155, 5)

    # ------------------------------------------------------------------
    # Yardımcı
    # ------------------------------------------------------------------
    def _text(self, txt: str, font: pygame.font.Font,
              color: Tuple[int, int, int], x: int, y: int) -> None:
        self._surf.blit(font.render(str(txt), True, color), (x, y))


# ---------------------------------------------------------------------------
# Yardımcı fonksiyonlar
# ---------------------------------------------------------------------------
def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _gradient_color(frac: float, warn: float = 0.6, crit: float = 0.85) -> Tuple:
    if frac < warn:
        t = frac / warn if warn > 0 else 0
        return _lerp_color((72, 199, 142), (255, 193, 7), t)
    elif frac < crit:
        t = (frac - warn) / (crit - warn) if crit != warn else 1
        return _lerp_color((255, 193, 7), (255, 82, 82), t)
    else:
        return (255, 82, 82)


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
