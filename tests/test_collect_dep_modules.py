import json
from unittest import mock

import pytest

from python_build_utils.collect_dep_modules import get_dependency_tree, validate_command


def test_get_dependency_tree_success():
    """Test get_dependency_tree when pipdeptree runs successfully."""
    mock_output = json.dumps([{"key": "package1", "dependencies": []}])
    with (
        mock.patch("python_build_utils.collect_dep_modules.validate_command"),  # <-- bypass validation
        mock.patch("python_build_utils.collect_dep_modules.run_safe_subprocess", return_value=mock_output),
    ):
        result = get_dependency_tree()
        assert isinstance(result, list)
        assert result[0]["key"] == "package1"


def test_get_dependency_tree_invalid_json():
    """Test get_dependency_tree when pipdeptree returns invalid JSON."""
    mock_output = "invalid json"
    with (
        mock.patch("python_build_utils.collect_dep_modules.run_safe_subprocess", return_value=mock_output),
        mock.patch("python_build_utils.collect_dep_modules.validate_command"),  # <-- bypass validation
        pytest.raises(json.JSONDecodeError),
    ):
        get_dependency_tree()


def test_validate_command_unsafe_short_option():
    """Test validate_command when unsafe short options are detected."""
    with mock.patch("sys.exit") as mock_exit:
        validate_command(["python", "-m", "pipdeptree", "-x"])
        mock_exit.assert_called_once_with(1)
