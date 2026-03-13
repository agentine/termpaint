"""ANSI escape code constants and classes."""

from __future__ import annotations

CSI = "\033["
OSC = "\033]"
BEL = "\007"


def code_to_chars(code: int) -> str:
    """Convert an SGR code to its ANSI escape string."""
    return f"{CSI}{code}m"


def set_title(title: str) -> str:
    """Return an OSC sequence that sets the terminal title."""
    return f"{OSC}2;{title}{BEL}"


def clear_screen(mode: int = 2) -> str:
    """Return an ED (Erase in Display) sequence."""
    return f"{CSI}{mode}J"


def clear_line(mode: int = 2) -> str:
    """Return an EL (Erase in Line) sequence."""
    return f"{CSI}{mode}K"


class AnsiCodes:
    """Base class for ANSI code groups."""

    _codes: dict[str, str]

    def __init__(self) -> None:
        # Build the lookup from class-level annotations
        self._codes = {}
        for attr in dir(type(self)):
            if attr.startswith("_"):
                continue
            val = getattr(type(self), attr)
            if isinstance(val, str):
                self._codes[attr] = val

    def __getattr__(self, name: str) -> str:
        try:
            return self._codes[name]
        except KeyError:
            raise AttributeError(f"{type(self).__name__} has no attribute {name!r}") from None


class AnsiFore(AnsiCodes):
    """ANSI foreground color codes."""

    BLACK = code_to_chars(30)
    RED = code_to_chars(31)
    GREEN = code_to_chars(32)
    YELLOW = code_to_chars(33)
    BLUE = code_to_chars(34)
    MAGENTA = code_to_chars(35)
    CYAN = code_to_chars(36)
    WHITE = code_to_chars(37)
    RESET = code_to_chars(39)

    # Light/bright variants
    LIGHTBLACK_EX = code_to_chars(90)
    LIGHTRED_EX = code_to_chars(91)
    LIGHTGREEN_EX = code_to_chars(92)
    LIGHTYELLOW_EX = code_to_chars(93)
    LIGHTBLUE_EX = code_to_chars(94)
    LIGHTMAGENTA_EX = code_to_chars(95)
    LIGHTCYAN_EX = code_to_chars(96)
    LIGHTWHITE_EX = code_to_chars(97)

    @staticmethod
    def color256(n: int) -> str:
        """Return a 256-color foreground escape sequence."""
        return f"{CSI}38;5;{n}m"

    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Return a true color (24-bit) foreground escape sequence."""
        return f"{CSI}38;2;{r};{g};{b}m"


class AnsiBack(AnsiCodes):
    """ANSI background color codes."""

    BLACK = code_to_chars(40)
    RED = code_to_chars(41)
    GREEN = code_to_chars(42)
    YELLOW = code_to_chars(43)
    BLUE = code_to_chars(44)
    MAGENTA = code_to_chars(45)
    CYAN = code_to_chars(46)
    WHITE = code_to_chars(47)
    RESET = code_to_chars(49)

    # Light/bright variants
    LIGHTBLACK_EX = code_to_chars(100)
    LIGHTRED_EX = code_to_chars(101)
    LIGHTGREEN_EX = code_to_chars(102)
    LIGHTYELLOW_EX = code_to_chars(103)
    LIGHTBLUE_EX = code_to_chars(104)
    LIGHTMAGENTA_EX = code_to_chars(105)
    LIGHTCYAN_EX = code_to_chars(106)
    LIGHTWHITE_EX = code_to_chars(107)

    @staticmethod
    def color256(n: int) -> str:
        """Return a 256-color background escape sequence."""
        return f"{CSI}48;5;{n}m"

    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Return a true color (24-bit) background escape sequence."""
        return f"{CSI}48;2;{r};{g};{b}m"


class AnsiStyle(AnsiCodes):
    """ANSI style/attribute codes."""

    BRIGHT = code_to_chars(1)
    DIM = code_to_chars(2)
    NORMAL = code_to_chars(22)
    RESET_ALL = code_to_chars(0)


class AnsiCursor:
    """ANSI cursor movement sequences."""

    @staticmethod
    def UP(n: int = 1) -> str:
        return f"{CSI}{n}A"

    @staticmethod
    def DOWN(n: int = 1) -> str:
        return f"{CSI}{n}B"

    @staticmethod
    def FORWARD(n: int = 1) -> str:
        return f"{CSI}{n}C"

    @staticmethod
    def BACK(n: int = 1) -> str:
        return f"{CSI}{n}D"

    @staticmethod
    def POS(x: int = 1, y: int = 1) -> str:
        return f"{CSI}{y};{x}H"


Fore = AnsiFore()
Back = AnsiBack()
Style = AnsiStyle()
Cursor = AnsiCursor()
