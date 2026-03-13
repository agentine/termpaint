"""Environment variable detection for color support."""

from __future__ import annotations

import os
import platform


def is_no_color() -> bool:
    """Check if NO_COLOR environment variable is set."""
    return "NO_COLOR" in os.environ


def is_force_color() -> bool:
    """Check if FORCE_COLOR environment variable is set."""
    return "FORCE_COLOR" in os.environ


def detect_color_support() -> int:
    """Detect the level of color support.

    Returns:
        0: No color support
        1: 16 colors (basic ANSI)
        2: 256 colors
        3: True color (24-bit)
    """
    if is_no_color():
        return 0

    if is_force_color():
        return 3

    # Check COLORTERM
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return 3

    # Check TERM
    term = os.environ.get("TERM", "").lower()
    if "256color" in term:
        return 2
    if term in ("xterm", "screen", "vt100", "linux", "ansi"):
        return 1

    # Windows
    if platform.system() == "Windows":
        # Windows 10 1607+ supports true color
        try:
            version = platform.version()
            parts = version.split(".")
            if len(parts) >= 3 and int(parts[2]) >= 14393:
                return 3
        except (ValueError, IndexError):
            pass
        return 1

    # Default: if connected to a terminal, assume basic color
    import sys
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        return 1

    return 0
