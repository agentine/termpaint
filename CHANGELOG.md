# Changelog

## [0.1.0] — 2026-03-14

Initial release of termpaint — a drop-in replacement for [colorama](https://github.com/tartley/colorama) with modern Python support, type annotations, and extended color capabilities.

### Features

- **Phase 1 — ANSI constants & core API**
  - `Fore`, `Back`, `Style`, `Cursor` constants (100% colorama-compatible values)
  - `AnsiFore`, `AnsiBack`, `AnsiStyle`, `AnsiCursor` classes
  - Utility functions: `code_to_chars()`, `set_title()`, `clear_screen()`, `clear_line()`
  - `CSI`, `OSC`, `BEL` constants
  - Full type annotations throughout

- **Phase 2 — Stream wrapping & ANSI processing**
  - `StreamWrapper` class with full proxy behavior (pickling, context manager, attribute forwarding)
  - `AnsiToWin32` class with CSI/OSC regex parsing
  - ANSI sequence stripping and autoreset behavior
  - `write()`, `write_and_convert()`, `write_plain_text()` methods

- **Phase 3 — Windows backend**
  - `win32` module with ctypes wrappers for all kernel32 console functions
  - `WinTerm` class with full console state management
  - `WinColor`, `WinStyle` constants
  - `enable_vt_processing()` for modern Windows (Win10+)
  - Screen/line erase, cursor positioning, title setting

- **Phase 4 — Initialization, environment detection & extensions**
  - `init()`, `deinit()`, `reinit()`, `just_fix_windows_console()` (colorama-compatible)
  - `colorama_text()` context manager with kwargs forwarding fix
  - `NO_COLOR` and `FORCE_COLOR` environment variable support
  - 256-color extensions: `Fore.color256(n)`, `Back.color256(n)`
  - True color (24-bit) extensions: `Fore.rgb(r, g, b)`, `Back.rgb(r, g, b)`
  - Terminal capability auto-detection (none/16/256/truecolor)
  - Thread-safe global state with proper locking
  - atexit reset registration

### Bug Fixes

- `NO_COLOR` / `FORCE_COLOR` environment variables now properly integrated into `AnsiToWin32.__init__()` auto-detection logic
- Fixed `mypy --strict` compliance (0 errors across all modules)
- Fixed `colorama_text()` to forward `**kwargs` to `init()` via `__enter__`

### CI

- Tests run on Ubuntu, Windows, macOS against Python 3.9–3.13 (145 tests)
- mypy strict type checking on Python 3.12

[0.1.0]: https://github.com/agentine/termpaint/releases/tag/v0.1.0
