from pathlib import Path
from unittest.mock import patch

import pytest

from python_build_utils.clean_pyd_modules import clean_by_extensions, clean_pyd_modules


@pytest.fixture
def mock_site_packages_path(tmp_path):
    """Fixture to create a temporary site-packages directory."""
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    return site_packages


@patch("python_build_utils.clean_pyd_modules.get_venv_site_packages")
@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_pyd_modules_no_site_packages(mock_echo, mock_get_venv_site_packages):
    """Test when site-packages cannot be located."""
    mock_get_venv_site_packages.return_value = None

    clean_pyd_modules(venv_path="dummy_path", regex=None)

    mock_echo.assert_called_with("Could not locate site-packages in the specified environment.")


@patch("python_build_utils.clean_pyd_modules.clean_by_extensions")
@patch("python_build_utils.clean_pyd_modules.get_venv_site_packages")
@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_pyd_modules_with_extensions(
    mock_echo, mock_get_venv_site_packages, mock_clean_by_extensions, mock_site_packages_path
):
    """Test cleaning .pyd and .c files."""
    mock_get_venv_site_packages.return_value = mock_site_packages_path

    clean_pyd_modules(venv_path="dummy_path", regex="test")

    mock_echo.assert_any_call(f"Cleaning the *.pyd files with 'test' filter in '{mock_site_packages_path}'...")
    mock_echo.assert_any_call(f"Cleaning the *.c files with 'test' filter in '{mock_site_packages_path}'...")
    mock_clean_by_extensions.assert_any_call(mock_site_packages_path, "test", "*.pyd")
    mock_clean_by_extensions.assert_any_call(mock_site_packages_path, "test", "*.c")


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_no_files_found(mock_echo, mock_site_packages_path):
    """Test when no files with the specified extension are found."""
    clean_by_extensions(venv_site_packages=mock_site_packages_path, regex=None, extension="*.pyd")

    mock_echo.assert_called_with(f"No *.pyd files found in {mock_site_packages_path}.")


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_with_files(mock_echo, mock_site_packages_path):
    """Test cleaning files with a specific extension."""
    # Create mock files
    file1 = mock_site_packages_path / "module1.pyd"
    file2 = mock_site_packages_path / "module2.pyd"
    file1.touch()
    file2.touch()

    clean_by_extensions(venv_site_packages=mock_site_packages_path, regex=None, extension="*.pyd")

    mock_echo.assert_any_call(f"Removing {file1}")
    mock_echo.assert_any_call(f"Removing {file2}")
    assert not file1.exists()
    assert not file2.exists()


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_with_regex(mock_echo, mock_site_packages_path):
    """Test cleaning files with a regex filter."""
    # Create mock files
    file1 = mock_site_packages_path / "module1.pyd"
    file2 = mock_site_packages_path / "test_module.pyd"
    file1.touch()
    file2.touch()

    clean_by_extensions(venv_site_packages=mock_site_packages_path, regex="test", extension="*.pyd")

    mock_echo.assert_any_call(f"Removing {file2}")
    assert file1.exists()
    assert not file2.exists()


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_error_handling(mock_echo, mock_site_packages_path):
    """Test error handling when a file cannot be removed."""
    # Create a mock file
    file1 = mock_site_packages_path / "module1.pyd"
    file1.touch()

    # Mock unlink to raise an exception
    with patch.object(Path, "unlink", side_effect=Exception("Permission denied")):
        clean_by_extensions(venv_site_packages=mock_site_packages_path, regex=None, extension="*.pyd")

    mock_echo.assert_any_call(f"Error removing {file1}: Permission denied", err=True)
    assert file1.exists()
