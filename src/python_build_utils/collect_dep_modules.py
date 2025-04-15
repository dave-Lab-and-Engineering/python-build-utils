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

import click

from . import __version__


@click.command(name="collect-dep-modules")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option("--package", help="Name of the python package to collect all dependencies")
@click.option(
    "--output", "-o", type=click.Path(writable=True), help="Optional output file to write the dependencies list"
)
def collect_dependencies(package: str, output: str | None) -> None:
    """
    Collects and processes the dependencies of a specified package.
    Args:
        package (str): The name of the package for which dependencies are to be collected.
        output (str | None): The file path to write the dependencies to. If None, dependencies are not written to a file.
    Returns:
        None: This function does not return a value. It outputs information to the console and optionally writes to a file.
    Behavior:
        - If the `package` argument is not provided, the function prompts the user to specify a package.
        - Retrieves the dependency tree of the current environment and identifies the specified package.
        - If the package is not found, a message is displayed to the user.
        - Collects the names of all dependencies for the specified package.
        - Displays the dependencies in a tree format on the console.
        - If the `output` argument is provided, writes the list of dependencies to the specified file.
    """

    if not package:
        click.echo("Please provide a package name using --package.")
        return

    click.echo(f"Collecting dependencies for '{package}'...")

    dep_tree = get_dependency_tree()
    package_node = find_package_node(dep_tree, package)

    if not package_node:
        click.echo(f"Package '{package}' not found in the environment.")
        return

    dependencies = collect_dependency_names(package_node["dependencies"])

    click.echo(f"Dependencies for {package}:")
    if not dependencies:
        click.echo(" (No dependencies found)")
    else:
        # print dependencies in a tree format to screen
        print_deps(package_node["dependencies"])

        # write dependencies to file if output is provided
        if output:
            with open(output, "w") as f:
                f.write("\n".join(dependencies))
            click.echo(f"Dependencies written s float list so {output}")


def print_deps(deps: list, level=1):
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


def get_dependency_tree() -> list:
    """Run pipdeptree and return the dependency tree as JSON."""
    command = [sys.executable, "-m", "pipdeptree", "--json-tree"]

    stdout = run_safe_subprocess(command)
    return json.loads(stdout)


def find_package_node(dep_tree: list, package: str) -> dict | None:
    """Find the package node in the dependency tree."""
    return next((pkg for pkg in dep_tree if pkg["key"].lower() == package.lower()), None)


def collect_dependency_names(dependencies: list, collected=None) -> list:
    """Recursively collect dependency names."""
    if collected is None:
        collected = []

    for dep in dependencies:
        dep_name = dep["package_name"]
        if dep_name not in collected:
            collected.append(dep_name)
            collect_dependency_names(dep.get("dependencies", []), collected)

    return collected
