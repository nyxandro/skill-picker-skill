"""The skill's scripts are standalone command-line tools, not a package: put their folder on the
import path so the tests can import them as modules. The test folder itself holds helpers.py."""

import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR.parent / "skill-picker" / "scripts"))
sys.path.insert(0, str(TEST_DIR))


@pytest.fixture
def home(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    return fake_home


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    return root
