"""
This module provides a CLI tool to collect all dependencies of a given Python package
using `pipdeptree`. The dependencies can be displayed in the console or written to an
output file.
Functions:
    collect_dependencies(package: str, output: str | None) -> None:
        CLI command to collect and display/write dependencies of a specified package.
    run_safe_subprocess(command: list) -> str:
        Runs a subprocess safely and returns the output. Handles errors gracefully.
    get_dependency_tree() -> list:
        Executes `pipdeptree` to retrieve the dependency tree in JSON format.
    find_package_node(dep_tree: list, package: str) -> dict | None:
        Searches for a specific package node in the dependency tree.
    collect_dependency_names(dependencies: list, collected=None) -> list:
        Recursively collects the names of all dependencies from a given dependency list.
"""

import json
import subprocess
import sys
from typing import Any

import click

from . import __version__


@click.command(name="collect-package-dependencies")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option(
    "--package",
    multiple=True,
    help="Name of the python package to collect all dependencies. "
    "Can be given multiple times. If not provided, all dependencies of the current venv will be collected.",
)
@click.option(
    "--output", "-o", type=click.Path(writable=True), help="Optional output file to write the dependencies list"
)
def collect_dependencies(package: tuple[str] | None, output: str | None) -> None:
    """
    Collects and processes the dependencies of a specified package.

    Args:
        package (tuple[str]): A tuple of package names for which dependencies are to be collected.
                              If empty, dependencies for all packages in the current environment are collected.
        output (str | None): The file path to write the dependencies to. If None, dependencies are not written to a file.
    Returns:
        None: This function does not return a value. It outputs information to the console and optionally writes to a file.
    Behavior:
        - If the `package` argument is not provided, all the package of the current environment are collected.
        - If the `package` argument is provided, it collects dependencies for the specified package(s).
        - Retrieves the dependency tree of the current environment and identifies the specified package.
        - If the package is not found, a message is displayed to the user.
        - Collects the names of all dependencies for the specified package.
        - Displays the dependencies in a tree format on the console.
        - If the `output` argument is provided, writes the list of dependencies to the specified file.
    """

    dep_tree = get_dependency_tree()
    package_nodes = find_package_node(dep_tree, package)

    if not package_nodes:
        click.echo(f"Package '{package}' not found in the environment.")
        return

    all_dependencies = []
    for package_node in package_nodes:
        package_dependencies = package_node.get("dependencies", [])
        dependencies = collect_dependency_names(package_dependencies)
        all_dependencies.extend(dependencies)
        # print dependencies in a tree format to screen
        print_deps(package_dependencies)

    if not all_dependencies:
        click.echo("No dependencies found")
    else:
        # write dependencies to file if output is provided
        if output:
            with open(output, "w") as f:
                f.write("\n".join(all_dependencies))
            click.echo(f"Dependencies written as plain list to  {output}")


def print_deps(deps: list, level: int = 1) -> None:
    """
    Recursively prints a list of dependencies in a hierarchical format.

    Args:
        deps (list): A list of dictionaries representing dependencies. Each dictionary
                     should contain the keys "key" (dependency name) and "installed_version"
                     (version of the dependency). Optionally, it can include a "dependencies"
                     key with a nested list of dependencies.
        level (int, optional): The current indentation level for printing. Defaults to 1.

    Returns:
        None
    """

    for dep in deps:
        dep_name = dep["key"]
        dep_version = dep["installed_version"]
        click.echo("  " * level + f"- {dep_name} ({dep_version})")
        print_deps(dep.get("dependencies", []), level + 1)


def run_safe_subprocess(command: list) -> str:
    """Runs a subprocess safely and returns the output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)  # nosec B603
    except subprocess.CalledProcessError as e:
        click.echo("Subprocess failed.")
        click.echo(e)
        sys.exit(1)
    else:
        return result.stdout  # return moved to else block


def get_dependency_tree() -> Any:
    """Run pipdeptree and return the dependency tree as JSON."""
    command = [sys.executable, "-m", "pipdeptree", "--json-tree"]

    stdout = run_safe_subprocess(command)
    return json.loads(stdout)


def find_package_node(dep_tree: list, package: tuple[str] | None) -> list | None:
    """Find the package node in the dependency tree."""
    package_nodes = []
    if not package:
        package_nodes = dep_tree
    else:
        if isinstance(package, str):
            package = [package]

        for package_name in package:
            for pkg in dep_tree:
                if pkg["key"].lower() == package_name.lower():
                    package_nodes.append(pkg)

    return package_nodes


def collect_dependency_names(dependencies: list, collected: list | None = None) -> list:
    """Recursively collect dependency names."""
    if collected is None:
        collected = []

    for dep in dependencies:
        dep_name = dep["package_name"]
        if dep_name not in collected:
            collected.append(dep_name)
            collect_dependency_names(dep.get("dependencies", []), collected)

    return collected
