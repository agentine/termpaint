"""Initialization and deinitialization of termpaint."""

from __future__ import annotations

import atexit
import platform
import sys
import threading
from typing import Any

from .ansi import Style
from .ansitowin32 import AnsiToWin32

_lock = threading.Lock()
_original_stdout: Any = None
_original_stderr: Any = None
_wrapped = False
_fixed = False


def init(
    autoreset: bool = False,
    convert: bool | None = None,
    strip: bool | None = None,
    wrap: bool = True,
) -> None:
    """Initialize termpaint. On Windows, wraps stdout/stderr."""
    global _original_stdout, _original_stderr, _wrapped

    with _lock:
        if not wrap:
            return

        _original_stdout = sys.stdout
        _original_stderr = sys.stderr

        sys.stdout = AnsiToWin32(  # type: ignore[assignment]
            _original_stdout,
            convert=convert,
            strip=strip,
            autoreset=autoreset,
        ).stream
        sys.stderr = AnsiToWin32(  # type: ignore[assignment]
            _original_stderr,
            convert=convert,
            strip=strip,
            autoreset=autoreset,
        ).stream
        _wrapped = True


def deinit() -> None:
    """Restore original stdout/stderr."""
    global _original_stdout, _original_stderr, _wrapped

    with _lock:
        if not _wrapped:
            return
        if _original_stdout is not None:
            sys.stdout = _original_stdout
        if _original_stderr is not None:
            sys.stderr = _original_stderr
        _original_stdout = None
        _original_stderr = None
        _wrapped = False


def reinit() -> None:
    """Re-initialize after deinit()."""
    with _lock:
        if _wrapped:
            return
    init()


def just_fix_windows_console() -> None:
    """Enable ANSI support on Windows. No-op on POSIX. Idempotent."""
    global _fixed

    with _lock:
        if _fixed:
            return
        _fixed = True

    if platform.system() != "Windows":
        return

    # Try VT processing first (modern Windows 10+)
    from .win32 import enable_vt_processing
    stdout_ok = enable_vt_processing(sys.stdout.fileno()) if hasattr(sys.stdout, "fileno") else False
    stderr_ok = enable_vt_processing(sys.stderr.fileno()) if hasattr(sys.stderr, "fileno") else False

    if not stdout_ok or not stderr_ok:
        # Fall back to stream wrapping
        init()


def _reset_all() -> None:
    """Reset all styles on exit."""
    try:
        sys.stdout.write(Style.RESET_ALL)
    except Exception:
        pass


atexit.register(_reset_all)
