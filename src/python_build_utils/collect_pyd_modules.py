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

import os
import re
import sys
from pathlib import Path

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

    venv_site_packages = get_venv_site_packages(venv_path)

    if not venv_site_packages:
        click.echo("Could not locate site-packages in the current environment.")
        return []

    click.echo(f"Collecting pyd in '{venv_site_packages}'")
    pyd_sub_modules = collect_all_pyd_modules(venv_site_packages=venv_site_packages, regex=regex)

    if not pyd_sub_modules:
        click.echo(" (No dependencies found)")
    else:
        # Print the list of pyd_sub_modules to the screen
        click.echo("Found the following .pyd submodules:")
        click.echo("\n".join(f"- {module}" for module in pyd_sub_modules))

        # Write dependencies to file if output is provided
        if output:
            with open(output, "w") as f:
                f.write("\n".join(pyd_sub_modules))
            click.echo(f"Dependencies written to {output}")


def get_venv_site_packages(venv_path: str | None = None) -> Path | None:
    """
    Get the site-packages directory for the given virtual environment path or the current environment.

    Args:
        venv_path (str | None): Path to the virtual environment. If None, uses the current environment.

    Returns:
        Path | None: The path to the site-packages directory, or None if not found.
    """
    if venv_path is not None:
        venv_path = Path(venv_path).resolve()
        if not venv_path.exists() or not venv_path.is_dir():
            click.echo(f"Path '{venv_path}' does not exist or is not a directory.")
            return None
        return venv_path / "Lib" / "site-packages"
    else:
        # Get the site-packages directory from the current virtual environment
        return next((Path(p) for p in sys.path if "site-packages" in p), None)


def collect_all_pyd_modules(venv_site_packages, regex: str | None = None) -> list:
    """Collect all .pyd submodules for a given dependency in the current virtual environment."""

    pyd_files = list(venv_site_packages.rglob("*.pyd"))

    submodules = []
    for file in pyd_files:
        module_name = extract_submodule_name(pyd_file=file, venv_site_packages=venv_site_packages)

        if regex is not None and not re.search(regex, module_name, re.IGNORECASE):
            continue

        # remove the .__init__ part of the module name if it exists
        module_name = re.sub(r"\.__init__", "", module_name)

        if module_name not in submodules:
            submodules.append(module_name)

    return submodules


def extract_submodule_name(pyd_file: Path, venv_site_packages: Path) -> str:
    """
    Extract the submodule name from a .pyd file path by removing the platform-specific suffix
    and the path leading to the module.

    Args:
        pyd_file (Path): The full path to the .pyd file.
        venv_site_packages (Path): The site-packages directory of the virtual environment.

    Returns:
        str: The submodule name in the format 'module.submodule'.
    """
    # Get the relative path from the site-packages directory
    relative_path = pyd_file.relative_to(venv_site_packages)

    # Remove the platform-specific suffix (e.g., cp312-win_amd64.pyd)
    module_name = re.sub(r"\.cp\d+.*\.pyd$", "", str(relative_path))

    # Convert the path to a dotted module name
    return module_name.replace(os.sep, ".")
