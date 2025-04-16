import pytest


@pytest.fixture
def mock_site_packages_path(tmp_path):
    """Fixture to create a temporary site-packages directory."""
    site_packages = tmp_path / "site-packages"
    site_packages.mkdir()
    return site_packages
