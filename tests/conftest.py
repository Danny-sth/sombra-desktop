"""Pytest configuration and fixtures for Sombra Desktop tests."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app here as pytest-qt handles cleanup
