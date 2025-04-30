"""CLI tests for `collect_dependencies` in `python_build_utils.collect_dep_modules`.

Covers basic usage, file output, regex filtering, and fallback when no package is provided.
"""

import logging
from pathlib import Path

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from python_build_utils.collect_dep_modules import collect_dependencies


logger = logging.getLogger("python_build_utils.collect_dep_modules")
logger.setLevel(logging.INFO)


def test_collect_dependencies_basic(monkeypatch: MonkeyPatch) -> None:
    """Collect dependencies from a mock package and print to stdout."""
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *_, **__: ["pkg1", "pkg2"],
    )
    runner = CliRunner()
    result = runner.invoke(collect_dependencies, ["--package", "example"])

    assert result.exit_code == 0
    assert "pkg1" in result.output
    assert "pkg2" in result.output


def test_collect_dependencies_no_package(monkeypatch: MonkeyPatch, caplog: LogCaptureFixture) -> None:
    """Handle case where no package is provided and no dependencies are found."""
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *_, **__: [],
    )
    runner = CliRunner()
    with caplog.at_level(logging.INFO):
        result = runner.invoke(collect_dependencies, [])

    assert result.exit_code == 0
    assert any("No dependencies found." in m for m in caplog.messages)


def test_collect_dependencies_output_to_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Write collected dependencies to a specified output file."""
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *_, **__: ["foo", "bar"],
    )
    output_file = tmp_path / "deps.txt"

    runner = CliRunner()
    result = runner.invoke(collect_dependencies, ["--output", str(output_file)])

    assert result.exit_code == 0
    content = output_file.read_text()
    assert "foo" in content
    assert "bar" in content


def test_collect_dependencies_regex(monkeypatch: MonkeyPatch) -> None:
    """Filter collected dependencies using a regular expression."""
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *_, **__: ["modA", "modB"],
    )
    runner = CliRunner()
    result = runner.invoke(collect_dependencies, ["--package", "example", "--regex", "mod"])

    assert result.exit_code == 0
    assert "modA" in result.output
    assert "modB" in result.output
