"""
This module contains tests for the CLI tools provided by the python_build_utils package.
Functions:
    test_cli_help: Tests the help command of the CLI.
    test_cli_version: Tests the version option of the CLI.
    test_rename_wheel_files_command: Tests the help command for the rename-wheel-files command.
    test_remove_tarballs_command: Tests the help command for the remove-tarballs command.
"""

from click.testing import CliRunner

from python_build_utils import __version__
from python_build_utils.cli_tools import cli


def test_cli_help():
    """Tests the help command of the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "Commands" in result.output


def test_cli_version():
    """Tests the version command of the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_rename_wheel_files_command():
    """Tests the help command for the rename-wheel-files command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["rename-wheel-files", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_remove_tarballs_command():
    """Tests the help command for the remove-tarballs command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["remove-tarballs", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
