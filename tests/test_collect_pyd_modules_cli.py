from click.testing import CliRunner

from python_build_utils.collect_pyd_modules import collect_pyd_submodules


def test_collect_pyd_submodules_no_site_packages(monkeypatch):
    """
    Test that collect_pyd_submodules handles the case where no site-packages directory is found.
    """

    def mock_get_venv_site_packages(venv_path):
        return None

    monkeypatch.setattr("python_build_utils.collect_pyd_modules.get_venv_site_packages", mock_get_venv_site_packages)

    runner = CliRunner()
    result = runner.invoke(collect_pyd_submodules, ["--venv_path", ""])
    assert "Could not locate site-packages in the current environment." in result.output


def test_collect_pyd_submodules_with_pyd_files(monkeypatch, tmp_path):
    """
    Test that collect_pyd_submodules correctly collects and prints .pyd files.
    """

    def mock_get_venv_site_packages(venv_path):
        return tmp_path

    monkeypatch.setattr("python_build_utils.collect_pyd_modules.get_venv_site_packages", mock_get_venv_site_packages)

    # Create mock .pyd files
    (tmp_path / "module1.pyd").touch()
    (tmp_path / "subdir" / "module2.pyd").mkdir(parents=True, exist_ok=True)
    (tmp_path / "subdir" / "module2.pyd").touch()

    runner = CliRunner()
    result = runner.invoke(collect_pyd_submodules, ["--venv_path", str(tmp_path)])
    assert "Collecting pyd in" in result.output
    assert "Found the following .pyd submodules:" in result.output
    assert "- module1" in result.output
    assert "- subdir.module2" in result.output
