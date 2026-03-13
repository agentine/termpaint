"""Tests for AnsiToWin32 and StreamWrapper."""

import io
from termpaint.ansitowin32 import (
    AnsiToWin32,
    StreamWrapper,
    ANSI_CSI_RE,
    ANSI_OSC_RE,
)


class TestRegex:
    def test_csi_matches_sgr(self) -> None:
        assert ANSI_CSI_RE.search("\033[31m") is not None

    def test_csi_matches_cursor(self) -> None:
        assert ANSI_CSI_RE.search("\033[5A") is not None

    def test_csi_matches_multi_param(self) -> None:
        assert ANSI_CSI_RE.search("\033[38;5;196m") is not None

    def test_csi_no_match_plain(self) -> None:
        assert ANSI_CSI_RE.search("hello world") is None

    def test_osc_matches_title(self) -> None:
        assert ANSI_OSC_RE.search("\033]2;title\007") is not None

    def test_osc_matches_st_terminator(self) -> None:
        assert ANSI_OSC_RE.search("\033]0;title\033\\") is not None


class TestStreamWrapper:
    def test_write_delegates_to_converter(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        wrapper = StreamWrapper(stream, converter)
        wrapper.write("hello")
        assert "hello" in stream.getvalue()

    def test_isatty_delegates(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        wrapper = StreamWrapper(stream, converter)
        assert wrapper.isatty() is False

    def test_closed_property(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        wrapper = StreamWrapper(stream, converter)
        assert wrapper.closed is False
        stream.close()
        assert wrapper.closed is True

    def test_context_manager(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        wrapper = StreamWrapper(stream, converter)
        with wrapper as w:
            assert w is wrapper

    def test_proxy_attrs(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        wrapper = StreamWrapper(stream, converter)
        # StringIO has getvalue()
        assert hasattr(wrapper, "getvalue")

    def test_getstate_setstate(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        wrapper = StreamWrapper(stream, converter)
        state = wrapper.__getstate__()
        assert "_wrapped" in state
        assert "_converter" in state
        new_wrapper = StreamWrapper.__new__(StreamWrapper)
        new_wrapper.__setstate__(state)
        assert new_wrapper._wrapped is stream


class TestAnsiToWin32:
    def test_passthrough_on_non_windows(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        converter.write("hello \033[31mworld\033[0m")
        assert "hello" in stream.getvalue()
        assert "\033[31m" in stream.getvalue()

    def test_strip_removes_ansi(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream, strip=True)
        converter.write("\033[31mhello\033[0m")
        output = stream.getvalue()
        assert "hello" in output
        assert "\033[" not in output

    def test_strip_multi_sequence(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream, strip=True)
        converter.write("\033[1m\033[31mbold red\033[0m normal")
        output = stream.getvalue()
        assert "bold red" in output
        assert "normal" in output
        assert "\033[" not in output

    def test_strip_preserves_plain_text(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream, strip=True)
        converter.write("no ansi here")
        assert stream.getvalue() == "no ansi here"

    def test_autoreset_appends_reset(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream, autoreset=True)
        converter.write("hello")
        output = stream.getvalue()
        assert "\033[0m" in output

    def test_should_wrap_false_on_non_windows(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        # StringIO.isatty() is False, so should_wrap is False
        assert converter.should_wrap() is False

    def test_flush(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        converter.flush()  # Should not raise

    def test_reset_all_passthrough(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        converter.reset_all()
        assert "\033[0m" in stream.getvalue()

    def test_extract_params_basic(self) -> None:
        params = AnsiToWin32.extract_params("m", "31")
        assert params == [31]

    def test_extract_params_multi(self) -> None:
        params = AnsiToWin32.extract_params("m", "38;5;196")
        assert params == [38, 5, 196]

    def test_extract_params_empty(self) -> None:
        params = AnsiToWin32.extract_params("m", "")
        assert params == []

    def test_stream_attribute(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        assert isinstance(converter.stream, StreamWrapper)

    def test_on_stderr_detection(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream)
        assert converter.on_stderr is False


class TestStripOSC:
    def test_strip_osc_title(self) -> None:
        stream = io.StringIO()
        converter = AnsiToWin32(stream, strip=True)
        converter.write("\033]2;My Title\007text after")
        output = stream.getvalue()
        assert "text after" in output
        assert "\033]" not in output
