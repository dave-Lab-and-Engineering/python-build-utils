import json
from unittest import mock

import pytest
from click.testing import CliRunner

from python_build_utils.collect_dep_modules import (
    _collect_dependency_names,
    _find_package_node,
    _get_dependency_tree,
    collect_dependencies,
)


def test_get_dependency_tree_success():
    """Test get_dependency_tree when pipdeptree runs successfully."""
    mock_output = json.dumps([{"key": "package1", "dependencies": []}])
    with (
        mock.patch("python_build_utils.collect_dep_modules.run_safe_subprocess", return_value=mock_output),
    ):
        result = _get_dependency_tree()
        assert isinstance(result, list)
        assert result[0]["key"] == "package1"


def test_get_dependency_tree_invalid_json():
    """Test get_dependency_tree when pipdeptree returns invalid JSON."""
    mock_output = "invalid json"
    with (
        mock.patch("python_build_utils.collect_dep_modules.run_safe_subprocess", return_value=mock_output),
        pytest.raises(json.JSONDecodeError),
    ):
        _get_dependency_tree()


def test_get_dependency_tree_empty_output():
    """Test get_dependency_tree when pipdeptree returns an empty output."""
    mock_output = "[]"
    with mock.patch("python_build_utils.collect_dep_modules.run_safe_subprocess", return_value=mock_output):
        result = _get_dependency_tree()
        assert isinstance(result, list)
        assert len(result) == 0


def test_collect_dependencies_no_package_found():
    """Test collect_dependencies when the specified package is not found."""
    mock_dep_tree = [{"key": "package1", "dependencies": []}]
    with mock.patch("python_build_utils.collect_dep_modules.get_dependency_tree", return_value=mock_dep_tree):
        runner = CliRunner()
        result = runner.invoke(collect_dependencies, ["--package", "nonexistent-package"])
        assert result.exit_code == 0
        assert "Package '('nonexistent-package',)' not found in the environment." in result.output


def test_collect_dependencies_no_dependencies():
    """Test collect_dependencies when the package has no dependencies."""
    mock_dep_tree = [{"key": "package1", "dependencies": []}]
    with mock.patch("python_build_utils.collect_dep_modules.get_dependency_tree", return_value=mock_dep_tree):
        runner = CliRunner()
        result = runner.invoke(collect_dependencies, ["--package", "package1"])
        assert result.exit_code == 0
        assert "No dependencies found" in result.output


def test_collect_dependency_names_no_dependencies():
    """Test collect_dependency_names with no dependencies."""
    dependencies = []
    result = _collect_dependency_names(dependencies)
    assert result == []


def test_collect_dependency_names_single_dependency():
    """Test collect_dependency_names with a single dependency."""
    dependencies = [{"package_name": "package1", "dependencies": []}]
    result = _collect_dependency_names(dependencies)
    assert result == ["package1"]


def test_collect_dependency_names_multiple_dependencies():
    """Test collect_dependency_names with multiple dependencies."""
    dependencies = [
        {"package_name": "package1", "dependencies": []},
        {"package_name": "package2", "dependencies": []},
    ]
    result = _collect_dependency_names(dependencies)
    assert result == ["package1", "package2"]


def test_collect_dependency_names_nested_dependencies():
    """Test collect_dependency_names with nested dependencies."""
    dependencies = [
        {
            "package_name": "package1",
            "dependencies": [
                {"package_name": "package2", "dependencies": []},
                {"package_name": "package3", "dependencies": []},
            ],
        }
    ]
    result = _collect_dependency_names(dependencies)
    assert result == ["package1", "package2", "package3"]


def test_collect_dependency_names_duplicate_dependencies():
    """Test collect_dependency_names with duplicate dependencies."""
    dependencies = [
        {
            "package_name": "package1",
            "dependencies": [
                {"package_name": "package2", "dependencies": []},
                {"package_name": "package2", "dependencies": []},
            ],
        }
    ]
    result = _collect_dependency_names(dependencies)
    assert result == ["package1", "package2"]


def test_find_package_node_no_package_provided():
    """Test find_package_node when no package is provided."""
    dep_tree = [{"key": "package1"}, {"key": "package2"}]
    result = _find_package_node(dep_tree, None)
    assert result == dep_tree


def test_find_package_node_single_package_found():
    """Test find_package_node when a single package is found."""
    dep_tree = [{"key": "package1"}, {"key": "package2"}]
    result = _find_package_node(dep_tree, ("package1",))
    assert result == [{"key": "package1"}]


def test_find_package_node_single_package_not_found():
    """Test find_package_node when a single package is not found."""
    dep_tree = [{"key": "package1"}, {"key": "package2"}]
    result = _find_package_node(dep_tree, ("package3",))
    assert result == []


def test_find_package_node_multiple_packages_found():
    """Test find_package_node when multiple packages are found."""
    dep_tree = [{"key": "package1"}, {"key": "package2"}, {"key": "package3"}]
    result = _find_package_node(dep_tree, ("package1", "package3"))
    assert result == [{"key": "package1"}, {"key": "package3"}]


def test_find_package_node_case_insensitive_match():
    """Test find_package_node with case-insensitive package matching."""
    dep_tree = [{"key": "Package1"}, {"key": "package2"}]
    result = _find_package_node(dep_tree, ("package1",))
    assert result == [{"key": "Package1"}]
