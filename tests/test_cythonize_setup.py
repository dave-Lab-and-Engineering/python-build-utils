"""Unit tests for the cythonized_setup function in cythonize_setup.py."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

import python_build_utils.cythonize_setup as mod


@pytest.fixture(autouse=True)
def restore_env() -> None:
    """Ensure environment is reset after each test."""
    original = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original)


def test_pure_python_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that setup is called without Cython when CYTHON_BUILD is not set."""
    monkeypatch.delenv("CYTHON_BUILD", raising=False)
    mock_setup = MagicMock()
    monkeypatch.setattr(mod, "setup", mock_setup)

    mod.cythonized_setup("dummy_module")

    mock_setup.assert_called_once()
    args, kwargs = mock_setup.call_args
    assert kwargs["ext_modules"] == []


def test_cythonized_setup_success(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> None:
    """Test that setup is called with Cythonized extensions when CYTHON_BUILD is set."""
    os.environ["CYTHON_BUILD"] = "1"

    dummy_file = tmp_path.mktemp("src") / "dummy_module" / "foo.py"
    dummy_file.parent.mkdir(parents=True, exist_ok=True)
    dummy_file.write_text("def foo(): pass")

    monkeypatch.chdir(tmp_path)

    mock_setup = MagicMock()
    monkeypatch.setattr(mod, "setup", mock_setup)

    mock_cythonize = MagicMock(return_value=["compiled_module"])
    monkeypatch.setattr("python_build_utils.cythonize_setup.cythonize", mock_cythonize)

    mock_options = MagicMock()
    monkeypatch.setattr("python_build_utils.cythonize_setup.Options", mock_options)

    mod.cythonized_setup("dummy_module")

    mock_cythonize.assert_called_once()
    mock_setup.assert_called_once()
    _, kwargs = mock_setup.call_args
    assert kwargs["ext_modules"] == ["compiled_module"]


def test_cython_required_but_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ImportError is raised with clear message when Cython is missing."""
    os.environ["CYTHON_BUILD"] = "1"

    monkeypatch.setattr(mod, "setup", MagicMock())

    with (
        patch.dict(sys.modules, {"Cython": None, "Cython.Build": None, "Cython.Compiler": None}),
        pytest.raises(ImportError, match="Cython is required"),
    ):
        mod.cythonized_setup("dummy_module")
