"""Tests for initialise module — init, deinit, reinit, just_fix_windows_console."""

from __future__ import annotations

import sys
from unittest import mock

import termpaint
from termpaint import init, deinit, reinit, just_fix_windows_console, colorama_text
from termpaint.ansitowin32 import StreamWrapper
from termpaint import initialise


class TestInit:
    def setup_method(self) -> None:
        # Ensure clean state before each test
        deinit()
        initialise._fixed = False

    def teardown_method(self) -> None:
        deinit()
        initialise._fixed = False

    def test_init_wraps_stdout(self) -> None:
        init()
        assert isinstance(sys.stdout, StreamWrapper)

    def test_init_wraps_stderr(self) -> None:
        init()
        assert isinstance(sys.stderr, StreamWrapper)

    def test_deinit_restores_stdout(self) -> None:
        original = sys.stdout
        init()
        deinit()
        assert sys.stdout is original

    def test_deinit_restores_stderr(self) -> None:
        original = sys.stderr
        init()
        deinit()
        assert sys.stderr is original

    def test_deinit_idempotent(self) -> None:
        deinit()
        deinit()  # Should not raise

    def test_reinit_after_deinit(self) -> None:
        init()
        deinit()
        reinit()
        assert isinstance(sys.stdout, StreamWrapper)

    def test_reinit_noop_when_wrapped(self) -> None:
        init()
        reinit()  # Should not double-wrap
        assert isinstance(sys.stdout, StreamWrapper)

    def test_init_wrap_false_noop(self) -> None:
        original = sys.stdout
        init(wrap=False)
        assert sys.stdout is original

    def test_colorama_text_wraps_and_unwraps(self) -> None:
        original = sys.stdout
        with colorama_text():
            assert isinstance(sys.stdout, StreamWrapper)
        assert sys.stdout is original

    def test_just_fix_windows_console_noop_on_posix(self) -> None:
        original = sys.stdout
        just_fix_windows_console()
        # On macOS/Linux, should be a no-op (not Windows)
        assert sys.stdout is original

    def test_just_fix_windows_console_idempotent(self) -> None:
        just_fix_windows_console()
        just_fix_windows_console()  # Should not raise


class TestResetAll:
    def test_reset_all_writes_reset(self) -> None:
        buf = mock.MagicMock()
        with mock.patch("sys.stdout", buf):
            initialise._reset_all()
        buf.write.assert_called_once_with("\033[0m")

    def test_reset_all_swallows_errors(self) -> None:
        buf = mock.MagicMock()
        buf.write.side_effect = OSError("broken pipe")
        with mock.patch("sys.stdout", buf):
            initialise._reset_all()  # Should not raise
