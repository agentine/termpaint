# termpaint

Drop-in replacement for [colorama](https://github.com/tartley/colorama) with 256-color, true color, and full type annotations.

```python
import termpaint as colorama  # zero-change migration
```

## Why termpaint?

colorama is one of the most-downloaded Python packages (262M downloads/month, 1.4M dependents) but has been effectively unmaintained since October 2022. termpaint replaces it with:

- **Python 3.9+** — no Python 2 compatibility cruft
- **Full type annotations** — mypy-strict clean, IDE-friendly
- **256-color support** — `Fore.color256(n)`, `Back.color256(n)`
- **True color (24-bit)** — `Fore.rgb(r, g, b)`, `Back.rgb(r, g, b)`
- **Color capability detection** — auto-detect terminal color support level
- **NO_COLOR / FORCE_COLOR** — respects standard environment variables
- **Thread-safe** — global state protected with locks
- **Zero dependencies**

## Installation

```bash
pip install termpaint
```

**Requires Python 3.9+.**

## Quickstart

```python
import termpaint
from termpaint import Fore, Back, Style

termpaint.init()

print(Fore.RED + "Error: something went wrong" + Style.RESET_ALL)
print(Back.GREEN + Fore.WHITE + "  OK  " + Style.RESET_ALL)
print(Style.BRIGHT + "Bold text" + Style.RESET_ALL)

# Auto-reset after each print
termpaint.init(autoreset=True)
print(Fore.CYAN + "This resets automatically")
print("Normal text again")

termpaint.deinit()
```

### just_fix_windows_console() — recommended for most projects

```python
import termpaint

termpaint.just_fix_windows_console()  # No-op on POSIX, enables ANSI on Windows

print("\033[32mGreen text\033[0m")
```

### Context manager

```python
from termpaint import Fore, Style, colorama_text

with colorama_text(autoreset=True):
    print(Fore.YELLOW + "Inside block, autoreset on")
# deinit() called automatically
```

## API Reference

### Initialization

#### `termpaint.init(autoreset=False, convert=None, strip=None, wrap=True)`

Wraps `sys.stdout` and `sys.stderr` with ANSI-processing stream wrappers.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `autoreset` | `bool` | `False` | Append `Style.RESET_ALL` after every `write()` |
| `convert` | `bool \| None` | `None` | Force Win32 API conversion (`True`/`False`) or auto-detect (`None`) |
| `strip` | `bool \| None` | `None` | Force strip ANSI codes (`True`/`False`) or auto-detect (`None`) |
| `wrap` | `bool` | `True` | If `False`, skip stream wrapping entirely |

#### `termpaint.deinit()`

Restore original `sys.stdout` and `sys.stderr`. Safe to call multiple times.

#### `termpaint.reinit()`

Re-initialize after a `deinit()`. No-op if already initialized.

#### `termpaint.just_fix_windows_console()`

The recommended modern alternative to `init()`. On Windows 10+, enables native VT processing; falls back to stream wrapping if unavailable. No-op on POSIX. Idempotent.

#### `termpaint.colorama_text(**kwargs)`

Context manager version of `init()`/`deinit()`. Accepts the same keyword arguments as `init()`.

```python
with termpaint.colorama_text(autoreset=True):
    print(Fore.GREEN + "colored")
```

---

### Foreground Colors — `Fore`

```python
from termpaint import Fore

Fore.BLACK    # \033[30m
Fore.RED      # \033[31m
Fore.GREEN    # \033[32m
Fore.YELLOW   # \033[33m
Fore.BLUE     # \033[34m
Fore.MAGENTA  # \033[35m
Fore.CYAN     # \033[36m
Fore.WHITE    # \033[37m
Fore.RESET    # \033[39m

# Bright variants
Fore.LIGHTBLACK_EX    # \033[90m
Fore.LIGHTRED_EX      # \033[91m
Fore.LIGHTGREEN_EX    # \033[92m
Fore.LIGHTYELLOW_EX   # \033[93m
Fore.LIGHTBLUE_EX     # \033[94m
Fore.LIGHTMAGENTA_EX  # \033[95m
Fore.LIGHTCYAN_EX     # \033[96m
Fore.LIGHTWHITE_EX    # \033[97m

# Extended colors (termpaint extensions)
Fore.color256(214)        # 256-color palette (0–255)
Fore.rgb(255, 165, 0)     # True color (24-bit)
```

---

### Background Colors — `Back`

Same attributes as `Fore` but for background (SGR codes 40–49, 100–107).

```python
from termpaint import Back

Back.RED                  # \033[41m
Back.color256(52)         # 256-color background
Back.rgb(0, 0, 128)       # True color background
```

---

### Styles — `Style`

```python
from termpaint import Style

Style.BRIGHT    # \033[1m  — bold / bright
Style.DIM       # \033[2m  — dim / faint
Style.NORMAL    # \033[22m — normal intensity
Style.RESET_ALL # \033[0m  — reset everything
```

---

### Cursor Movement — `Cursor`

`Cursor` methods return escape sequences; write them to stdout.

```python
from termpaint import Cursor
import sys

sys.stdout.write(Cursor.UP(3))        # Move up 3 lines
sys.stdout.write(Cursor.DOWN(1))      # Move down 1 line
sys.stdout.write(Cursor.FORWARD(5))   # Move right 5 columns
sys.stdout.write(Cursor.BACK(2))      # Move left 2 columns
sys.stdout.write(Cursor.POS(10, 5))   # Absolute position (col=10, row=5)
```

All methods default to `n=1`; `POS` defaults to `x=1, y=1`.

---

### Utility Functions

```python
from termpaint import code_to_chars, set_title, clear_screen, clear_line

code_to_chars(31)     # '\033[31m'  — SGR code to ANSI string
set_title("My App")   # '\033]2;My App\007'  — set terminal window title
clear_screen(2)       # '\033[2J'  — erase display (modes: 0=to end, 1=to start, 2=all)
clear_line(2)         # '\033[2K'  — erase line (modes: 0=to end, 1=to start, 2=all)
```

---

### Color Capability Detection

```python
from termpaint.environ import detect_color_support, is_no_color, is_force_color

level = detect_color_support()
# Returns:
#   0 — no color (NO_COLOR set, or not a TTY)
#   1 — 16 colors (basic ANSI)
#   2 — 256 colors (TERM contains "256color")
#   3 — true color (COLORTERM=truecolor or 24bit, or Windows 10 1607+)

if level >= 2:
    print(Fore.color256(208) + "Orange" + Style.RESET_ALL)
if level >= 3:
    print(Fore.rgb(255, 128, 0) + "True orange" + Style.RESET_ALL)
```

---

### Constants

```python
from termpaint import CSI, OSC, BEL

CSI  # '\033['  — Control Sequence Introducer
OSC  # '\033]'  — Operating System Command
BEL  # '\007'   — Bell character
```

---

## Extended Color Examples

### 256-Color Palette

```python
import termpaint
from termpaint import Fore, Back, Style

termpaint.just_fix_windows_console()

for i in range(256):
    print(f"{Fore.color256(i)}{i:>4}{Style.RESET_ALL}", end="")
    if (i + 1) % 16 == 0:
        print()
```

### True Color (24-bit)

```python
import termpaint
from termpaint import Fore, Style

termpaint.just_fix_windows_console()

# RGB gradient
for r in range(0, 256, 32):
    print(Fore.rgb(r, 100, 200) + f"r={r}" + Style.RESET_ALL)
```

---

## Environment Variables

| Variable | Effect |
|----------|--------|
| `NO_COLOR` | Strip all ANSI codes from output (see [no-color.org](https://no-color.org/)) |
| `FORCE_COLOR` | Emit ANSI codes even when not connected to a TTY (useful in CI/CD) |
| `COLORTERM=truecolor` | Signal true color support to capability detection |
| `COLORTERM=24bit` | Same as `truecolor` |

---

## Windows Support

termpaint uses a two-tier strategy on Windows:

1. **VT processing (Windows 10 1511+):** Calls `SetConsoleMode` to enable `ENABLE_VIRTUAL_TERMINAL_PROCESSING`. ANSI codes pass through natively. This is the preferred path.
2. **Win32 API fallback:** For older Windows or consoles that don't support VT processing, termpaint translates ANSI sequences into `SetConsoleTextAttribute`, `SetConsoleCursorPosition`, and related Win32 calls at runtime via `ctypes`.

Call `just_fix_windows_console()` at startup and termpaint handles the rest automatically.

---

## Migration from colorama

### Option 1: Import alias (zero code changes)

```python
# Before
import colorama
colorama.init()

# After — one line changed, everything else stays the same
import termpaint as colorama
colorama.init()
```

### Option 2: Direct migration

```python
# Before
import colorama
from colorama import Fore, Back, Style
colorama.init()

# After
import termpaint
from termpaint import Fore, Back, Style
termpaint.init()
```

All `Fore.*`, `Back.*`, `Style.*`, and `Cursor.*` values are identical to colorama. All `init()`, `deinit()`, `reinit()`, `just_fix_windows_console()`, and `colorama_text()` signatures are compatible.

### What's new vs colorama

| Feature | colorama | termpaint |
|---------|----------|-----------|
| Python 3.9+ only | No (supports 2.7) | Yes |
| Type annotations | No | Yes (mypy-strict) |
| 256-color | No | `Fore.color256(n)` |
| True color | No | `Fore.rgb(r, g, b)` |
| NO_COLOR support | No | Yes |
| FORCE_COLOR support | No | Yes |
| Color capability detection | No | `detect_color_support()` |
| Thread safety | Partial | Yes |
| Zero dependencies | Yes | Yes |

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/ tests/
```

---

## License

MIT
