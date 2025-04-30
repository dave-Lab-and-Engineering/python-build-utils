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
import logging
import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution
from typing import Any

import click

logger = logging.getLogger(__name__)


@click.command(name="collect-dependencies", help="Collect and display dependencies for one or more Python packages.")
@click.option(
    "--package",
    "-p",
    multiple=True,
    help=(
        "Name of the Python package to collect dependencies for. "
        "Can be given multiple times. If omitted, dependencies for the entire environment are collected."
    ),
)
@click.option(
    "--regex",
    "-r",
    default=None,
    help="Optional regular expression to filter modules by name.",
)
@click.option(
    "--output", "-o", type=click.Path(writable=True), help="Optional file path to write the list of dependencies to."
)
@click.pass_context
def collect_dependencies(
    ctx: click.Context, package: tuple[str] | None, output: str | None, regex: str | None = None
) -> list | None:
    """
    CLI command to collect dependencies for specified packages or the entire environment.

    Args:
        package (tuple[str]): Names of packages to collect dependencies for. If empty, collects for all installed packages.
        output (str | None): Optional path to write the dependency list.
        regex (str | None): Optional regex pattern to filter module names.

    Returns:
        list | None: A list of dependencies for the specified package(s).

    Behavior:
        * If no package is provided, collects dependencies for all packages in the environment.
        * If a package is not found, notifies the user.
        * Displays dependencies in a tree format on the console.
        * Writes a plain list of dependencies to the given file if --output is provided.
    """

    logger.info("Python Build Utilities — Dependency Collector starting up.")

    deps = collect_package_dependencies(package, regex)

    if not deps:
        logger.info("No dependencies found.")
    else:
        if output:
            with open(output, "w") as f:
                f.write("\n".join(deps))
            logger.info(f"Dependencies written as plain list to {output}")
        else:
            for dep in deps:
                click.echo(dep)

    return deps


def collect_package_dependencies(package: str | tuple[str] | None, regex: str | None = None) -> list[str]:
    """
    Collects the dependencies of a given package or packages in the current environment.

    Args:
        package (str | tuple[str] | None): The name of a single package as a string,
            a tuple of package names, or None. If None, the dependencies for all packages in the environment
            are collected.
        regex (str| None): Optional regular expression to filter modules by name.
    Returns:
        list[str]: A list of dependency names for the specified package(s).
            Returns an empty list if the package(s) are not found in the environment.
    Logs:
        - A warning if the specified package(s) are not found in the environment.
        - A debug message with a representation of the dependency tree for the package(s).
    Notes:
        - The function relies on helper functions `_get_dependency_tree`,
          `_find_package_node`, `_collect_dependency_names`, and `_get_deps_tree`
          to retrieve and process the dependency information.
    """

    # Normalize the package argument
    if not package or package == "":
        package_tuple: tuple[str] | None = None
    elif isinstance(package, str):
        package_tuple = (package,)
    else:
        package_tuple = package

    dep_tree = _get_dependency_tree()
    package_nodes = _find_package_node(dep_tree, package_tuple)
    if not package_nodes:
        logger.warning(f"Package(s) {package} not found in the environment.")
        return []

    all_dependencies = []
    package_tree = ""
    for package_node in package_nodes:
        package_dependencies = package_node.get("dependencies", [])
        dependencies = _collect_dependency_names(package_dependencies)
        all_dependencies.extend(dependencies)
        package_tree = _get_deps_tree(package_dependencies, deps_tree=package_tree)

    if regex:
        pattern = re.compile(regex, re.IGNORECASE)
        all_dependencies = [p for p in all_dependencies if pattern.search(p)]

    logger.debug("Representation of the dependencies:")
    logger.debug(package_tree)

    return all_dependencies


def _get_import_names(dist_name: str) -> list[str]:
    """
    Gets the top-level import names for a given distribution name.
    Falls back to the distribution name itself if not available.
    """
    try:
        dist = distribution(dist_name)
        top_level_text = dist.read_text("top_level.txt")
        if top_level_text:
            return [line.strip() for line in top_level_text.splitlines() if line.strip()]
    except (PackageNotFoundError, FileNotFoundError):
        pass
    return [dist_name]


def _get_deps_tree(deps: list[dict], level: int = 1, deps_tree: str = "") -> str:
    """
    Recursively prints a list of dependencies in a hierarchical format.

    Args:
        deps (list): A list of dictionaries representing dependencies. Each dictionary
                     should contain the keys "key" (dependency name) and "installed_version"
                     (version of the dependency). Optionally, it can include a "dependencies"
                     key with a nested list of dependencies.
        level (int, optional): The current indentation level for printing. Defaults to 1.
        deps_tree (str, optional): A string to accumulate the formatted dependencies. Defaults to an empty string.

    Returns:
        str: A string representation of the dependencies in a hierarchical format.
    """

    for dep in deps:
        dep_name = dep["key"]
        dep_version = dep["installed_version"]
        deps_tree += "  " * level + f"- {dep_name} ({dep_version})\n"
        deps_tree = _get_deps_tree(dep.get("dependencies", []), level + 1, deps_tree=deps_tree)

    return deps_tree


def _run_safe_subprocess(command: list[str]) -> str:
    """Runs a subprocess safely and returns the output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)  # nosec B603
    except subprocess.CalledProcessError as e:
        logger.warning("Subprocess failed.")
        logger.warning(e)
        sys.exit(1)
    else:
        return result.stdout  # return moved to else block


def _get_dependency_tree() -> Any:
    """Run pipdeptree and return the dependency tree as JSON."""
    # pipdeptree is only required for this tool
    try:
        import pipdeptree
    except ModuleNotFoundError:
        logger.exception(
            "pipdeptree is not installed. Please install it to use this tool. Do:\n"
            ""
            "   pip install pipdeptree\n"
            ""
            "or\n"
            ""
            "   pip install python-build-utils[all]\n"
        )
        sys.exit(1)
    else:
        logger.debug(f"Imported {pipdeptree.__name__}")

    command = [sys.executable, "-m", "pipdeptree", "--json-tree"]

    stdout = _run_safe_subprocess(command)
    return json.loads(stdout)


def _find_package_node(dep_tree: list, package: tuple[str] | None) -> list | None:
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


def _collect_dependency_names(dependencies: list, collected: list | None = None) -> list:
    """Recursively collect import names using top_level.txt from metadata."""
    if collected is None:
        collected = []

    for dep in dependencies:
        dist_name = dep["package_name"]
        import_names = _get_import_names(dist_name)

        for name in import_names:
            if name not in collected:
                collected.append(name)

        _collect_dependency_names(dep.get("dependencies", []), collected)

    return collected
