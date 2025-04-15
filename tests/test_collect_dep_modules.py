import json
from unittest import mock

import pytest

from python_build_utils.collect_dep_modules import collect_dependencies, get_dependency_tree


def test_get_dependency_tree_success():
    """Test get_dependency_tree when pipdeptree runs successfully."""
    mock_output = json.dumps([{"key": "package1", "dependencies": []}])
    with (
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
        pytest.raises(json.JSONDecodeError),
    ):
        get_dependency_tree()


def test_collect_dependencies_no_package(capfd):
    """Test collect_dependencies when no package is provided."""
    with mock.patch("click.echo") as mock_echo:
        collect_dependencies(package=None, output=None)
        mock_echo.assert_called_with("Please provide a package name using --package.")


def test_collect_dependencies_package_not_found(capfd):
    """Test collect_dependencies when the package is not found in the dependency tree."""
    with (
        mock.patch("python_build_utils.collect_dep_modules.get_dependency_tree", return_value=[]),
        mock.patch("click.echo") as mock_echo,
    ):
        collect_dependencies(package="nonexistent_package", output=None)
        mock_echo.assert_any_call("Collecting dependencies for 'nonexistent_package'...")
        mock_echo.assert_any_call("Package 'nonexistent_package' not found in the environment.")


def test_collect_dependencies_no_dependencies(capfd):
    """Test collect_dependencies when the package has no dependencies."""
    mock_dep_tree = [{"key": "test_package", "dependencies": []}]
    with (
        mock.patch("python_build_utils.collect_dep_modules.get_dependency_tree", return_value=mock_dep_tree),
        mock.patch("python_build_utils.collect_dep_modules.find_package_node", return_value=mock_dep_tree[0]),
        mock.patch("click.echo") as mock_echo,
    ):
        collect_dependencies(package="test_package", output=None)
        mock_echo.assert_any_call("Collecting dependencies for 'test_package'...")
        mock_echo.assert_any_call("Dependencies for test_package:")
        mock_echo.assert_any_call(" (No dependencies found)")


def test_collect_dependencies_with_dependencies(capfd):
    """Test collect_dependencies when the package has dependencies."""
    mock_dep_tree = [
        {
            "key": "test_package",
            "dependencies": [
                {"key": "dep1", "installed_version": "1.0", "dependencies": []},
                {"key": "dep2", "installed_version": "2.0", "dependencies": []},
            ],
        }
    ]
    with (
        mock.patch("python_build_utils.collect_dep_modules.get_dependency_tree", return_value=mock_dep_tree),
        mock.patch("python_build_utils.collect_dep_modules.find_package_node", return_value=mock_dep_tree[0]),
        mock.patch("python_build_utils.collect_dep_modules.print_deps") as mock_print_deps,
        mock.patch("click.echo") as mock_echo,
    ):
        collect_dependencies(package="test_package", output=None)
        mock_echo.assert_any_call("Collecting dependencies for 'test_package'...")
        mock_echo.assert_any_call("Dependencies for test_package:")
        mock_print_deps.assert_called_once_with(mock_dep_tree[0]["dependencies"])


def test_collect_dependencies_write_to_file(tmp_path):
    """Test collect_dependencies when writing dependencies to a file."""
    mock_dep_tree = [
        {
            "key": "test_package",
            "dependencies": [
                {"key": "dep1", "installed_version": "1.0", "dependencies": []},
                {"key": "dep2", "installed_version": "2.0", "dependencies": []},
            ],
        }
    ]
    output_file = tmp_path / "dependencies.txt"
    with (
        mock.patch("python_build_utils.collect_dep_modules.get_dependency_tree", return_value=mock_dep_tree),
        mock.patch("python_build_utils.collect_dep_modules.find_package_node", return_value=mock_dep_tree[0]),
        mock.patch("python_build_utils.collect_dep_modules.collect_dependency_names", return_value=["dep1", "dep2"]),
        mock.patch("click.echo") as mock_echo,
    ):
        collect_dependencies(package="test_package", output=str(output_file))
        assert output_file.read_text() == "dep1\ndep2"
        mock_echo.assert_any_call(f"Dependencies written s float list so {output_file}")
