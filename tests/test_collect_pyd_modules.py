import sys
from pathlib import Path

import pytest

from python_build_utils.collect_pyd_modules import (
    _find_pyd_modules_in_site_packages,
    _get_venv_site_packages,
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
    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages)
    assert result == []


def test_collect_all_pyd_modules_with_files(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly collects .pyd files.
    """
    # Create mock .pyd files
    (mock_venv_site_packages / "module1.pyd").touch()
    (mock_venv_site_packages / "subdir" / "module2.pyd").mkdir(parents=True, exist_ok=True)
    (mock_venv_site_packages / "subdir" / "module2.pyd").touch()

    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages)
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
    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages, regex=regex)
    assert "module1" in result
    assert "module2" not in result


def test_collect_all_pyd_modules_remove_init(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules removes .__init__ from module names.
    """
    # Create mock .pyd file with __init__ in the name
    (mock_venv_site_packages / "package" / "__init__.pyd").mkdir(parents=True, exist_ok=True)
    (mock_venv_site_packages / "package" / "__init__.pyd").touch()

    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages)
    assert "package" in result
    assert "__init__" not in result


def test_collect_all_pyd_modules_invalid_path():
    """
    Test that collect_all_pyd_modules raises an exception or returns an empty list for an invalid path.
    """
    invalid_path = Path("/invalid/path/to/site-packages")
    result = _find_pyd_modules_in_site_packages(invalid_path)
    assert result == []


def test_collect_all_pyd_modules_case_insensitive_regex(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly filters .pyd files using a case-insensitive regex.
    """
    # Create mock .pyd files
    (mock_venv_site_packages / "Module1.pyd").touch()
    (mock_venv_site_packages / "module2.pyd").touch()

    regex = r"(?i)module1"  # Case-insensitive regex
    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages, regex=regex)
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

    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages)
    assert "package.subpackage.module" in result


def test_collect_all_pyd_modules_no_pyd_extension(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules ignores files without the .pyd extension.
    """
    # Create mock files with different extensions
    (mock_venv_site_packages / "module1.txt").touch()
    (mock_venv_site_packages / "module2.py").touch()

    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages)
    assert result == []


def test_collect_all_pyd_modules_with_platform_specific_suffix(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules correctly removes platform-specific suffixes from module names.
    """
    # Create mock .pyd files with platform-specific suffixes
    (mock_venv_site_packages / "module1.cp310-win_amd64.pyd").touch()
    (mock_venv_site_packages / "module2.cp39-win_amd64.pyd").touch()

    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages)
    assert "module1" in result
    assert "module2" in result


def test_collect_all_pyd_modules_empty_directory(mock_venv_site_packages):
    """
    Test that collect_all_pyd_modules returns an empty list when the directory is empty.
    """
    result = _find_pyd_modules_in_site_packages(mock_venv_site_packages)
    assert result == []

    def test_get_venv_site_packages_valid_path(tmp_path):
        """
        Test that get_venv_site_packages returns the correct site-packages path for a valid virtual environment.
        """
        venv_path = tmp_path / "venv"
        site_packages = venv_path / "Lib" / "site-packages"
        site_packages.mkdir(parents=True, exist_ok=True)

        result = _get_venv_site_packages(str(venv_path))
        assert result == site_packages


def test_get_venv_site_packages_invalid_path():
    """
    Test that get_venv_site_packages returns None for an invalid virtual environment path.
    """
    invalid_path = "/invalid/venv/path"
    result = _get_venv_site_packages(invalid_path)
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
    result = _get_venv_site_packages()
    assert result == site_packages


def test_get_venv_site_packages_no_site_packages(monkeypatch):
    """
    Test that get_venv_site_packages returns None when no site-packages directory is found in the current environment.
    """

    def mock_sys_path():
        return ["/some/random/path"]

    monkeypatch.setattr(sys, "path", mock_sys_path())
    result = _get_venv_site_packages()
    assert result is None


def test_get_venv_site_packages_valid_path(tmp_path):
    """
    Test that get_venv_site_packages returns the correct site-packages path for a valid virtual environment.
    """
    venv_path = tmp_path / "venv"
    site_packages = venv_path / "Lib" / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)

    result = _get_venv_site_packages(str(venv_path))
    assert result == site_packages
