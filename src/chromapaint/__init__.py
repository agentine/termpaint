"""chromapaint — Drop-in replacement for colorama."""

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
from typing import Any

from .initialise import (
    init,
    deinit,
    reinit,
    just_fix_windows_console,
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


class _ColoramaText:
    """Context manager for colorama_text()."""

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = kwargs

    def __enter__(self) -> "_ColoramaText":
        init(**self._kwargs)
        return self

    def __exit__(self, *args: object) -> None:
        deinit()


def colorama_text(**kwargs: Any) -> _ColoramaText:
    """Context manager that calls init() on enter and deinit() on exit."""
    return _ColoramaText(**kwargs)
