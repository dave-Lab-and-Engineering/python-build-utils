import logging
import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from python_build_utils.collect_pyd_modules import collect_pyd_modules


logger = logging.getLogger("python_build_utils.collect_pyd_modules")
logger.setLevel(logging.INFO)


@pytest.fixture
def mock_venv_structure(tmp_path):
    """Creates a fake site-packages directory with .pyd and .py files."""
    site_packages = tmp_path / "Lib" / "site-packages"
    os.makedirs(site_packages / "pkg" / "subpkg", exist_ok=True)

    # Valid .pyd files
    (site_packages / "pkg" / "mod1.cp311-win_amd64.pyd").touch()
    (site_packages / "pkg" / "subpkg" / "mod2.cp311-win_amd64.pyd").touch()
    # __init__ file
    (site_packages / "pkg" / "__init__.cp311-win_amd64.pyd").touch()
    # .py file (for --collect-py test)
    (site_packages / "pkg" / "altmod.py").touch()

    return tmp_path


def test_collect_pyd_modules_default(mock_venv_structure):
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(mock_venv_structure)])
    modules = result.output.strip().splitlines()
    assert "pkg" in modules
    assert result.exit_code == 0
    assert "pkg.mod1" in result.output
    assert "pkg.subpkg.mod2" in result.output


def test_collect_pyd_modules_with_regex(mock_venv_structure):
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(mock_venv_structure), "--regex", "subpkg"])
    assert result.exit_code == 0
    assert "pkg.subpkg.mod2" in result.output
    assert "pkg.mod1" not in result.output


def test_collect_pyd_modules_py_mode(mock_venv_structure):
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(mock_venv_structure), "--collect-py"])
    assert result.exit_code == 0
    assert "pkg.altmod" in result.output
    assert "mod1" not in result.output


def test_collect_pyd_modules_output_file(mock_venv_structure):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        output_path = f.name

    try:
        runner = CliRunner()
        result = runner.invoke(collect_pyd_modules, ["--venv-path", str(mock_venv_structure), "--output", output_path])
        assert result.exit_code == 0
        contents = Path(output_path).read_text()
        assert "pkg.mod1" in contents
        assert "pkg.subpkg.mod2" in contents
    finally:
        os.remove(output_path)


def test_collect_pyd_modules_site_packages_not_found(monkeypatch):
    # Lege sys.path simuleren
    monkeypatch.setattr("sys.path", [])

    # Logger output opvangen
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger("python_build_utils.collect_pyd_modules")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # CLI aanroepen
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, [])

    # Handler verwijderen
    logger.removeHandler(handler)

    assert result.exit_code == 0
    assert "Could not locate site-packages" in log_stream.getvalue()


def test_collect_pyd_modules_invalid_path(tmp_path):
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--venv-path", str(tmp_path / "does_not_exist")])
    assert result.exit_code == 0
    assert "does not exist" in result.output


def test_collect_pyd_modules_site_packages_not_found(monkeypatch, caplog):
    logger = logging.getLogger("python_build_utils.collect_pyd_modules")
    monkeypatch.setattr("sys.path", [])
    with caplog.at_level(logging.INFO):
        runner = CliRunner()
        result = runner.invoke(collect_pyd_modules, [])
    assert result.exit_code == 0
    assert any("Could not locate site-packages" in record.message for record in caplog.records)
