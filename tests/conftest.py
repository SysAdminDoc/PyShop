#!/usr/bin/env python3
"""Keep GUI tests away from the user's windows, preferences, and recovery data."""
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest


@pytest.fixture(autouse=True)
def isolated_profile(tmp_path, monkeypatch):
    monkeypatch.setenv("PYSHOP_TEST_PROFILE", str(tmp_path / "profile"))
    monkeypatch.setenv("PYSHOP_DATA_DIR", str(tmp_path / "data"))
