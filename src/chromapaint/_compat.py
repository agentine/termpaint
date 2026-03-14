"""Compatibility shim: ``import chromapaint as colorama``."""

from __future__ import annotations

# Re-export everything so existing code using ``import colorama`` can switch
# to ``import chromapaint as colorama`` with zero changes.
from chromapaint import (  # noqa: F401
    Fore,
    Back,
    Style,
    Cursor,
    init,
    deinit,
    reinit,
    just_fix_windows_console,
    colorama_text,
)
