"""Tests for ANSI constants, utility functions, and color extensions."""

from chromapaint import Fore, Back, Style, Cursor
from chromapaint.ansi import (
    CSI,
    OSC,
    BEL,
    code_to_chars,
    set_title,
    clear_screen,
    clear_line,
)


class TestConstants:
    def test_csi(self) -> None:
        assert CSI == "\033["

    def test_osc(self) -> None:
        assert OSC == "\033]"

    def test_bel(self) -> None:
        assert BEL == "\007"


class TestForeground:
    def test_black(self) -> None:
        assert Fore.BLACK == "\033[30m"

    def test_red(self) -> None:
        assert Fore.RED == "\033[31m"

    def test_green(self) -> None:
        assert Fore.GREEN == "\033[32m"

    def test_yellow(self) -> None:
        assert Fore.YELLOW == "\033[33m"

    def test_blue(self) -> None:
        assert Fore.BLUE == "\033[34m"

    def test_magenta(self) -> None:
        assert Fore.MAGENTA == "\033[35m"

    def test_cyan(self) -> None:
        assert Fore.CYAN == "\033[36m"

    def test_white(self) -> None:
        assert Fore.WHITE == "\033[37m"

    def test_reset(self) -> None:
        assert Fore.RESET == "\033[39m"

    def test_lightblack_ex(self) -> None:
        assert Fore.LIGHTBLACK_EX == "\033[90m"

    def test_lightred_ex(self) -> None:
        assert Fore.LIGHTRED_EX == "\033[91m"

    def test_lightgreen_ex(self) -> None:
        assert Fore.LIGHTGREEN_EX == "\033[92m"

    def test_lightyellow_ex(self) -> None:
        assert Fore.LIGHTYELLOW_EX == "\033[93m"

    def test_lightblue_ex(self) -> None:
        assert Fore.LIGHTBLUE_EX == "\033[94m"

    def test_lightmagenta_ex(self) -> None:
        assert Fore.LIGHTMAGENTA_EX == "\033[95m"

    def test_lightcyan_ex(self) -> None:
        assert Fore.LIGHTCYAN_EX == "\033[96m"

    def test_lightwhite_ex(self) -> None:
        assert Fore.LIGHTWHITE_EX == "\033[97m"


class TestBackground:
    def test_black(self) -> None:
        assert Back.BLACK == "\033[40m"

    def test_red(self) -> None:
        assert Back.RED == "\033[41m"

    def test_green(self) -> None:
        assert Back.GREEN == "\033[42m"

    def test_yellow(self) -> None:
        assert Back.YELLOW == "\033[43m"

    def test_blue(self) -> None:
        assert Back.BLUE == "\033[44m"

    def test_magenta(self) -> None:
        assert Back.MAGENTA == "\033[45m"

    def test_cyan(self) -> None:
        assert Back.CYAN == "\033[46m"

    def test_white(self) -> None:
        assert Back.WHITE == "\033[47m"

    def test_reset(self) -> None:
        assert Back.RESET == "\033[49m"

    def test_lightblack_ex(self) -> None:
        assert Back.LIGHTBLACK_EX == "\033[100m"

    def test_lightwhite_ex(self) -> None:
        assert Back.LIGHTWHITE_EX == "\033[107m"


class TestStyle:
    def test_bright(self) -> None:
        assert Style.BRIGHT == "\033[1m"

    def test_dim(self) -> None:
        assert Style.DIM == "\033[2m"

    def test_normal(self) -> None:
        assert Style.NORMAL == "\033[22m"

    def test_reset_all(self) -> None:
        assert Style.RESET_ALL == "\033[0m"


class TestCursor:
    def test_up(self) -> None:
        assert Cursor.UP() == "\033[1A"
        assert Cursor.UP(5) == "\033[5A"

    def test_down(self) -> None:
        assert Cursor.DOWN() == "\033[1B"
        assert Cursor.DOWN(3) == "\033[3B"

    def test_forward(self) -> None:
        assert Cursor.FORWARD() == "\033[1C"
        assert Cursor.FORWARD(10) == "\033[10C"

    def test_back(self) -> None:
        assert Cursor.BACK() == "\033[1D"
        assert Cursor.BACK(2) == "\033[2D"

    def test_pos(self) -> None:
        assert Cursor.POS() == "\033[1;1H"
        assert Cursor.POS(5, 10) == "\033[10;5H"


class TestUtilityFunctions:
    def test_code_to_chars(self) -> None:
        assert code_to_chars(31) == "\033[31m"
        assert code_to_chars(0) == "\033[0m"

    def test_set_title(self) -> None:
        assert set_title("hello") == "\033]2;hello\007"

    def test_clear_screen(self) -> None:
        assert clear_screen() == "\033[2J"
        assert clear_screen(0) == "\033[0J"

    def test_clear_line(self) -> None:
        assert clear_line() == "\033[2K"
        assert clear_line(1) == "\033[1K"


class TestColor256:
    def test_fore_color256(self) -> None:
        assert Fore.color256(196) == "\033[38;5;196m"
        assert Fore.color256(0) == "\033[38;5;0m"
        assert Fore.color256(255) == "\033[38;5;255m"

    def test_back_color256(self) -> None:
        assert Back.color256(196) == "\033[48;5;196m"
        assert Back.color256(0) == "\033[48;5;0m"


class TestTrueColor:
    def test_fore_rgb(self) -> None:
        assert Fore.rgb(255, 0, 0) == "\033[38;2;255;0;0m"
        assert Fore.rgb(0, 128, 255) == "\033[38;2;0;128;255m"

    def test_back_rgb(self) -> None:
        assert Back.rgb(255, 0, 0) == "\033[48;2;255;0;0m"
        assert Back.rgb(0, 0, 0) == "\033[48;2;0;0;0m"


class TestInvalidAttribute:
    def test_fore_invalid(self) -> None:
        import pytest
        with pytest.raises(AttributeError, match="NONEXISTENT"):
            _ = Fore.NONEXISTENT  # type: ignore[attr-defined]
