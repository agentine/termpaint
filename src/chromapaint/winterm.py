"""WinTerm — Windows console state management.

Manages foreground/background colors, styles, cursor position, and
screen/line erase operations via Win32 Console API.
"""

from __future__ import annotations

from . import win32


class WinColor:
    """Windows console color constants (4-bit)."""
    BLACK = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    YELLOW = 6
    GREY = 7


class WinStyle:
    """Windows console style constants."""
    NORMAL = 0x00
    BRIGHT = 0x08
    BRIGHT_BACKGROUND = 0x80


class WinTerm:
    """Manages Windows console state via Win32 API."""

    def __init__(self) -> None:
        self._default_fore = WinColor.GREY
        self._default_back = WinColor.BLACK
        self._default_style = WinStyle.NORMAL

        # Try to read current console attributes
        csbi = win32.GetConsoleScreenBufferInfo(win32.STD_OUTPUT_HANDLE)
        if csbi:
            attrs = csbi.wAttributes
            self._default_fore = attrs & 0x07
            self._default_back = (attrs >> 4) & 0x07
            self._default_style = attrs & (WinStyle.BRIGHT | WinStyle.BRIGHT_BACKGROUND)

        self._fore = self._default_fore
        self._back = self._default_back
        self._style = self._default_style

    def _get_attrs(self) -> int:
        """Build the combined attribute word."""
        return self._fore | (self._back << 4) | self._style

    def _stream_id(self, on_stderr: bool = False) -> int:
        return win32._stream_id(on_stderr)

    def reset_all(self, on_stderr: bool | None = None) -> None:
        """Reset all attributes to defaults."""
        self._fore = self._default_fore
        self._back = self._default_back
        self._style = self._default_style
        win32.SetConsoleTextAttribute(
            self._stream_id(on_stderr or False), self._get_attrs()
        )

    def fore(
        self,
        fore: int | None = None,
        light: bool = False,
        on_stderr: bool = False,
    ) -> None:
        """Set foreground color."""
        if fore is None:
            self._fore = self._default_fore
        else:
            self._fore = fore
        if light:
            self._style |= WinStyle.BRIGHT
        win32.SetConsoleTextAttribute(self._stream_id(on_stderr), self._get_attrs())

    def back(
        self,
        back: int | None = None,
        light: bool = False,
        on_stderr: bool = False,
    ) -> None:
        """Set background color."""
        if back is None:
            self._back = self._default_back
        else:
            self._back = back
        if light:
            self._style |= WinStyle.BRIGHT_BACKGROUND
        win32.SetConsoleTextAttribute(self._stream_id(on_stderr), self._get_attrs())

    def style(self, style: int | None = None, on_stderr: bool = False) -> None:
        """Set style attributes."""
        if style is None:
            self._style = self._default_style
        else:
            self._style |= style
        win32.SetConsoleTextAttribute(self._stream_id(on_stderr), self._get_attrs())

    def set_console(self, attrs: int | None = None, on_stderr: bool = False) -> None:
        """Set raw console attributes."""
        if attrs is not None:
            win32.SetConsoleTextAttribute(self._stream_id(on_stderr), attrs)

    def get_position(self, handle: int) -> win32.COORD:
        """Get the current cursor position."""
        csbi = win32.GetConsoleScreenBufferInfo(handle)
        if csbi:
            return csbi.dwCursorPosition
        return win32.COORD(0, 0)

    def set_cursor_position(
        self,
        position: tuple[int, int] | None = None,
        on_stderr: bool = False,
    ) -> None:
        """Set cursor position. Position is (x, y)."""
        if position is None:
            position = (0, 0)
        win32.SetConsoleCursorPosition(self._stream_id(on_stderr), position)

    def cursor_adjust(self, x: int, y: int, on_stderr: bool = False) -> None:
        """Move cursor relative to current position."""
        stream_id = self._stream_id(on_stderr)
        pos = self.get_position(stream_id)
        new_x = max(0, pos.X + x)
        new_y = max(0, pos.Y + y)
        win32.SetConsoleCursorPosition(stream_id, (new_x, new_y), adjust=False)

    def erase_screen(self, mode: int = 0, on_stderr: bool = False) -> None:
        """Erase screen. mode: 0=below, 1=above, 2=all."""
        stream_id = self._stream_id(on_stderr)
        csbi = win32.GetConsoleScreenBufferInfo(stream_id)
        if not csbi:
            return

        if mode == 0:
            # Erase from cursor to end
            start = (csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y)
            length = (
                (csbi.dwSize.X - csbi.dwCursorPosition.X)
                + csbi.dwSize.X * (csbi.dwSize.Y - csbi.dwCursorPosition.Y - 1)
            )
        elif mode == 1:
            # Erase from start to cursor
            start = (0, 0)
            length = csbi.dwCursorPosition.Y * csbi.dwSize.X + csbi.dwCursorPosition.X + 1
        else:
            # Erase all
            start = (0, 0)
            length = csbi.dwSize.X * csbi.dwSize.Y

        win32.FillConsoleOutputCharacter(stream_id, " ", length, start)
        win32.FillConsoleOutputAttribute(stream_id, self._get_attrs(), length, start)

        if mode == 2:
            win32.SetConsoleCursorPosition(stream_id, (0, 0))

    def erase_line(self, mode: int = 0, on_stderr: bool = False) -> None:
        """Erase line. mode: 0=to end, 1=to start, 2=all."""
        stream_id = self._stream_id(on_stderr)
        csbi = win32.GetConsoleScreenBufferInfo(stream_id)
        if not csbi:
            return

        if mode == 0:
            start = (csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y)
            length = csbi.dwSize.X - csbi.dwCursorPosition.X
        elif mode == 1:
            start = (0, csbi.dwCursorPosition.Y)
            length = csbi.dwCursorPosition.X + 1
        else:
            start = (0, csbi.dwCursorPosition.Y)
            length = csbi.dwSize.X

        win32.FillConsoleOutputCharacter(stream_id, " ", length, start)
        win32.FillConsoleOutputAttribute(stream_id, self._get_attrs(), length, start)

    def set_title(self, title: str) -> None:
        """Set the console window title."""
        win32.SetConsoleTitle(title)


# Module-level singleton (only usable on Windows, but safe to instantiate anywhere)
win_term = WinTerm()
