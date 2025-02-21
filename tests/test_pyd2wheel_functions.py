"""
This module contains unit tests for the functions in the `python_build_utils.pyd2wheel` module.

Tests included:
- `test_extract_pyd_file_info_long_format`: Tests `_extract_pyd_file_info` with a long format filename.
- `test_extract_pyd_file_info_short_format`: Tests `_extract_pyd_file_info` with a short format filename.
- `test_extract_pyd_file_info_invalid_format`: Tests `_extract_pyd_file_info` with an invalid format filename.
- `test_extract_pyd_file_info_invalid_suffix`: Tests `_extract_pyd_file_info` with an invalid file suffix.
- `test_get_package_version_from_filename`: Tests `_get_package_version` when the version is provided in the filename.
- `test_get_package_version_provided`: Tests `_get_package_version` when the version is explicitly provided.
- `test_get_package_version_error`: Tests `_get_package_version` when no version is provided, expecting an error.
- `test_convert_pyd_to_wheel`: Tests `convert_pyd_to_wheel` to ensure it converts a .pyd file to a .whl file correctly.
"""

from pathlib import Path

import pytest

from python_build_utils.pyd2wheel import (
    PydFileFormatError,
    PydFileSuffixError,
    VersionNotFoundError,
    _extract_pyd_file_info,
    _get_package_version,
    convert_pyd_to_wheel,
)


def test_extract_pyd_file_info_long_format():
    """
    Test the `_extract_pyd_file_info` function with a long format filename.

    This test checks if the function correctly extracts the following information
    from a `.pyd` file with a long format filename:
    - name
    - package version
    - python version
    - platform

    The test uses a dummy filename "dummy-0.1.0-py311-win_amd64.pyd" and asserts
    that the extracted values match the expected results:
    - name: "dummy"
    - package version: "0.1.0"
    - python version: "py311"
    - platform: "win_amd64"
    """
    pyd_file = Path("dummy-0.1.0-py311-win_amd64.pyd")
    name, package_version, python_version, platform = _extract_pyd_file_info(pyd_file)
    assert name == "dummy"
    assert package_version == "0.1.0"
    assert python_version == "py311"
    assert platform == "win_amd64"


def test_extract_pyd_file_info_short_format():
    """
    Test the `_extract_pyd_file_info` function with a short format filename.

    This test verifies that the function correctly extracts the name, package version,
    Python version, and platform from a `.pyd` file with a short format filename.

    Assertions:
        - The name should be "DAVEcore".
        - The package version should be `None`.
        - The Python version should be "cp310".
        - The platform should be "win_amd64".
    """
    pyd_file = Path("DAVEcore.cp310-win_amd64.pyd")
    name, package_version, python_version, platform = _extract_pyd_file_info(pyd_file)
    assert name == "DAVEcore"
    assert package_version is None
    assert python_version == "cp310"
    assert platform == "win_amd64"


def test_extract_pyd_file_info_invalid_format():
    """
    Test case for `_extract_pyd_file_info` function with an invalid .pyd file format.

    This test ensures that the `_extract_pyd_file_info` function raises a
    `PydFileFormatError` when provided with a .pyd file that has an invalid format.

    Raises:
        PydFileFormatError: If the .pyd file format is invalid.
    """
    pyd_file = Path("invalid_format.pyd")
    with pytest.raises(PydFileFormatError):
        _extract_pyd_file_info(pyd_file)


def test_extract_pyd_file_info_invalid_suffix():
    """
    Test case for `_extract_pyd_file_info` function with an invalid suffix.

    This test ensures that the `_extract_pyd_file_info` function raises a
    `PydFileSuffixError` when provided with a `.whl` file that has an invalid
    suffix.

    Raises:
        PydFileSuffixError: If the suffix of the provided `.whl` file is invalid.
    """
    pyd_file = Path("DAVEcore.cp310-win_amd64.whl")
    with pytest.raises(PydFileSuffixError):
        _extract_pyd_file_info(pyd_file)


def test_get_package_version_from_filename():
    """
    Test the `_get_package_version` function to ensure it correctly extracts the package version from the provided
    filename.

    This test checks that the function returns the expected version string when given a filename with a specific
    version.

    Assertions:
        - The function should return "0.1.0" when the filename contains "0.1.0".
    """
    package_version = _get_package_version(None, "0.1.0")
    assert package_version == "0.1.0"


def test_get_package_version_provided():
    """
    Test the _get_package_version function when a version is provided.

    This test ensures that the _get_package_version function returns the
    provided version correctly when a version string is given as an argument.

    Assertions:
        - The function should return the provided version string.
    """
    package_version = _get_package_version("0.2.0", None)
    assert package_version == "0.2.0"


def test_get_package_version_error():
    """
    Test case for _get_package_version function to ensure it raises a VersionNotFoundError
    when called with None as both arguments.

    This test verifies that the _get_package_version function correctly handles the
    case where the package name and version are not provided, and raises the appropriate
    exception.

    Raises:
        VersionNotFoundError: If the package name and version are not provided.
    """
    with pytest.raises(VersionNotFoundError):
        _get_package_version(None, None)


def test_convert_pyd_to_wheel(tmp_path):
    """
    Test the conversion of a .pyd file to a .whl file.

    This test creates a dummy .pyd file in a temporary directory, converts it to a .whl file using the
    `convert_pyd_to_wheel` function, and verifies that the resulting .whl file exists and has the correct suffix.

    Args:
        tmp_path (pathlib.Path): A temporary directory provided by pytest.

    Asserts:
        The resulting .whl file exists.
        The resulting file has a .whl suffix.
    """
    pyd_file = tmp_path / "dummy-0.1.0-py311-win_amd64.pyd"
    pyd_file.touch()
    wheel_file = convert_pyd_to_wheel(pyd_file)
    assert wheel_file.exists()
    assert wheel_file.suffix == ".whl"
