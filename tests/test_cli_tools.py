from click.testing import CliRunner

from python_build_utils.cli_tools import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "Commands" in result.output


def test_rename_wheel_files_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["rename_wheel_files", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_remove_tarballs_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["remove_tarballs", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
