"""Unit tests for sombra.ui.utils module."""

import platform
import pytest

from sombra import __app_name__, __version__
from sombra.ui.utils import health_check


class TestHealthCheck:
    """Tests for health_check() function."""

    def test_health_check_returns_dict(self):
        """Test that health_check returns a dictionary."""
        result = health_check()
        assert isinstance(result, dict)

    def test_health_check_has_required_keys(self):
        """Test that health_check returns all required keys."""
        result = health_check()
        required_keys = {"version", "app_name", "python_version", "platform"}
        assert set(result.keys()) == required_keys

    def test_health_check_version_value(self):
        """Test that version matches the package version."""
        result = health_check()
        assert result["version"] == __version__

    def test_health_check_app_name_value(self):
        """Test that app_name matches the package app name."""
        result = health_check()
        assert result["app_name"] == __app_name__

    def test_health_check_python_version_value(self):
        """Test that python_version matches current Python version."""
        result = health_check()
        assert result["python_version"] == platform.python_version()

    def test_health_check_platform_value(self):
        """Test that platform matches current system platform."""
        result = health_check()
        assert result["platform"] == platform.system()

    def test_health_check_all_values_are_strings(self):
        """Test that all values in the result are strings."""
        result = health_check()
        for key, value in result.items():
            assert isinstance(value, str), f"Value for '{key}' should be a string"

    def test_health_check_version_not_empty(self):
        """Test that version is not an empty string."""
        result = health_check()
        assert result["version"], "Version should not be empty"

    def test_health_check_app_name_not_empty(self):
        """Test that app_name is not an empty string."""
        result = health_check()
        assert result["app_name"], "App name should not be empty"

    def test_health_check_platform_valid(self):
        """Test that platform is a valid system identifier."""
        result = health_check()
        valid_platforms = {"Linux", "Windows", "Darwin", "Java"}
        assert result["platform"] in valid_platforms, f"Platform '{result['platform']}' is unexpected"
