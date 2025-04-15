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

import sys

import click

from . import __version__


@click.command(name="collect-pyd-modules")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option(
    "--venv_path",
    default=None,
    help="Path to the virtual environment where you want to collect all pyd modules. Default is the current environment.",
)
@click.option(
    "--regex", default=None, help="regular expression to filter on modules for which you want to collect pyd files."
)
@click.option(
    "--output", "-o", type=click.Path(writable=True), help="Optional output file to write the dependencies list"
)
def collect_pyd_submodules(output: str | None, regex: str | None = None, venv_path: str | None = None) -> None:
    """Collect all the dependencies of a given package using pipdeptree."""

    search_paths = [venv_path] if venv_path is not None else sys.path

    # get the site-packages directory from the venv in the paths
    venv_site_packages = next((p for p in search_paths if "site-packages" in p), None)

    if not venv_site_packages:
        click.echo("Could not locate site-packages in the current environment.")
        return []

    click.echo(f"Collecting pyd in '{venv_site_packages}'")
