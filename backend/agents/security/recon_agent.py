"""Network reconnaissance agent — Python wrapper around C-based port scanner."""

import ctypes
import json
from pathlib import Path
from typing import Any

LIB_PATH = Path(__file__).parent.parent / "c_libs" / "lib" / "librecon.so"

_lib = None


def _load_lib():
    global _lib
    if _lib is None:
        if not LIB_PATH.exists():
            raise FileNotFoundError(
                f"librecon.so not found at {LIB_PATH}. Run 'make' in backend/agents/c_libs/"
            )
        _lib = ctypes.CDLL(str(LIB_PATH))
        # scan_common_ports(target_ip, result_json, buffer_size) -> int
        _lib.scan_common_ports.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
        ]
        _lib.scan_common_ports.restype = ctypes.c_int
        # scan_port_range(target_ip, start, end, result_json, buffer_size) -> int
        _lib.scan_port_range.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_char_p, ctypes.c_int
        ]
        _lib.scan_port_range.restype = ctypes.c_int
        # grab_banner(target_ip, port, banner, banner_size) -> int
        _lib.grab_banner.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int
        ]
        _lib.grab_banner.restype = ctypes.c_int
    return _lib


def scan_common_ports(target_ip: str) -> dict[str, Any]:
    """Scan common ports (21,22,23,25,53,80,...) on target IP."""
    lib = _load_lib()
    buf = ctypes.create_string_buffer(65536)
    lib.scan_common_ports(target_ip.encode(), buf, 65536)
    return json.loads(buf.value.decode())


def scan_port_range(target_ip: str, start: int = 1, end: int = 1024) -> dict[str, Any]:
    """Scan a specific port range on target IP."""
    lib = _load_lib()
    buf = ctypes.create_string_buffer(65536)
    lib.scan_port_range(target_ip.encode(), start, end, buf, 65536)
    return json.loads(buf.value.decode())


def grab_banner(target_ip: str, port: int) -> str:
    """Grab service banner from target:port."""
    lib = _load_lib()
    buf = ctypes.create_string_buffer(4096)
    result = lib.grab_banner(target_ip.encode(), port, buf, 4096)
    if result == 0:
        return buf.value.decode()
    return ""
