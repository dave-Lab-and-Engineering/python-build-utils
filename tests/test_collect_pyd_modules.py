import sys
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from click.testing import CliRunner

from python_build_utils.collect_pyd_modules import (
    collect_all_pyd_modules,
    collect_pyd_modules,
    get_venv_site_packages,
)


@pytest.fixture
def mock_venv_site_packages(tmp_path):
    """
    Fixture to create a temporary mock virtual environment site-packages directory.
    """
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)
    return site_packages


def test_collect_all_pyd_modules_no_files(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules returns an empty list when no .pyd files are present.
    """
    result = collect_all_pyd_modules(mock_venv_site_packages)
    assert result == []


def test_collect_all_pyd_modules_with_files(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly collects .pyd files.
    """
    # Create mock .pyd files
    (mock_venv_site_packages / "module1.pyd").touch()
    (mock_venv_site_packages / "subdir" / "module2.pyd").mkdir(parents=True, exist_ok=True)
    (mock_venv_site_packages / "subdir" / "module2.pyd").touch()

    result = collect_all_pyd_modules(mock_venv_site_packages)
    assert "module1" in result
    assert "subdir.module2" in result


def test_collect_all_pyd_modules_with_regex(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly filters .pyd files using a regex.
    """
    # Create mock .pyd files
    (mock_venv_site_packages / "module1.pyd").touch()
    (mock_venv_site_packages / "module2.pyd").touch()

    regex = r"module1"
    result = collect_all_pyd_modules(mock_venv_site_packages, regex=regex)
    assert "module1" in result
    assert "module2" not in result


def test_collect_all_pyd_modules_remove_init(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules removes .__init__ from module names.
    """
    # Create mock .pyd file with __init__ in the name
    (mock_venv_site_packages / "package" / "__init__.pyd").mkdir(parents=True, exist_ok=True)
    (mock_venv_site_packages / "package" / "__init__.pyd").touch()

    result = collect_all_pyd_modules(mock_venv_site_packages)
    assert "package" in result
    assert "__init__" not in result


def test_collect_all_pyd_modules_invalid_path():
    """
    Test that collect_all_pyd_modules raises an exception or returns an empty list for an invalid path.
    """
    invalid_path = Path("/invalid/path/to/site-packages")
    result = collect_all_pyd_modules(invalid_path)
    assert result == []


def test_collect_all_pyd_modules_case_insensitive_regex(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly filters .pyd files using a case-insensitive regex.
    """
    # Create mock .pyd files
    (mock_venv_site_packages / "Module1.pyd").touch()
    (mock_venv_site_packages / "module2.pyd").touch()

    regex = r"(?i)module1"  # Case-insensitive regex
    result = collect_all_pyd_modules(mock_venv_site_packages, regex=regex)
    assert "Module1" in result
    assert "module2" not in result


def test_collect_all_pyd_modules_nested_directories(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly collects .pyd files from deeply nested directories.
    """
    # Create mock .pyd files in nested directories
    nested_dir = mock_venv_site_packages / "package" / "subpackage"
    nested_dir.mkdir(parents=True, exist_ok=True)
    (nested_dir / "module.pyd").touch()

    result = collect_all_pyd_modules(mock_venv_site_packages)
    assert "package.subpackage.module" in result


def test_collect_all_pyd_modules_no_pyd_extension(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules ignores files without the .pyd extension.
    """
    # Create mock files with different extensions
    (mock_venv_site_packages / "module1.txt").touch()
    (mock_venv_site_packages / "module2.py").touch()

    result = collect_all_pyd_modules(mock_venv_site_packages)
    assert result == []


def test_collect_all_pyd_modules_with_platform_specific_suffix(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly removes platform-specific suffixes from module names.
    """
    # Create mock .pyd files with platform-specific suffixes
    (mock_venv_site_packages / "module1.cp310-win_amd64.pyd").touch()
    (mock_venv_site_packages / "module2.cp39-win_amd64.pyd").touch()

    result = collect_all_pyd_modules(mock_venv_site_packages)
    assert "module1" in result
    assert "module2" in result


def test_collect_all_pyd_modules_empty_directory(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules returns an empty list when the directory is empty.
    """
    result = collect_all_pyd_modules(mock_venv_site_packages)
    assert result == []

    def test_get_venv_site_packages_valid_path(tmp_path):
        """
        Test that get_venv_site_packages returns the correct site-packages path for a valid virtual environment.
        """
        venv_path = tmp_path / "venv"
        site_packages = venv_path / "Lib" / "site-packages"
        site_packages.mkdir(parents=True, exist_ok=True)

        result = get_venv_site_packages(str(venv_path))
        assert result == site_packages


def test_get_venv_site_packages_invalid_path():
    """
    Test that get_venv_site_packages returns None for an invalid virtual environment path.
    """
    invalid_path = "/invalid/venv/path"
    result = get_venv_site_packages(invalid_path)
    assert result is None


def test_get_venv_site_packages_none_path(monkeypatch, tmp_path):
    """
    Test that get_venv_site_packages returns the site-packages path for the current environment when no path is provided.
    """
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)

    def mock_sys_path():
        return [str(site_packages)]

    monkeypatch.setattr(sys, "path", mock_sys_path())
    result = get_venv_site_packages()
    assert result == site_packages


def test_get_venv_site_packages_no_site_packages(monkeypatch):
    """
    Test that get_venv_site_packages returns None when no site-packages directory is found in the current environment.
    """

    def mock_sys_path():
        return ["/some/random/path"]

    monkeypatch.setattr(sys, "path", mock_sys_path())
    result = get_venv_site_packages()
    assert result is None


def test_get_venv_site_packages_valid_path(tmp_path):
    """
    Test that get_venv_site_packages returns the correct site-packages path for a valid virtual environment.
    """
    venv_path = tmp_path / "venv"
    site_packages = venv_path / "Lib" / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)

    result = get_venv_site_packages(str(venv_path))
    assert result == site_packages


def test_collect_pyd_submodules_no_venv_path(mock_get_venv_site_packages, mock_collect_all_pyd_modules):
    """
    Test collect_pyd_submodules when no venv_path is provided.
    """
    mock_get_venv_site_packages.return_value = None
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, [])
    assert "Could not locate site-packages in the specified environment." in result.output
    assert result.exit_code == 0


def test_collect_pyd_submodules_no_pyd_modules(mock_get_venv_site_packages, mock_collect_all_pyd_modules):
    """
    Test collect_pyd_submodules when no .pyd modules are found.
    """
    mock_get_venv_site_packages.return_value = "/mock/site-packages"
    mock_collect_all_pyd_modules.return_value = []
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, [])
    assert "Collecting .pyd modules in '/mock/site-packages'..." in result.output
    assert "No .pyd modules found." in result.output
    assert result.exit_code == 0


def test_collect_pyd_submodules_with_pyd_modules(mock_get_venv_site_packages, mock_collect_all_pyd_modules):
    """
    Test collect_pyd_submodules when .pyd modules are found.
    """
    mock_get_venv_site_packages.return_value = "/mock/site-packages"
    mock_collect_all_pyd_modules.return_value = ["module1", "module2"]
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, [])
    assert "Found the following .pyd submodules:" in result.output
    assert "- module1" in result.output
    assert "- module2" in result.output
    assert result.exit_code == 0


def test_collect_pyd_submodules_with_regex(mock_get_venv_site_packages, mock_collect_all_pyd_modules):
    """
    Test collect_pyd_submodules with a regex filter.
    """
    mock_get_venv_site_packages.return_value = "/mock/site-packages"
    mock_collect_all_pyd_modules.return_value = ["module1"]
    runner = CliRunner()
    result = runner.invoke(collect_pyd_modules, ["--regex", "module1"])
    assert "Found the following .pyd submodules:" in result.output
    assert "- module1" in result.output
    assert result.exit_code == 0


def test_collect_pyd_submodules_write_to_file(mock_get_venv_site_packages, mock_collect_all_pyd_modules):
    """
    Test collect_pyd_submodules when writing the output to a file.
    """
    mock_get_venv_site_packages.return_value = "/mock/site-packages"
    mock_collect_all_pyd_modules.return_value = ["module1", "module2"]
    runner = CliRunner()
    with patch("builtins.open", mock_open()) as mocked_file:
        result = runner.invoke(collect_pyd_modules, ["--output", "output.txt"])
        mocked_file.assert_called_once_with("output.txt", "w")
        mocked_file().write.assert_called_once_with("module1\nmodule2")
    assert "Module list written to output.txt" in result.output
    assert result.exit_code == 0
