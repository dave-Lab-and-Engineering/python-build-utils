from unittest.mock import patch

import pytest


@pytest.fixture
def mock_src_packages(tmp_path):
    """
    Fixture to create a temporary mock virtual environment site-packages directory.
    """
    src_packages = tmp_path / "src"
    src_packages.mkdir(parents=True, exist_ok=True)
    return src_packages


@pytest.fixture
def mock_venv_site_packages(tmp_path):
    """
    Fixture to create a temporary mock virtual environment site-packages directory.
    """
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)
    return site_packages


@pytest.fixture
def mock_collect_all_pyd_modules():
    """
    Fixture to mock the collect_all_pyd_modules function.
    """
    with patch("python_build_utils.collect_pyd_modules.collect_all_pyd_modules") as mock:
        yield mock


@pytest.fixture
def mock_get_venv_site_packages():
    """
    Fixture to mock the get_venv_site_packages function.
    """
    with patch("python_build_utils.collect_pyd_modules.get_venv_site_packages") as mock:
        yield mock
