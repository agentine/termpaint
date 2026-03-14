"""Tests for environment variable detection."""

from __future__ import annotations

import os
from unittest import mock

from chromapaint.environ import is_no_color, is_force_color, detect_color_support


class TestNoColor:
    def test_no_color_when_set(self) -> None:
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}):
            assert is_no_color() is True

    def test_no_color_when_empty(self) -> None:
        with mock.patch.dict(os.environ, {"NO_COLOR": ""}):
            assert is_no_color() is True

    def test_no_color_when_absent(self) -> None:
        env = os.environ.copy()
        env.pop("NO_COLOR", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert is_no_color() is False


class TestForceColor:
    def test_force_color_when_set(self) -> None:
        with mock.patch.dict(os.environ, {"FORCE_COLOR": "1"}):
            assert is_force_color() is True

    def test_force_color_when_absent(self) -> None:
        env = os.environ.copy()
        env.pop("FORCE_COLOR", None)
        with mock.patch.dict(os.environ, env, clear=True):
            assert is_force_color() is False


class TestDetectColorSupport:
    def test_no_color_returns_zero(self) -> None:
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}, clear=True):
            assert detect_color_support() == 0

    def test_force_color_returns_three(self) -> None:
        with mock.patch.dict(os.environ, {"FORCE_COLOR": "1"}, clear=True):
            assert detect_color_support() == 3

    def test_colorterm_truecolor(self) -> None:
        with mock.patch.dict(os.environ, {"COLORTERM": "truecolor"}, clear=True):
            assert detect_color_support() == 3

    def test_colorterm_24bit(self) -> None:
        with mock.patch.dict(os.environ, {"COLORTERM": "24bit"}, clear=True):
            assert detect_color_support() == 3

    def test_term_256color(self) -> None:
        with mock.patch.dict(os.environ, {"TERM": "xterm-256color"}, clear=True):
            assert detect_color_support() == 2

    def test_term_xterm_basic(self) -> None:
        with mock.patch.dict(os.environ, {"TERM": "xterm"}, clear=True):
            assert detect_color_support() == 1

    def test_term_screen(self) -> None:
        with mock.patch.dict(os.environ, {"TERM": "screen"}, clear=True):
            assert detect_color_support() == 1

    def test_no_color_overrides_force(self) -> None:
        with mock.patch.dict(os.environ, {"NO_COLOR": "1", "FORCE_COLOR": "1"}, clear=True):
            assert detect_color_support() == 0

    def test_empty_env_no_tty(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("chromapaint.environ.platform") as mock_platform:
                mock_platform.system.return_value = "Linux"
                with mock.patch("sys.stdout") as mock_stdout:
                    mock_stdout.isatty.return_value = False
                    assert detect_color_support() == 0

    def test_empty_env_with_tty(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("chromapaint.environ.platform") as mock_platform:
                mock_platform.system.return_value = "Linux"
                mock_stdout = mock.MagicMock()
                mock_stdout.isatty.return_value = True
                with mock.patch("sys.stdout", mock_stdout):
                    assert detect_color_support() == 1
