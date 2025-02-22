"""
This module contains tests for the `rename_wheel_files` function from the `python_build_utils` package.
Fixtures:
    setup_wheel_files: Creates a temporary directory with a sample wheel file for testing.
Tests:
    test_rename_wheel_files_default_tags: Tests renaming wheel files with default tags based on the current
                                        Python-version and platform.
    test_rename_wheel_files_version: Test the version option of the rename_wheel_files command.
    test_rename_wheel_files_custom_tags: Tests renaming wheel files with custom Python version and platform tags.
    test_rename_wheel_files_custom_wheel_tag: Tests renaming wheel files with a custom wheel tag.
    test_rename_wheel_files_no_files_found: Tests the behavior when no wheel files are found in the specified directory.
"""

import os
import sys
import sysconfig

import pytest
from click.testing import CliRunner

from python_build_utils import __version__
from python_build_utils.rename_wheel_files import rename_wheel_files


@pytest.fixture
def setup_wheel_files(tmpdir):
    """Set up the fixtures for the test cases."""
    dist_dir = tmpdir.mkdir("dist")
    wheel_file = dist_dir.join("example-1.0.0-py3-none-any.whl")
    wheel_file.write("")
    return str(dist_dir)


def test_rename_wheel_files_version():
    """Tests the version option of the rename_wheel_files_version command."""
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_rename_wheel_files_default_tags(setup_wheel_files):  # pylint: disable=redefined-outer-name
    """Tests renaming wheel files with default tags based on the current Python version and platform."""
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist_dir={dist_dir}"])

    python_version_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    platform_tag = sysconfig.get_platform().replace("-", "_")
    expected_tag = f"{python_version_tag}-{python_version_tag}-{platform_tag}"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def test_rename_wheel_files_custom_tags(setup_wheel_files):  # pylint: disable=redefined-outer-name
    """Tests renaming wheel files with custom Python version and platform tags."""
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(
        rename_wheel_files, [f"--dist_dir={dist_dir}", "--python_version_tag=cp39", "--platform_tag=win_amd64"]
    )

    expected_tag = "cp39-cp39-win_amd64"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def test_rename_wheel_files_custom_wheel_tag(setup_wheel_files):  # pylint: disable=redefined-outer-name
    """Tests renaming wheel files with a custom wheel tag."""
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist_dir={dist_dir}", "--wheel_tag=custom_tag"])

    expected_tag = "custom_tag"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def test_rename_wheel_files_no_files_found(tmpdir):
    """Tests the behavior when no wheel files are found in the specified directory."""
    dist_dir = tmpdir.mkdir("dist")
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist_dir={dist_dir}"])

    assert result.exit_code == 0
    assert "No wheel files found" in result.output
