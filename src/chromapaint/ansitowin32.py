"""AnsiToWin32 stream wrapper — ANSI parsing, stripping, and conversion."""

from __future__ import annotations

import platform
import re
import sys
from typing import Any, TextIO

from .ansi import Style
from .environ import is_force_color, is_no_color

ANSI_CSI_RE = re.compile(r"\001?\033\[(\d+;)*\d*[A-Za-z]\002?")
ANSI_OSC_RE = re.compile(r"\001?\033\].*?(\007|\033\\)\002?")


class StreamWrapper:
    """Proxy stream that delegates write() to a converter."""

    def __init__(self, wrapped: TextIO, converter: "AnsiToWin32") -> None:
        self._wrapped = wrapped
        self._converter = converter

    def write(self, text: str) -> int:
        self._converter.write(text)
        return len(text)

    def isatty(self) -> bool:
        return self._wrapped.isatty()

    @property
    def closed(self) -> bool:
        return self._wrapped.closed

    def __enter__(self) -> "StreamWrapper":
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def __getattr__(self, name: str) -> Any:
        return getattr(self._wrapped, name)

    def __getstate__(self) -> dict[str, Any]:
        return {"_wrapped": self._wrapped, "_converter": self._converter}

    def __setstate__(self, state: dict[str, Any]) -> None:
        self._wrapped = state["_wrapped"]
        self._converter = state["_converter"]


class AnsiToWin32:
    """Translates ANSI codes to Win32 console API calls (or strips them).

    On non-Windows platforms, this is essentially a pass-through unless
    strip=True is explicitly set.
    """

    ANSI_CSI_RE = ANSI_CSI_RE
    ANSI_OSC_RE = ANSI_OSC_RE

    def __init__(
        self,
        wrapped: TextIO,
        convert: bool | None = None,
        strip: bool | None = None,
        autoreset: bool = False,
    ) -> None:
        self.wrapped = wrapped
        self.autoreset = autoreset
        self.on_stderr = wrapped is sys.__stderr__

        # Determine if we should strip and/or convert.
        # NO_COLOR and FORCE_COLOR environment variables take precedence.
        on_windows = platform.system() == "Windows"
        is_tty = hasattr(wrapped, "isatty") and wrapped.isatty()
        no_color = is_no_color()
        force_color = is_force_color()

        if strip is None:
            if no_color:
                # NO_COLOR: strip all ANSI sequences
                self.strip = True
            elif force_color:
                # FORCE_COLOR: never strip, even if not a TTY
                self.strip = False
            else:
                # Auto-detect: strip if we're on Windows with a real console
                self.strip = on_windows and is_tty and convert is not False
        else:
            self.strip = strip

        if convert is None:
            if no_color:
                # NO_COLOR: do not convert, just strip
                self.convert = False
            else:
                # Auto-detect: convert if on Windows with a real console
                self.convert = on_windows and is_tty
        else:
            self.convert = convert

        self.win32_calls: dict[str, Any] = {}
        self.stream = StreamWrapper(wrapped, self)

        if self.convert:
            self._init_win32()

    def _init_win32(self) -> None:
        """Set up Win32 console dispatch table."""
        try:
            from . import winterm
            wt = winterm.win_term
        except (ImportError, AttributeError):
            self.convert = False
            return

        self.win32_calls = {
            "m": lambda params: self._sgr(wt, params),
            "J": lambda params: wt.erase_screen(params[0] if params else 0, self.on_stderr),
            "K": lambda params: wt.erase_line(params[0] if params else 0, self.on_stderr),
            "H": lambda params: wt.set_cursor_position(
                (params[1] - 1 if len(params) > 1 else 0,
                 params[0] - 1 if params else 0),
                self.on_stderr,
            ),
            "f": lambda params: wt.set_cursor_position(
                (params[1] - 1 if len(params) > 1 else 0,
                 params[0] - 1 if params else 0),
                self.on_stderr,
            ),
            "A": lambda params: wt.cursor_adjust(0, -(params[0] if params else 1), self.on_stderr),
            "B": lambda params: wt.cursor_adjust(0, params[0] if params else 1, self.on_stderr),
            "C": lambda params: wt.cursor_adjust(params[0] if params else 1, 0, self.on_stderr),
            "D": lambda params: wt.cursor_adjust(-(params[0] if params else 1), 0, self.on_stderr),
        }

    def _sgr(self, wt: Any, params: list[int]) -> None:
        """Handle SGR (Select Graphic Rendition) parameters."""
        if not params:
            params = [0]
        for param in params:
            if param == 0:
                wt.reset_all(self.on_stderr)
            elif param == 1:
                wt.style(wt.__class__.__dict__.get("BRIGHT", 0x08), self.on_stderr)
            elif param == 2:
                wt.style(wt.__class__.__dict__.get("DIM", 0x00), self.on_stderr)
            elif param == 22:
                wt.style(wt.__class__.__dict__.get("NORMAL", 0x00), self.on_stderr)
            elif 30 <= param <= 37:
                wt.fore(param - 30, on_stderr=self.on_stderr)
            elif param == 39:
                wt.fore(on_stderr=self.on_stderr)
            elif 40 <= param <= 47:
                wt.back(param - 40, on_stderr=self.on_stderr)
            elif param == 49:
                wt.back(on_stderr=self.on_stderr)
            elif 90 <= param <= 97:
                wt.fore(param - 90, light=True, on_stderr=self.on_stderr)
            elif 100 <= param <= 107:
                wt.back(param - 100, light=True, on_stderr=self.on_stderr)

    def should_wrap(self) -> bool:
        """Return True if the stream should be wrapped."""
        on_windows = platform.system() == "Windows"
        is_tty = hasattr(self.wrapped, "isatty") and self.wrapped.isatty()
        return on_windows and is_tty

    def write(self, text: str) -> None:
        """Write text, processing ANSI sequences as configured."""
        if self.strip or self.convert:
            self.write_and_convert(text)
        else:
            self.wrapped.write(text)
            self.wrapped.flush()

        if self.autoreset:
            self.reset_all()

    def write_and_convert(self, text: str) -> None:
        """Split text into plain parts and ANSI sequences, processing each."""
        cursor = 0

        for match in self.ANSI_CSI_RE.finditer(text):
            start, end = match.span()
            if cursor < start:
                self.write_plain_text(text, cursor, start)
            if self.convert:
                paramstring = match.group()[2:-1]  # Strip ESC[ and final char
                command = match.group()[-1]
                self.call_win32(paramstring, command)
            cursor = end

        # Also handle OSC sequences
        for match in self.ANSI_OSC_RE.finditer(text):
            start, end = match.span()
            if self.convert:
                self.convert_osc(match.group())

        # Write any remaining plain text
        if cursor < len(text):
            # Strip any remaining ANSI sequences if we're in strip mode
            remaining = text[cursor:]
            remaining = self.ANSI_CSI_RE.sub("", remaining)
            remaining = self.ANSI_OSC_RE.sub("", remaining)
            if remaining:
                self.wrapped.write(remaining)
                self.wrapped.flush()

    def write_plain_text(self, text: str, start: int, end: int) -> None:
        """Write a slice of text with no ANSI sequences."""
        if start < end:
            plain = text[start:end]
            # Strip any embedded sequences from this slice
            plain = self.ANSI_OSC_RE.sub("", plain)
            if plain:
                self.wrapped.write(plain)
                self.wrapped.flush()

    @staticmethod
    def extract_params(command: str, paramstring: str) -> list[int]:
        """Parse numeric CSI parameters from the parameter string."""
        if not paramstring:
            return []
        params: list[int] = []
        for p in paramstring.split(";"):
            if p.isdigit():
                params.append(int(p))
            else:
                params.append(0)
        return params

    def call_win32(self, paramstring: str, command: str) -> None:
        """Dispatch a CSI sequence to the appropriate Win32 handler."""
        params = self.extract_params(command, paramstring)
        handler = self.win32_calls.get(command)
        if handler:
            handler(params)

    def convert_osc(self, text: str) -> None:
        """Handle OSC (Operating System Command) sequences."""
        # OSC format: ESC ] Ps ; Pt BEL
        match = re.match(r"\033\](\d+);(.*?)(?:\007|\033\\)", text)
        if match:
            ps = int(match.group(1))
            pt = match.group(2)
            if ps in (0, 2):
                try:
                    from . import win32
                    win32.SetConsoleTitle(pt)
                except (ImportError, AttributeError):
                    pass

    def reset_all(self) -> None:
        """Reset all styles."""
        if self.convert:
            try:
                from . import winterm
                winterm.win_term.reset_all(self.on_stderr)
            except (ImportError, AttributeError):
                pass
        else:
            self.wrapped.write(Style.RESET_ALL)

    def flush(self) -> None:
        """Flush the underlying stream."""
        self.wrapped.flush()
