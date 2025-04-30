import logging

from click.testing import CliRunner

from python_build_utils.collect_dep_modules import collect_dependencies


logger = logging.getLogger("python_build_utils.collect_dep_modules").setLevel(logging.INFO)
logger.setLevel(logging.INFO)


def test_collect_dependencies_basic(monkeypatch):
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *a, **kw: ["pkg1", "pkg2"],
    )
    runner = CliRunner()
    result = runner.invoke(collect_dependencies, ["--package", "example"])
    assert result.exit_code == 0
    assert "pkg1" in result.output
    assert "pkg2" in result.output


def test_collect_dependencies_no_package(monkeypatch, caplog):
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *a, **kw: [],
    )
    runner = CliRunner()
    with caplog.at_level(logging.INFO):
        result = runner.invoke(collect_dependencies, [])
    assert result.exit_code == 0
    assert any("No dependencies found." in m for m in caplog.messages)


def test_collect_dependencies_output_to_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *a, **kw: ["foo", "bar"],
    )
    output_file = tmp_path / "deps.txt"
    runner = CliRunner()
    result = runner.invoke(collect_dependencies, ["--output", str(output_file)])
    assert result.exit_code == 0
    content = output_file.read_text()
    assert "foo" in content
    assert "bar" in content


def test_collect_dependencies_regex(monkeypatch):
    monkeypatch.setattr(
        "python_build_utils.collect_dep_modules.collect_package_dependencies",
        lambda *a, **kw: ["modA", "modB"],
    )
    runner = CliRunner()
    result = runner.invoke(collect_dependencies, ["--package", "example", "--regex", "mod"])
    assert result.exit_code == 0
    assert "modA" in result.output
    assert "modB" in result.output
