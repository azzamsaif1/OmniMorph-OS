"""Behaviour Analyzer — keyboard & mouse activity patterns.

Tracks typing speed, error rate (backspace frequency), mouse jitter,
idle gaps, and scroll behaviour to infer cognitive load.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field

from backend.utils.logger import log


@dataclass
class BehaviorMetrics:
    """Aggregated keyboard / mouse signals over a time window."""

    typing_speed_cpm: float = 0.0       # characters per minute
    error_rate: float = 0.0             # backspace ratio
    idle_gap_sec: float = 0.0           # longest idle gap in window
    mouse_velocity: float = 0.0         # avg pixels/sec
    mouse_jitter: float = 0.0           # stddev of velocity
    scroll_speed: float = 0.0           # scroll events per minute
    click_rate: float = 0.0             # clicks per minute
    activity_score: float = 0.0         # 0 = idle, 1 = very active


@dataclass
class _KeyEvent:
    key: str
    timestamp: float


@dataclass
class _MouseEvent:
    x: float
    y: float
    timestamp: float


class BehaviorAnalyzer:
    """Accumulates raw input events and produces ``BehaviorMetrics``."""

    def __init__(self, window_sec: float = 60.0) -> None:
        self._window = window_sec
        self._keys: deque[_KeyEvent] = deque()
        self._mouse: deque[_MouseEvent] = deque()
        self._scrolls: deque[float] = deque()
        self._clicks: deque[float] = deque()

    # -- ingestion ----------------------------------------------------------

    def record_keystroke(self, key: str) -> None:
        now = time.monotonic()
        self._keys.append(_KeyEvent(key=key, timestamp=now))
        self._prune()

    def record_mouse_move(self, x: float, y: float) -> None:
        now = time.monotonic()
        self._mouse.append(_MouseEvent(x=x, y=y, timestamp=now))
        self._prune()

    def record_scroll(self) -> None:
        self._scrolls.append(time.monotonic())
        self._prune()

    def record_click(self) -> None:
        self._clicks.append(time.monotonic())
        self._prune()

    # -- analysis -----------------------------------------------------------

    def compute_metrics(self) -> BehaviorMetrics:
        self._prune()
        now = time.monotonic()
        window_min = max(self._window / 60.0, 1e-6)

        # Typing speed & error rate
        total_keys = len(self._keys)
        backspaces = sum(1 for k in self._keys if k.key in ("backspace", "delete"))
        cpm = total_keys / window_min if total_keys else 0.0
        err = backspaces / total_keys if total_keys else 0.0

        # Idle gap
        idle_gap = 0.0
        key_times = [k.timestamp for k in self._keys]
        if len(key_times) >= 2:
            gaps = [key_times[i + 1] - key_times[i] for i in range(len(key_times) - 1)]
            idle_gap = max(gaps)

        # Mouse velocity & jitter
        velocities: list[float] = []
        mouse_list = list(self._mouse)
        for i in range(1, len(mouse_list)):
            dx = mouse_list[i].x - mouse_list[i - 1].x
            dy = mouse_list[i].y - mouse_list[i - 1].y
            dt = mouse_list[i].timestamp - mouse_list[i - 1].timestamp
            if dt > 0:
                velocities.append((dx**2 + dy**2) ** 0.5 / dt)

        import numpy as np

        avg_vel = float(np.mean(velocities)) if velocities else 0.0
        jitter = float(np.std(velocities)) if velocities else 0.0

        scroll_rate = len(self._scrolls) / window_min
        click_rate = len(self._clicks) / window_min

        # Activity score: normalised composite
        activity = min(
            1.0, (cpm / 300.0) * 0.4 + (avg_vel / 1000.0) * 0.3 + (click_rate / 60.0) * 0.3
        )

        metrics = BehaviorMetrics(
            typing_speed_cpm=cpm,
            error_rate=err,
            idle_gap_sec=idle_gap,
            mouse_velocity=avg_vel,
            mouse_jitter=jitter,
            scroll_speed=scroll_rate,
            click_rate=click_rate,
            activity_score=activity,
        )
        log.debug("behavior.metrics", cpm=cpm, err=err, activity=activity)
        return metrics

    # -- helpers ------------------------------------------------------------

    def _prune(self) -> None:
        cutoff = time.monotonic() - self._window
        while self._keys and self._keys[0].timestamp < cutoff:
            self._keys.popleft()
        while self._mouse and self._mouse[0].timestamp < cutoff:
            self._mouse.popleft()
        while self._scrolls and self._scrolls[0] < cutoff:
            self._scrolls.popleft()
        while self._clicks and self._clicks[0] < cutoff:
            self._clicks.popleft()

    def reset(self) -> None:
        self._keys.clear()
        self._mouse.clear()
        self._scrolls.clear()
        self._clicks.clear()
