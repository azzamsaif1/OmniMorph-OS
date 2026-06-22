"""Portfolio management agent — C-based Markowitz optimization and risk assessment."""

import ctypes
import json
from pathlib import Path
from typing import Any

LIB_PATH = Path(__file__).parent.parent / "c_libs" / "lib" / "libportfolio.so"

_lib = None


def _load_lib():
    global _lib
    if _lib is None:
        if not LIB_PATH.exists():
            raise FileNotFoundError(
                f"libportfolio.so not found at {LIB_PATH}. Run 'make' in backend/agents/c_libs/"
            )
        _lib = ctypes.CDLL(str(LIB_PATH))
        # optimize_portfolio(assets_json, num_assets, risk_tol, result, buf_size) -> int
        _lib.optimize_portfolio.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_double,
            ctypes.c_char_p, ctypes.c_int
        ]
        _lib.optimize_portfolio.restype = ctypes.c_int
        # calculate_var(value, volatility, confidence, days) -> double
        _lib.calculate_var.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int
        ]
        _lib.calculate_var.restype = ctypes.c_double
        # assess_risk(value, volatility, drawdown, leverage, result, buf_size) -> int
        _lib.assess_risk.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.c_char_p, ctypes.c_int
        ]
        _lib.assess_risk.restype = ctypes.c_int
    return _lib


def optimize_portfolio(
    assets: list[dict], risk_tolerance: float = 0.5
) -> dict[str, Any]:
    """Run mean-variance portfolio optimization."""
    lib = _load_lib()
    assets_json = json.dumps(assets).encode()
    buf = ctypes.create_string_buffer(16384)
    lib.optimize_portfolio(assets_json, len(assets), risk_tolerance, buf, 16384)
    return json.loads(buf.value.decode())


def calculate_var(
    portfolio_value: float,
    volatility: float,
    confidence: float = 0.95,
    holding_days: int = 1,
) -> float:
    """Calculate Value at Risk (parametric method)."""
    lib = _load_lib()
    return lib.calculate_var(portfolio_value, volatility, confidence, holding_days)


def assess_risk(
    portfolio_value: float,
    volatility: float,
    max_drawdown: float = 0.1,
    leverage: float = 1.0,
) -> dict[str, Any]:
    """Comprehensive risk assessment of portfolio."""
    lib = _load_lib()
    buf = ctypes.create_string_buffer(4096)
    lib.assess_risk(portfolio_value, volatility, max_drawdown, leverage, buf, 4096)
    return json.loads(buf.value.decode())
