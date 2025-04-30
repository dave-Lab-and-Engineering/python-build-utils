import logging

from click.testing import CliRunner

from python_build_utils.cli_tools import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "A collection of CLI tools for Python build utilities." in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "Version: " in result.output


def test_cli_verbose_levels(monkeypatch):
    runner = CliRunner()

    # patch logger to observe level setting
    import python_build_utils.cli_tools as mod

    test_logger = logging.getLogger("test_logger")
    monkeypatch.setattr(mod, "logger", test_logger)

    result = runner.invoke(mod.cli, ["-v"])
    assert result.exit_code == 0
    assert test_logger.level == logging.INFO

    result = runner.invoke(mod.cli, ["-vv"])
    assert result.exit_code == 0
    assert test_logger.level == logging.DEBUG

    result = runner.invoke(mod.cli, [])
    assert result.exit_code == 0
    assert test_logger.level == logging.WARNING
