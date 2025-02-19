import glob

import pytest
from click.testing import CliRunner

from python_build_utils.remove_tarballs import remove_tarballs


@pytest.fixture
def setup_test_environment(tmp_path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    tarball_file = dist_dir / "test.tar.gz"
    tarball_file.write_text("dummy content")
    return dist_dir


def test_remove_tarballs(setup_test_environment):
    dist_dir = setup_test_environment
    runner = CliRunner()
    result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    assert result.exit_code == 0
    assert "Removed" in result.output
    assert not glob.glob(f"{dist_dir}/*.tar.gz")


def test_remove_tarballs_no_files(tmp_path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    runner = CliRunner()
    result = runner.invoke(remove_tarballs, ["--dist_dir", str(dist_dir)])

    assert result.exit_code == 0
    assert "No tarball files found" in result.output
