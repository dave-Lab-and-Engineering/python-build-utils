"""Tests for `remove_tarballs` function from `python_build_utils.remove_tarballs`."""

import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from python_build_utils.remove_tarballs import remove_tarballs


logger = logging.getLogger("python_build_utils.remove_tarballs")
logger.setLevel(logging.INFO)


@pytest.fixture
def setup_test_environment(tmp_path: Path) -> Path:
    """Create a temporary dist directory with a dummy tarball file.

    Args:
        tmp_path: Temporary directory path provided by pytest.

    Returns:
        Path: Path to the created 'dist' directory containing a dummy tarball.

    """
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    tarball_file = dist_dir / "test.tar.gz"
    tarball_file.write_text("dummy content")
    return dist_dir


def test_remove_tarballs(setup_test_environment: Path) -> None:
    """Test that `remove_tarballs` successfully removes existing tarball files.

    Args:
        setup_test_environment: Fixture providing a directory with a dummy tarball.

    """
    dist_dir = setup_test_environment
    runner = CliRunner()

    assert list(dist_dir.glob("*.tar.gz"))

    result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    assert result.exit_code == 0
    assert not list(dist_dir.glob("*.tar.gz"))


def test_remove_tarballs_no_files(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test `remove_tarballs` behavior when no tarball files are present.

    Args:
        tmp_path: Temporary directory provided by pytest.
        caplog: Fixture for capturing log output.

    """
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    runner = CliRunner()

    assert not list(dist_dir.glob("*.tar.gz"))

    with caplog.at_level(logging.INFO):
        result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    assert result.exit_code == 0
    assert "No tarball files found in" in caplog.text
