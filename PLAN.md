# chromapaint — Drop-in Replacement for colorama

## Overview

**Target:** [colorama](https://github.com/tartley/colorama) — cross-platform terminal color support for Python
**Package:** `chromapaint` on PyPI
**License:** MIT
**Python:** 3.9+
**Dependencies:** Zero

## Why Replace colorama

- 262 million monthly PyPI downloads — one of the most-downloaded Python packages
- 1.4 million dependent projects
- Last release: v0.4.6, October 2022 (3.5+ years ago)
- 108 open issues with no triage
- Both maintainers (tartley, wiggin15) appear inactive
- Still contains Python 2 compatibility code
- No type annotations
- No 256-color or true color (24-bit) support
- No terminal capability detection
- PyCharm-specific hacks in the codebase

## Architecture

chromapaint is a single-package Python library with three layers:

```
Public API (init/deinit/Fore/Back/Style/Cursor)
    ↓
Stream Wrapper (AnsiToWin32 → intercepts write() calls)
    ↓
Platform Backend
    ├── POSIX: pass-through (ANSI natively supported)
    └── Windows: Win32 Console API via ctypes (legacy)
                 OR enable VT processing (modern Win10+)
```

On POSIX systems, colorama is essentially a no-op (ANSI codes pass through natively). On Windows, it either enables native VT processing (Win10 1511+) or falls back to translating ANSI escape codes into Win32 Console API calls via ctypes.

## Public API Surface (100% colorama compatible)

### Module-Level Functions

```python
def init(autoreset=False, convert=None, strip=None, wrap=True) -> None
def deinit() -> None
def reinit() -> None
def just_fix_windows_console() -> None

@contextlib.contextmanager
def colorama_text(*args, **kwargs) -> Generator
```

**`init()` parameters:**
- `autoreset` — if True, automatically append `Style.RESET_ALL` after each `write()`
- `convert` — if True, force Win32 API conversion; if False, disable it; if None, auto-detect
- `strip` — if True, strip ANSI codes from output; if False, don't; if None, auto-detect
- `wrap` — if True, replace sys.stdout/stderr with wrapped streams

**`just_fix_windows_console()`** — the recommended modern API. On Windows, enables native ANSI support if available, or falls back to stream wrapping. No-op on POSIX. Idempotent.

### ANSI Code Constants

```python
# Foreground colors
Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW
Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE
Fore.RESET
Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX
Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX

# Background colors
Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW
Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE
Back.RESET
Back.LIGHTBLACK_EX, Back.LIGHTRED_EX, Back.LIGHTGREEN_EX, Back.LIGHTYELLOW_EX
Back.LIGHTBLUE_EX, Back.LIGHTMAGENTA_EX, Back.LIGHTCYAN_EX, Back.LIGHTWHITE_EX

# Style attributes
Style.BRIGHT, Style.DIM, Style.NORMAL, Style.RESET_ALL

# Cursor movement (methods, not constants)
Cursor.UP(n=1), Cursor.DOWN(n=1), Cursor.FORWARD(n=1), Cursor.BACK(n=1)
Cursor.POS(x=1, y=1)
```

All `Fore.*`, `Back.*`, and `Style.*` attributes are ANSI escape code strings (e.g., `Fore.RED == '\033[31m'`).

### Utility Functions

```python
def code_to_chars(code: int) -> str     # SGR code → ANSI string
def set_title(title: str) -> str         # OSC title-set string
def clear_screen(mode: int = 2) -> str   # ED (Erase in Display)
def clear_line(mode: int = 2) -> str     # EL (Erase in Line)
```

### AnsiToWin32 Class

```python
class AnsiToWin32:
    ANSI_CSI_RE: re.Pattern  # CSI sequence regex
    ANSI_OSC_RE: re.Pattern  # OSC sequence regex

    wrapped: TextIO           # original stream
    autoreset: bool
    stream: StreamWrapper     # proxy stream
    strip: bool
    convert: bool
    on_stderr: bool

    def __init__(self, wrapped, convert=None, strip=None, autoreset=False)
    def should_wrap(self) -> bool
    def write(self, text: str) -> None
    def reset_all(self) -> None
    def flush(self) -> None
```

### StreamWrapper Class

```python
class StreamWrapper:
    def __init__(self, wrapped, converter)
    def write(self, text: str) -> None
    def isatty(self) -> bool
    @property
    def closed(self) -> bool
    def __enter__(self, *args, **kwargs)
    def __exit__(self, *args, **kwargs)
    def __getattr__(self, name)  # proxies all other attributes
    def __getstate__(self) / def __setstate__(self, state)  # pickling support
```

### Windows Backend (Internal)

```python
# WinColor constants
class WinColor:
    BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, GREY = 0..7

# WinStyle constants
class WinStyle:
    NORMAL = 0x00
    BRIGHT = 0x08
    BRIGHT_BACKGROUND = 0x80

# WinTerm — manages Windows console state
class WinTerm:
    def reset_all(self, on_stderr=None)
    def fore(self, fore=None, light=False, on_stderr=False)
    def back(self, back=None, light=False, on_stderr=False)
    def style(self, style=None, on_stderr=False)
    def set_console(self, attrs=None, on_stderr=False)
    def get_position(self, handle) -> COORD
    def set_cursor_position(self, position=None, on_stderr=False)
    def cursor_adjust(self, x, y, on_stderr=False)
    def erase_screen(self, mode=0, on_stderr=False)
    def erase_line(self, mode=0, on_stderr=False)
    def set_title(self, title)

# VT processing
def enable_vt_processing(fd: int) -> bool

# Win32 API wrappers (ctypes)
def GetConsoleScreenBufferInfo(stream_id) -> CONSOLE_SCREEN_BUFFER_INFO
def SetConsoleTextAttribute(stream_id, attrs)
def SetConsoleCursorPosition(stream_id, position, adjust=True)
def FillConsoleOutputCharacter(stream_id, char, length, start)
def FillConsoleOutputAttribute(stream_id, attr, length, start)
def SetConsoleTitle(title)
def GetConsoleMode(handle) -> int
def SetConsoleMode(handle, mode)
def winapi_test() -> bool
```

### ANSI Code Handling

**CSI (Control Sequence Introducer) sequences handled:**
- `m` — SGR (Select Graphic Rendition): colors and styles
- `J` — ED (Erase in Display): clear screen modes 0/1/2
- `K` — EL (Erase in Line): clear line modes 0/1/2
- `H`, `f` — CUP (Cursor Position): absolute positioning
- `A` — CUU (Cursor Up)
- `B` — CUD (Cursor Down)
- `C` — CUF (Cursor Forward)
- `D` — CUB (Cursor Back)

**OSC (Operating System Command) sequences handled:**
- `0;title` — Set window title and icon
- `2;title` — Set window title

## Key Improvements Over colorama

1. **Python 3.9+ only** — remove all Python 2 compatibility code and conditional imports
2. **Full type annotations** — complete type stubs for IDE support and mypy
3. **256-color support (extension)** — `Fore.color256(n)`, `Back.color256(n)` for 256-color palette
4. **True color support (extension)** — `Fore.rgb(r, g, b)`, `Back.rgb(r, g, b)` for 24-bit color
5. **Terminal capability detection** — auto-detect color support level (none/16/256/truecolor)
6. **NO_COLOR support** — respect the [NO_COLOR](https://no-color.org/) environment variable
7. **FORCE_COLOR support** — respect `FORCE_COLOR` for CI/CD environments
8. **Remove PyCharm hack** — handle IDE detection cleanly instead of special-casing
9. **Thread safety** — protect global state with proper locking
10. **Modern Windows handling** — prefer VT processing (Win10+), only fall back to Win32 API when necessary

## Implementation Phases

### Phase 1: ANSI Constants & Core API
- `Fore`, `Back`, `Style`, `Cursor` constants (exact same values as colorama)
- `AnsiCodes`, `AnsiFore`, `AnsiBack`, `AnsiStyle`, `AnsiCursor` classes
- Utility functions: `code_to_chars()`, `set_title()`, `clear_screen()`, `clear_line()`
- `CSI`, `OSC`, `BEL` constants
- Type annotations throughout

### Phase 2: Stream Wrapping & ANSI Processing
- `StreamWrapper` class with full proxy behavior
- `AnsiToWin32` class with CSI/OSC regex parsing
- ANSI sequence stripping logic
- `write()`, `write_and_convert()`, `write_plain_text()` methods
- `extract_params()`, `call_win32()`, `convert_osc()` methods
- `should_wrap()` detection logic
- `autoreset` behavior

### Phase 3: Windows Backend
- `win32` module with ctypes wrappers for all kernel32 functions
- `WinTerm` class with full console state management
- `WinColor`, `WinStyle` constants
- `enable_vt_processing()` for modern Windows
- Screen/line erase, cursor positioning, title setting
- Proper error handling for non-console file descriptors

### Phase 4: Initialization & Extensions
- `init()`, `deinit()`, `reinit()`, `just_fix_windows_console()`
- `colorama_text()` context manager
- `reset_all()` with atexit registration
- NO_COLOR / FORCE_COLOR environment variable support
- 256-color and true color extensions
- Terminal capability auto-detection
- Thread safety for global state
- PyPI package, CI/CD (test on Windows + POSIX), documentation
- Migration guide (import chromapaint as colorama)
