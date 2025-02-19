import os
import sys
import sysconfig

import pytest
from click.testing import CliRunner

from python_build_utils.rename_wheel_files import rename_wheel_files


@pytest.fixture
def setup_wheel_files(tmpdir):
    dist_dir = tmpdir.mkdir("dist")
    wheel_file = dist_dir.join("example-1.0.0-py3-none-any.whl")
    wheel_file.write("")
    return str(dist_dir)


def test_rename_wheel_files_default_tags(setup_wheel_files):
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist_dir={dist_dir}"])

    python_version_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    platform_tag = sysconfig.get_platform().replace("-", "_")
    expected_tag = f"{python_version_tag}-{python_version_tag}-{platform_tag}"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def test_rename_wheel_files_custom_tags(setup_wheel_files):
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(
        rename_wheel_files, [f"--dist_dir={dist_dir}", "--python_version_tag=cp39", "--platform_tag=win_amd64"]
    )

    expected_tag = "cp39-cp39-win_amd64"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def test_rename_wheel_files_custom_wheel_tag(setup_wheel_files):
    dist_dir = setup_wheel_files
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist_dir={dist_dir}", "--wheel_tag=custom_tag"])

    expected_tag = "custom_tag"

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(dist_dir, f"example-1.0.0-{expected_tag}.whl"))


def test_rename_wheel_files_no_files_found(tmpdir):
    dist_dir = tmpdir.mkdir("dist")
    runner = CliRunner()
    result = runner.invoke(rename_wheel_files, [f"--dist_dir={dist_dir}"])

    assert result.exit_code == 0
    assert "No wheel files found" in result.output
