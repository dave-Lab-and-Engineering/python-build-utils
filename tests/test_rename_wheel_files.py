"""This module contains tests for the `rename_wheel_files` function from the `python_build_utils` package.
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

import logging
import os
import sys
import sysconfig
from io import StringIO

import pytest
from click.testing import CliRunner

from python_build_utils.rename_wheel_files import rename_wheel_files


@pytest.fixture
def setup_wheel_files(tmpdir):
    """Set upt the fixtures for the test cases."""
    dist_dir = tmpdir.mkdir("dist")
    wheel_file = dist_dir.join("example-1.0.0-py3-none-any.whl")
    wheel_file.write("")
    return str(dist_dir)


def test_rename_wheel_files_default_tags(setup_wheel_files):  # pylint: disable=redefined-outer-name
    """Tests renaming wheel files with default tags based on the current Python version and platform."""
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist-dir={dist_dir}"])

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
        rename_wheel_files,
        [f"--dist-dir={dist_dir}", "--python-version-tag=cp39", "--platform-tag=win_amd64"],
    )

    expected_tag = "cp39-cp39-win_amd64"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def test_rename_wheel_files_custom_wheel_tag(setup_wheel_files):  # pylint: disable=redefined-outer-name
    """Tests renaming wheel files with a custom wheel tag."""
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist-dir={dist_dir}", "--wheel-tag=custom_tag"])

    expected_tag = "custom_tag"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def create_dummy_wheel(dist_dir, filename):
    dist_dir.mkdir(parents=True, exist_ok=True)
    file = dist_dir / filename
    file.write_text("dummy content")
    return file


def test_rename_with_defaults(tmp_path):
    wheel = create_dummy_wheel(tmp_path, "package-1.0.0-py3-none-any.whl")

    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path)])

    assert result.exit_code == 0
    pyver = f"cp{sys.version_info.major}{sys.version_info.minor}"
    plat = sysconfig.get_platform().replace("-", "_")

    expected_suffix = f"{pyver}-{pyver}-{plat}.whl"
    assert any(f.endswith(expected_suffix) for f in os.listdir(tmp_path))


def test_rename_with_custom_tags(tmp_path):
    wheel = create_dummy_wheel(tmp_path, "pkg-2.0.0-py3-none-any.whl")

    runner = CliRunner()
    result = runner.invoke(
        rename_wheel_files,
        ["--dist-dir", str(tmp_path), "--python-version-tag", "cp313", "--platform-tag", "linux_x86_64"],
    )

    assert result.exit_code == 0
    expected = "pkg-2.0.0-cp313-cp313-linux_x86_64.whl"
    assert (tmp_path / expected).exists()


def test_rename_with_full_wheel_tag(tmp_path):
    wheel = create_dummy_wheel(tmp_path, "abc-1.2.3-py3-none-any.whl")

    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path), "--wheel-tag", "cp310-cp310-win_amd64"])

    assert result.exit_code == 0
    assert (tmp_path / "abc-1.2.3-cp310-cp310-win_amd64.whl").exists()


def test_no_matching_files(tmp_path, caplog):
    runner = CliRunner()

    # Tijdelijke plain stream handler toevoegen
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("python_build_utils.rename_wheel_files")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path)])
    handler.flush()

    log_output = stream.getvalue()
    logger.removeHandler(handler)

    assert result.exit_code == 0
    assert "No matching wheel files" in log_output


def test_file_exists_error(tmp_path, monkeypatch, caplog):
    wheel = create_dummy_wheel(tmp_path, "example-1.0-py3-none-any.whl")
    target = tmp_path / "example-1.0-custom.whl"
    target.write_text("already exists")

    def mock_rename(src, dst):
        raise FileExistsError("Mocked")

    monkeypatch.setattr(os, "rename", mock_rename)

    runner = CliRunner()
    with caplog.at_level(logging.ERROR):
        result = runner.invoke(rename_wheel_files, ["--dist-dir", str(tmp_path), "--wheel-tag", "custom"])

    assert result.exit_code == 0
    assert any("Error" in message for message in caplog.messages)
