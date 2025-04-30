"""CLI tests for `python_build_utils.collect_pyd_modules`."""

import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from python_build_utils.collect_pyd_modules import collect_pyd_modules


logger = logging.getLogger("python_build_utils.collect_pyd_modules")
logger.setLevel(logging.INFO)


@pytest.fixture
def mock_venv_structure(tmp_path: Path) -> Path:
    """Create a mock venv with site-packages and test files."""
    site_packages = tmp_path / "Lib" / "site-packages"
    site_packages.mkdir(parents=True)

    # Create valid .pyd files
    (site_packages / "pkg").mkdir()
    (site_packages / "pkg" / "mod1.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "subpkg").mkdir()
    (site_packages / "pkg" / "subpkg" / "mod2.cp311-win_amd64.pyd").touch()

    # __init__ file
    (site_packages / "pkg" / "__init__.cp311-win_amd64.pyd").touch()

    # .py file (for --collect-py)
    (site_packages / "pkg" / "altmod.py").touch()

    return tmp_path


def test_collect_pyd_modules_default(mock_venv_structure: Path) -> None:
    """Test collection of .pyd modules with default settings."""
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(mock_venv_structure)])

    assert result.exit_code == 0
    output = result.output.strip().splitlines()
    assert "pkg" in output
    assert "pkg.mod1" in output
    assert "pkg.subpkg.mod2" in output


def test_collect_pyd_modules_with_regex(mock_venv_structure: Path) -> None:
    """Test collection of .pyd modules filtered by regex."""
    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure), "--regex", "subpkg"],
    )

    assert result.exit_code == 0
    output = result.output
    assert "pkg.subpkg.mod2" in output
    assert "pkg.mod1" not in output


def test_collect_pyd_modules_py_mode(mock_venv_structure: Path) -> None:
    """Test collection of .py modules when using --collect-py."""
    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure), "--collect-py"],
    )

    assert result.exit_code == 0
    output = result.output
    assert "pkg.altmod" in output
    assert "mod1" not in output


def test_collect_pyd_modules_output_file(mock_venv_structure: Path, tmp_path: Path) -> None:
    """Test outputting collected modules to a specified file."""
    output_file = tmp_path / "modules.txt"

    runner = CliRunner()
    result = runner.invoke(
        collect_pyd_modules,
        ["--venv-path", str(mock_venv_structure), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    contents = output_file.read_text()
    assert "pkg.mod1" in contents
    assert "pkg.subpkg.mod2" in contents


def test_collect_pyd_modules_site_packages_not_found(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test behavior when site-packages directory is not found."""
    monkeypatch.setattr("sys.path", [])

    runner = CliRunner()
    with caplog.at_level(logging.INFO):
        result = runner.invoke(collect_pyd_modules, [])

    assert result.exit_code == 0
    assert any("Could not locate site-packages" in r.message for r in caplog.records)


def test_collect_pyd_modules_invalid_path(tmp_path: Path) -> None:
    """Test behavior when provided venv-path does not exist."""
    invalid_path = tmp_path / "does_not_exist"

    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(invalid_path)])

    assert result.exit_code == 0
    assert "does not exist" in result.output
