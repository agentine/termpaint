"""Tests for __init__ module exports and stub functions."""

import termpaint
from termpaint import (
    Fore,
    Back,
    Style,
    Cursor,
    init,
    deinit,
    reinit,
    just_fix_windows_console,
    colorama_text,
    code_to_chars,
    set_title,
    clear_screen,
    clear_line,
    CSI,
    OSC,
    BEL,
)


class TestExports:
    def test_version(self) -> None:
        assert termpaint.__version__ == "0.1.0"

    def test_fore_exported(self) -> None:
        assert Fore.RED == "\033[31m"

    def test_back_exported(self) -> None:
        assert Back.RED == "\033[41m"

    def test_style_exported(self) -> None:
        assert Style.RESET_ALL == "\033[0m"

    def test_cursor_exported(self) -> None:
        assert Cursor.UP() == "\033[1A"

    def test_csi_exported(self) -> None:
        assert CSI == "\033["

    def test_osc_exported(self) -> None:
        assert OSC == "\033]"

    def test_bel_exported(self) -> None:
        assert BEL == "\007"

    def test_utility_functions_exported(self) -> None:
        assert callable(code_to_chars)
        assert callable(set_title)
        assert callable(clear_screen)
        assert callable(clear_line)


class TestStubFunctions:
    def test_init_no_error(self) -> None:
        init()

    def test_deinit_no_error(self) -> None:
        deinit()

    def test_reinit_no_error(self) -> None:
        reinit()

    def test_just_fix_windows_console_no_error(self) -> None:
        just_fix_windows_console()

    def test_colorama_text_context_manager(self) -> None:
        with colorama_text():
            pass
