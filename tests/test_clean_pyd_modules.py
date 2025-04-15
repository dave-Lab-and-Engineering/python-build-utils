from pathlib import Path
from unittest.mock import patch

import pytest

from python_build_utils.clean_pyd_modules import clean_by_extensions


@pytest.fixture
def mock_site_packages_path(tmp_path):
    """Fixture to create a temporary site-packages directory."""
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    return site_packages


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_no_files_found(mock_echo, mock_site_packages_path):
    """Test when no files with the specified extension are found."""
    clean_by_extensions(src_path=mock_site_packages_path, regex=None, extension="*.pyd")

    mock_echo.assert_called_with(f"No *.pyd files found in {mock_site_packages_path}.")


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_with_files(mock_echo, mock_site_packages_path):
    """Test cleaning files with a specific extension."""
    # Create mock files
    file1 = mock_site_packages_path / "module1.pyd"
    file2 = mock_site_packages_path / "module2.pyd"
    file1.touch()
    file2.touch()

    clean_by_extensions(src_path=mock_site_packages_path, regex=None, extension="*.pyd")

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

    clean_by_extensions(src_path=mock_site_packages_path, regex="test", extension="*.pyd")

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
        clean_by_extensions(src_path=mock_site_packages_path, regex=None, extension="*.pyd")

    mock_echo.assert_any_call(f"Error removing {file1}: Permission denied", err=True)
    assert file1.exists()
