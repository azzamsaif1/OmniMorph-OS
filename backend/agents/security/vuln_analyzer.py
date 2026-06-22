"""Vulnerability analysis agent — correlates scan results with CVE database."""

import ctypes
import json
from pathlib import Path
from typing import Any

LIB_PATH = Path(__file__).parent.parent / "c_libs" / "lib" / "libvuln.so"

_lib = None


def _load_lib():
    global _lib
    if _lib is None:
        if not LIB_PATH.exists():
            raise FileNotFoundError(
                f"libvuln.so not found at {LIB_PATH}. Run 'make' in backend/agents/c_libs/"
            )
        _lib = ctypes.CDLL(str(LIB_PATH))
        # analyze_service(service, banner, port, result_json, buffer_size) -> int
        _lib.analyze_service.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
            ctypes.c_char_p, ctypes.c_int
        ]
        _lib.analyze_service.restype = ctypes.c_int
        # correlate_scan_with_cves(scan_json, result_json, buffer_size) -> int
        _lib.correlate_scan_with_cves.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
        ]
        _lib.correlate_scan_with_cves.restype = ctypes.c_int
        # calculate_risk_score(open_ports, critical, high, medium) -> float
        _lib.calculate_risk_score.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        _lib.calculate_risk_score.restype = ctypes.c_float
    return _lib


def analyze_service(service: str, banner: str, port: int) -> dict[str, Any]:
    """Analyze a specific service for known vulnerabilities."""
    lib = _load_lib()
    buf = ctypes.create_string_buffer(32768)
    lib.analyze_service(service.encode(), banner.encode(), port, buf, 32768)
    return json.loads(buf.value.decode())


def correlate_scan(scan_results: dict) -> dict[str, Any]:
    """Correlate full scan results with CVE database."""
    lib = _load_lib()
    scan_json = json.dumps(scan_results).encode()
    buf = ctypes.create_string_buffer(65536)
    lib.correlate_scan_with_cves(scan_json, buf, 65536)
    return json.loads(buf.value.decode())


def calculate_risk_score(
    open_ports: int, critical_vulns: int, high_vulns: int, medium_vulns: int
) -> float:
    """Calculate overall risk score (0-10)."""
    lib = _load_lib()
    return lib.calculate_risk_score(open_ports, critical_vulns, high_vulns, medium_vulns)
