"""AnsiToWin32 stream wrapper — stub for Phase 2."""

from __future__ import annotations

import re
from typing import Any, TextIO

ANSI_CSI_RE = re.compile(r"\033\[(\d+;)*\d*[A-Za-z]")
ANSI_OSC_RE = re.compile(r"\033\].*?(\007|\033\\)")


class StreamWrapper:
    """Proxy stream that delegates write() to a converter."""

    def __init__(self, wrapped: TextIO, converter: Any) -> None:
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
    """Translates ANSI codes to Win32 console API calls (or strips them)."""

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
        self.strip = strip or False
        self.convert = convert or False
        self.on_stderr = False
        self.stream = StreamWrapper(wrapped, self)

    def should_wrap(self) -> bool:
        return False

    def write(self, text: str) -> None:
        self.wrapped.write(text)

    def reset_all(self) -> None:
        from .ansi import Style
        self.wrapped.write(Style.RESET_ALL)

    def flush(self) -> None:
        self.wrapped.flush()
