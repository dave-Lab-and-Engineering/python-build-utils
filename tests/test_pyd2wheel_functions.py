from pathlib import Path

import pytest

from python_build_utils.pyd2wheel import (
    PydFileFormatError,
    _extract_pyd_file_info,
    _get_package_version,
    convert_pyd_to_wheel,
)


def test_extract_pyd_file_info_long_format():
    pyd_file = Path("dummy-0.1.0-py311-win_amd64.pyd")
    name, package_version, python_version, platform = _extract_pyd_file_info(pyd_file)
    assert name == "dummy"
    assert package_version == "0.1.0"
    assert python_version == "py311"
    assert platform == "win_amd64"


def test_extract_pyd_file_info_short_format():
    pyd_file = Path("DAVEcore.cp310-win_amd64.pyd")
    name, package_version, python_version, platform = _extract_pyd_file_info(pyd_file)
    assert name == "DAVEcore"
    assert package_version is None
    assert python_version == "cp310"
    assert platform == "win_amd64"


def test_extract_pyd_file_info_invalid_format():
    pyd_file = Path("invalid_format.pyd")
    with pytest.raises(PydFileFormatError):
        _extract_pyd_file_info(pyd_file)


def test_get_package_version_from_filename():
    package_version = _get_package_version(None, "0.1.0")
    assert package_version == "0.1.0"


def test_get_package_version_provided():
    package_version = _get_package_version("0.2.0", None)
    assert package_version == "0.2.0"


def test_get_package_version_error():
    with pytest.raises(ValueError):
        _get_package_version(None, None)


def test_convert_pyd_to_wheel(tmp_path):
    pyd_file = tmp_path / "dummy-0.1.0-py311-win_amd64.pyd"
    pyd_file.touch()
    wheel_file = convert_pyd_to_wheel(pyd_file)
    assert wheel_file.exists()
    assert wheel_file.suffix == ".whl"
