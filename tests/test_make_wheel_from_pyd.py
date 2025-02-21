"""Test the pyd2wheel function."""

import pytest
from click.testing import CliRunner

from python_build_utils.pyd2wheel import pyd2wheel


@pytest.fixture
def setup_wheel_files(tmpdir):
    """Factory fixture to create a simple pyd file for testing."""

    def _create_pyd_file(dummy_file_name):
        pyd_file_name = tmpdir / dummy_file_name

        with open(pyd_file_name, "w", encoding="utf-8") as f:
            f.write('print("hello")')

        return str(pyd_file_name)

    return _create_pyd_file


def test_if_wheel_pyd_file_exists(setup_wheel_files):  # pylint: disable=redefined-outer-name
    """Test if the wheel file is created from the pyd file."""

    pyd_file = setup_wheel_files("dummy-0.1.0-py311-win_amd64.pyd")

    result = pyd2wheel(pyd_file=pyd_file)

    assert result.exists()


@pytest.mark.parametrize("dummy_file_name", ["DAVEcore.cp310-win_amd64.pyd"])
def test_make_wheel_format2(setup_wheel_files, dummy_file_name):  # pylint: disable=redefined-outer-name
    """Test different naming conventions."""
    pyd_file_name = setup_wheel_files(dummy_file_name)  # Call the factory with the parameter

    runner = CliRunner()
    result = runner.invoke(pyd2wheel, [f"{pyd_file_name}", "--package_version=1.2.3"])

    assert result
