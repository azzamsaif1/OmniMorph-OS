"""Trading agent — Python wrapper around C-based technical analysis engine."""

import ctypes
import json
from pathlib import Path
from typing import Any

LIB_PATH = Path(__file__).parent.parent / "c_libs" / "lib" / "libtrading.so"

_lib = None


def _load_lib():
    global _lib
    if _lib is None:
        if not LIB_PATH.exists():
            raise FileNotFoundError(
                f"libtrading.so not found at {LIB_PATH}. Run 'make' in backend/agents/c_libs/"
            )
        _lib = ctypes.CDLL(str(LIB_PATH))
        # generate_signals(prices, count, symbol, result_json, buf_size) -> int
        _lib.generate_signals.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int,
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
        ]
        _lib.generate_signals.restype = ctypes.c_int
        # kelly_position_size(win_rate, avg_win, avg_loss, balance) -> double
        _lib.kelly_position_size.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double
        ]
        _lib.kelly_position_size.restype = ctypes.c_double
        # backtest_strategy(prices, count, capital, result_json, buf_size) -> int
        _lib.backtest_strategy.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int,
            ctypes.c_double, ctypes.c_char_p, ctypes.c_int
        ]
        _lib.backtest_strategy.restype = ctypes.c_int
    return _lib


def generate_signals(prices: list[float], symbol: str = "ASSET") -> dict[str, Any]:
    """Generate trading signals from price data using technical analysis."""
    lib = _load_lib()
    n = len(prices)
    c_prices = (ctypes.c_double * n)(*prices)
    buf = ctypes.create_string_buffer(8192)
    lib.generate_signals(c_prices, n, symbol.encode(), buf, 8192)
    return json.loads(buf.value.decode())


def kelly_position_size(
    win_rate: float, avg_win: float, avg_loss: float, account_balance: float
) -> float:
    """Calculate optimal position size using Kelly Criterion (half-Kelly)."""
    lib = _load_lib()
    return lib.kelly_position_size(win_rate, avg_win, avg_loss, account_balance)


def backtest_strategy(prices: list[float], initial_capital: float = 10000.0) -> dict[str, Any]:
    """Backtest RSI+SMA strategy on historical price data."""
    lib = _load_lib()
    n = len(prices)
    c_prices = (ctypes.c_double * n)(*prices)
    buf = ctypes.create_string_buffer(4096)
    lib.backtest_strategy(c_prices, n, initial_capital, buf, 4096)
    return json.loads(buf.value.decode())
