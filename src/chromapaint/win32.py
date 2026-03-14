"""Win32 Console API wrappers via ctypes.

All functions gracefully return None/False on non-Windows platforms.
"""

from __future__ import annotations

import sys
from typing import Any, NamedTuple

# Win32 constants
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

_windll: Any = None
_handles: dict[int, Any] = {}


class COORD(NamedTuple):
    X: int
    Y: int


class SMALL_RECT(NamedTuple):
    Left: int
    Top: int
    Right: int
    Bottom: int


class CONSOLE_SCREEN_BUFFER_INFO(NamedTuple):
    dwSize: COORD
    dwCursorPosition: COORD
    wAttributes: int
    srWindow: SMALL_RECT
    dwMaximumWindowSize: COORD


def _init_kernel32() -> Any:
    """Lazily import and cache kernel32 handle."""
    global _windll
    if _windll is not None:
        return _windll
    try:
        import ctypes
        _windll = ctypes.windll.kernel32  # type: ignore[attr-defined]
        return _windll
    except (ImportError, AttributeError):
        return None


def _get_handle(stream_id: int) -> Any:
    """Get a Win32 console handle for a stream id."""
    if stream_id in _handles:
        return _handles[stream_id]
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return None
    handle = kernel32.GetStdHandle(stream_id)
    _handles[stream_id] = handle
    return handle


def _stream_id(on_stderr: bool = False) -> int:
    """Return the Win32 standard handle ID."""
    return STD_ERROR_HANDLE if on_stderr else STD_OUTPUT_HANDLE


def winapi_test() -> bool:
    """Return True if Win32 console API is available."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return False
    try:
        handle = _get_handle(STD_OUTPUT_HANDLE)
        import ctypes
        csbi = ctypes.create_string_buffer(22)
        return bool(kernel32.GetConsoleScreenBufferInfo(handle, csbi))
    except Exception:
        return False


def GetConsoleScreenBufferInfo(stream_id: int) -> CONSOLE_SCREEN_BUFFER_INFO | None:
    """Get console screen buffer info."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return None
    try:
        import ctypes
        handle = _get_handle(stream_id)
        csbi = ctypes.create_string_buffer(22)
        if not kernel32.GetConsoleScreenBufferInfo(handle, csbi):
            return None
        result = ctypes.cast(csbi, ctypes.POINTER(ctypes.c_short * 11)).contents
        return CONSOLE_SCREEN_BUFFER_INFO(
            dwSize=COORD(result[0], result[1]),
            dwCursorPosition=COORD(result[2], result[3]),
            wAttributes=result[4],
            srWindow=SMALL_RECT(result[5], result[6], result[7], result[8]),
            dwMaximumWindowSize=COORD(result[9], result[10]),
        )
    except Exception:
        return None


def SetConsoleTextAttribute(stream_id: int, attrs: int) -> None:
    """Set console text attributes."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return
    handle = _get_handle(stream_id)
    kernel32.SetConsoleTextAttribute(handle, attrs)


def SetConsoleCursorPosition(
    stream_id: int,
    position: tuple[int, int],
    adjust: bool = True,
) -> None:
    """Set cursor position. Position is (x, y)."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return
    handle = _get_handle(stream_id)
    x, y = position
    if adjust:
        # Adjust for scrollback offset
        csbi = GetConsoleScreenBufferInfo(stream_id)
        if csbi:
            y += csbi.srWindow.Top
    # COORD is packed as a DWORD: low word = X, high word = Y
    coord = (y << 16) | (x & 0xFFFF)
    kernel32.SetConsoleCursorPosition(handle, coord)


def FillConsoleOutputCharacter(
    stream_id: int, char: str, length: int, start: tuple[int, int]
) -> int:
    """Fill console with a character."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return 0
    try:
        import ctypes
        handle = _get_handle(stream_id)
        coord = (start[1] << 16) | (start[0] & 0xFFFF)
        num_written = ctypes.c_ulong(0)
        kernel32.FillConsoleOutputCharacterA(
            handle, ctypes.c_char(char.encode()), length, coord,
            ctypes.byref(num_written),
        )
        return num_written.value
    except Exception:
        return 0


def FillConsoleOutputAttribute(
    stream_id: int, attr: int, length: int, start: tuple[int, int]
) -> int:
    """Fill console with an attribute."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return 0
    try:
        import ctypes
        handle = _get_handle(stream_id)
        coord = (start[1] << 16) | (start[0] & 0xFFFF)
        num_written = ctypes.c_ulong(0)
        kernel32.FillConsoleOutputAttribute(
            handle, attr, length, coord,
            ctypes.byref(num_written),
        )
        return num_written.value
    except Exception:
        return 0


def SetConsoleTitle(title: str) -> None:
    """Set the console window title."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return
    try:
        kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


def GetConsoleMode(handle: Any) -> int:
    """Get the console mode for a handle."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return 0
    try:
        import ctypes
        mode = ctypes.c_ulong(0)
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        return mode.value
    except Exception:
        return 0


def SetConsoleMode(handle: Any, mode: int) -> None:
    """Set the console mode for a handle."""
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return
    try:
        kernel32.SetConsoleMode(handle, mode)
    except Exception:
        pass


def enable_vt_processing(fd: int) -> bool:
    """Enable VT processing on a Windows console handle.

    Returns True if VT processing was successfully enabled, False otherwise.
    On non-Windows platforms, always returns False.
    """
    kernel32 = _init_kernel32()
    if kernel32 is None:
        return False
    try:
        import ctypes
        import msvcrt
        handle = msvcrt.get_osfhandle(fd)  # type: ignore[attr-defined]
        mode = ctypes.c_ulong(0)
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        return bool(kernel32.SetConsoleMode(handle, new_mode))
    except Exception:
        return False
