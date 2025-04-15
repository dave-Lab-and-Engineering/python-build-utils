from unittest.mock import patch

import pytest
from click.testing import CliRunner

from python_build_utils.clean_pyd_modules import clean_pyd_modules


@pytest.fixture
def mock_site_packages_path(tmp_path):
    """Fixture to create a temporary site-packages directory."""
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    return site_packages


@patch("python_build_utils.clean_pyd_modules.get_venv_site_packages")
def test_clean_pyd_modules_no_site_packages(mock_get_venv_site_packages):
    """Test when site-packages cannot be located."""
    mock_get_venv_site_packages.return_value = None

    runner = CliRunner()
    result = runner.invoke(clean_pyd_modules, ["--venv-path", "dummy_path"])

    assert "Could not locate site-packages in the specified environment." in result.output
    assert result.exit_code == 0


@patch("python_build_utils.clean_pyd_modules.clean_by_extensions")
@patch("python_build_utils.clean_pyd_modules.get_venv_site_packages")
def test_clean_pyd_modules_with_extensions(
    mock_get_venv_site_packages, mock_clean_by_extensions, mock_site_packages_path
):
    """Test cleaning .pyd and .c files."""
    mock_get_venv_site_packages.return_value = mock_site_packages_path

    runner = CliRunner()
    result = runner.invoke(clean_pyd_modules, ["--venv-path", "dummy_path", "--regex", "test"])

    assert f"Cleaning the *.pyd files with 'test' filter in '{mock_site_packages_path}'..." in result.output
    assert f"Cleaning the *.c files with 'test' filter in '{mock_site_packages_path}'..." in result.output

    # Corrected: match the keyword arguments the real code is using
    mock_clean_by_extensions.assert_any_call(
        venv_site_packages=mock_site_packages_path, regex="test", extension="*.pyd"
    )
    mock_clean_by_extensions.assert_any_call(venv_site_packages=mock_site_packages_path, regex="test", extension="*.c")

    assert result.exit_code == 0
