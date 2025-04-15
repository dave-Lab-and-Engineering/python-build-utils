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
import os
import re
import subprocess
import sys
from pathlib import Path

import click

from . import __version__


@click.command(name="collect-dep-modules")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option("--package", help="Name of the python package to collect all dependencies")
@click.option(
    "--output", "-o", type=click.Path(writable=True), help="Optional output file to write the dependencies list"
)
def collect_dependencies(
    package: str, output: str | None, regex: str | None = None, venv_path: str | None = None
) -> None:
    """Collect all the dependencies of a given package using pipdeptree."""
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

        # submodules = collect_cythonized_submodules(dependencies, regex=regex, venv_path=venv_path)

        # write dependencies to file if output is provided
        if output:
            with open(output, "w") as f:
                f.write("\n".join(dependencies))
            click.echo(f"Dependencies written s float list so {output}")


def collect_cythonized_submodules(deps: list, regex: str | None = None, venv_path: str | None = None) -> list:
    """Collect submodules from the dependencies list."""
    submodules = []
    for dep in deps:
        collect_submodels = False
        if regex is not None:
            match = re.search(dep, regex)
            if match:
                collect_submodels = True
        else:
            collect_submodels = True

        if collect_submodels:
            all_submodules = collect_pyd_modules(dep, venv_path=venv_path)
            if all_submodules:
                submodules.extend(all_submodules)
            else:
                click.echo(f"No submodules found for {dep}.")

    return submodules


def collect_pyd_modules(dep: str, venv_path=None) -> list:
    """Collect all .pyd submodules for a given dependency in the current virtual environment."""

    paths = [venv_path] if venv_path is not None else sys.path

    venv_site_packages = next((p for p in paths if "site-packages" in p), None)

    if not venv_site_packages:
        click.echo("Could not locate site-packages in the current environment.")
        return []

    dep_path = Path(venv_site_packages) / dep
    if not dep_path.exists():
        click.echo(f"No installed directory found for dependency '{dep}' in site-packages.")
        return []

    pyd_files = list(dep_path.rglob("*.pyd"))

    submodules = []
    for file in pyd_files:
        relative_path = file.relative_to(venv_site_packages)
        module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")
        submodules.append(module_name)

    return submodules


def print_deps(deps: list, level=1):
    """Recursively print dependencies in a tree format."""
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
