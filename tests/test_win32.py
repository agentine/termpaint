"""Tests for win32 module — graceful behavior on non-Windows."""

from termpaint.win32 import (
    winapi_test,
    enable_vt_processing,
    GetConsoleScreenBufferInfo,
    SetConsoleTextAttribute,
    SetConsoleCursorPosition,
    FillConsoleOutputCharacter,
    FillConsoleOutputAttribute,
    SetConsoleTitle,
    GetConsoleMode,
    SetConsoleMode,
    COORD,
    SMALL_RECT,
    CONSOLE_SCREEN_BUFFER_INFO,
    STD_OUTPUT_HANDLE,
    STD_ERROR_HANDLE,
)
from termpaint.winterm import WinColor, WinStyle, WinTerm


class TestWin32Graceful:
    """All functions should work without error on non-Windows."""

    def test_winapi_test(self) -> None:
        # On macOS/Linux, should return False
        result = winapi_test()
        assert isinstance(result, bool)

    def test_enable_vt_processing(self) -> None:
        assert enable_vt_processing(1) is False

    def test_get_console_screen_buffer_info(self) -> None:
        result = GetConsoleScreenBufferInfo(STD_OUTPUT_HANDLE)
        assert result is None  # Not Windows

    def test_set_console_text_attribute(self) -> None:
        SetConsoleTextAttribute(STD_OUTPUT_HANDLE, 0x07)  # Should not raise

    def test_set_console_cursor_position(self) -> None:
        SetConsoleCursorPosition(STD_OUTPUT_HANDLE, (0, 0))  # Should not raise

    def test_fill_console_output_character(self) -> None:
        result = FillConsoleOutputCharacter(STD_OUTPUT_HANDLE, " ", 10, (0, 0))
        assert result == 0  # Not Windows

    def test_fill_console_output_attribute(self) -> None:
        result = FillConsoleOutputAttribute(STD_OUTPUT_HANDLE, 0x07, 10, (0, 0))
        assert result == 0  # Not Windows

    def test_set_console_title(self) -> None:
        SetConsoleTitle("test")  # Should not raise

    def test_get_console_mode(self) -> None:
        result = GetConsoleMode(None)
        assert result == 0  # Not Windows

    def test_set_console_mode(self) -> None:
        SetConsoleMode(None, 0)  # Should not raise


class TestStructures:
    def test_coord(self) -> None:
        c = COORD(10, 20)
        assert c.X == 10
        assert c.Y == 20

    def test_small_rect(self) -> None:
        r = SMALL_RECT(0, 0, 79, 24)
        assert r.Right == 79

    def test_console_screen_buffer_info(self) -> None:
        info = CONSOLE_SCREEN_BUFFER_INFO(
            dwSize=COORD(80, 25),
            dwCursorPosition=COORD(0, 0),
            wAttributes=0x07,
            srWindow=SMALL_RECT(0, 0, 79, 24),
            dwMaximumWindowSize=COORD(80, 25),
        )
        assert info.dwSize.X == 80
        assert info.wAttributes == 0x07


class TestConstants:
    def test_std_output_handle(self) -> None:
        assert STD_OUTPUT_HANDLE == -11

    def test_std_error_handle(self) -> None:
        assert STD_ERROR_HANDLE == -12


class TestWinColor:
    def test_values(self) -> None:
        assert WinColor.BLACK == 0
        assert WinColor.RED == 4
        assert WinColor.GREY == 7


class TestWinStyle:
    def test_values(self) -> None:
        assert WinStyle.NORMAL == 0x00
        assert WinStyle.BRIGHT == 0x08
        assert WinStyle.BRIGHT_BACKGROUND == 0x80


class TestWinTerm:
    def test_instantiation(self) -> None:
        wt = WinTerm()
        assert wt is not None

    def test_reset_all(self) -> None:
        wt = WinTerm()
        wt.reset_all()  # Should not raise

    def test_fore(self) -> None:
        wt = WinTerm()
        wt.fore(WinColor.RED)  # Should not raise

    def test_back(self) -> None:
        wt = WinTerm()
        wt.back(WinColor.BLUE)  # Should not raise

    def test_style(self) -> None:
        wt = WinTerm()
        wt.style(WinStyle.BRIGHT)  # Should not raise

    def test_get_position(self) -> None:
        wt = WinTerm()
        pos = wt.get_position(STD_OUTPUT_HANDLE)
        assert isinstance(pos, COORD)

    def test_set_cursor_position(self) -> None:
        wt = WinTerm()
        wt.set_cursor_position((0, 0))  # Should not raise

    def test_cursor_adjust(self) -> None:
        wt = WinTerm()
        wt.cursor_adjust(1, 1)  # Should not raise

    def test_erase_screen(self) -> None:
        wt = WinTerm()
        wt.erase_screen(2)  # Should not raise

    def test_erase_line(self) -> None:
        wt = WinTerm()
        wt.erase_line(2)  # Should not raise

    def test_set_title(self) -> None:
        wt = WinTerm()
        wt.set_title("test")  # Should not raise
