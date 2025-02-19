"""Tests for the `remove_tarballs` function from the `python_build_utils.remove_tarballs` module.

This module contains tests for the `remove_tarballs` function from the
`python_build_utils.remove_tarballs` module. It uses pytest for testing
and click.testing for invoking the command-line interface.

Functions:
    setup_test_environment(tmp_path): Sets up a test environment by creating
        a temporary directory structure and a dummy tarball file.
    test_remove_tarballs_version: Tests if the version option is working
    test_remove_tarballs(setup_test_environment): Tests the removal of tarball
        files in the specified directory.
    test_remove_tarballs_no_files(tmp_path): Tests the behavior when no tarball
        files are found in the specified directory.
"""

import glob

import pytest
from click.testing import CliRunner

from python_build_utils import __version__
from python_build_utils.remove_tarballs import remove_tarballs


@pytest.fixture
def setup_test_environment(tmp_path):
    """
    Sets up a test environment by creating a temporary directory structure
    and a dummy tarball file.

    Args:
        tmp_path (pathlib.Path): A temporary directory path provided by pytest.

    Returns:
        pathlib.Path: The path to the 'dist' directory containing the dummy tarball file.
    """
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    tarball_file = dist_dir / "test.tar.gz"
    tarball_file.write_text("dummy content")
    return dist_dir


def test_remove_tarballs_version():
    """Tests the version option of the remove_tarballs command."""
    runner = CliRunner()
    result = runner.invoke(remove_tarballs, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_remove_tarballs(setup_test_environment):  # pylint: disable=redefined-outer-name
    """Tests the removal of tarball files in the specified directory."""
    dist_dir = setup_test_environment
    runner = CliRunner()
    result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    assert result.exit_code == 0
    assert "Removed" in result.output
    assert not glob.glob(f"{dist_dir}/*.tar.gz")


def test_remove_tarballs_no_files(tmp_path):
    """Tests the behavior when no tarball files are found in the specified directory."""
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    runner = CliRunner()
    result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    assert result.exit_code == 0
    assert "No tarball files found" in result.output
