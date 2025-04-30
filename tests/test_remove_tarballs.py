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
import logging

import pytest
from click.testing import CliRunner

from python_build_utils.remove_tarballs import remove_tarballs

logger = logging.getLogger("python_build_utils.remove_tarballs")
logger.setLevel(logging.INFO)


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


def test_remove_tarballs(setup_test_environment):
    """
    Tests the removal of tarball files in the specified directory.

    Args:
        setup_test_environment (pathlib.Path): A pytest fixture that sets up
        a test environment with a dummy tarball file.
    """
    dist_dir = setup_test_environment
    runner = CliRunner()

    # Ensure the tarball file exists before running the command
    assert len(glob.glob(f"{dist_dir}/*.tar.gz")) == 1

    # Run the remove_tarballs command
    result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    # Ensure the tarball file is removed
    assert result.exit_code == 0
    assert len(glob.glob(f"{dist_dir}/*.tar.gz")) == 0


def test_remove_tarballs_no_files(tmp_path, caplog):
    """
    Tests the behavior when no tarball files are found in the specified directory.

    Args:
        tmp_path (pathlib.Path): A temporary directory path provided by pytest.
        caplog: A pytest fixture to capture log messages.
    """
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    runner = CliRunner()

    # Ensure no tarball files exist in the directory
    assert len(glob.glob(f"{dist_dir}/*.tar.gz")) == 0

    # Run the remove_tarballs command
    with caplog.at_level(logging.INFO):
        result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    # Ensure the command exits successfully and logs the appropriate message
    assert result.exit_code == 0
    assert "No tarball files found in" in caplog.text
