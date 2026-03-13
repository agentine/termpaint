"""termpaint — Drop-in replacement for colorama."""

from __future__ import annotations

from .ansi import (
    Fore,
    Back,
    Style,
    Cursor,
    code_to_chars,
    set_title,
    clear_screen,
    clear_line,
    CSI,
    OSC,
    BEL,
)

__all__ = [
    "init",
    "deinit",
    "reinit",
    "just_fix_windows_console",
    "colorama_text",
    "Fore",
    "Back",
    "Style",
    "Cursor",
    "code_to_chars",
    "set_title",
    "clear_screen",
    "clear_line",
    "CSI",
    "OSC",
    "BEL",
]

__version__ = "0.1.0"


def init(
    autoreset: bool = False,
    convert: bool | None = None,
    strip: bool | None = None,
    wrap: bool = True,
) -> None:
    """Initialize termpaint. Wraps stdout/stderr on Windows."""
    # Stub — full implementation in Phase 4
    pass


def deinit() -> None:
    """Undo the effects of init()."""
    pass


def reinit() -> None:
    """Re-initialize after deinit()."""
    pass


def just_fix_windows_console() -> None:
    """Enable ANSI support on Windows. No-op on POSIX. Idempotent."""
    pass


class _ColoramaText:
    """Context manager for colorama_text()."""

    def __init__(self, **kwargs: object) -> None:
        self._kwargs = kwargs

    def __enter__(self) -> "_ColoramaText":
        init()
        return self

    def __exit__(self, *args: object) -> None:
        deinit()


def colorama_text(**kwargs: object) -> _ColoramaText:
    """Context manager that calls init() on enter and deinit() on exit."""
    return _ColoramaText(**kwargs)
