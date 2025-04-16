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

import pytest


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
