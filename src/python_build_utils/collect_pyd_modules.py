"""
This module provides functionality to collect `.pyd` submodules from a specified Python virtual environment.
It includes a CLI command to filter and optionally write the list of `.pyd` submodules to a file.
Functions:
    collect_pyd_submodules(output: str | None, regex: str | None = None, venv_path: str | None = None) -> None:
        CLI command to collect `.pyd` submodules from a virtual environment, filter them using a regex,
        and optionally write the results to a file.
    get_venv_site_packages(venv_path: str | None = None) -> Path | None:
        Determines the `site-packages` directory for a given virtual environment or the current environment.
    collect_all_pyd_modules(venv_site_packages, regex: str | None = None) -> list:
        Collects all `.pyd` submodules from the specified `site-packages` directory, optionally filtering them
        using a regular expression.
    extract_submodule_name(pyd_file: Path, venv_site_packages: Path) -> str:
        Extracts the submodule name from a `.pyd` file path by removing platform-specific suffixes and converting
        the path to a dotted module name.
CLI Command:
    collect-pyd-modules:
        - Collects `.pyd` submodules from a virtual environment.
        - Filters the submodules using an optional regular expression.
        - Prints the results to the console and optionally writes them to a file.
Dependencies:
    - click: Used for creating the CLI command.
    - pathlib.Path: Used for handling file paths.
    - re: Used for regular expression matching.
    - sys: Used for accessing the Python environment's `sys.path`.
    - os: Used for path manipulation.
    - The `get_venv_site_packages` function is used to locate the `site-packages` directory of the virtual environment.
    - The `collect_all_pyd_modules` function recursively searches for `.pyd` files in the `site-packages` directory.
    - The `extract_submodule_name` function ensures that the module names are in a consistent dotted format.

"""

import os
import re
import sys
from pathlib import Path

import click

from . import __version__


@click.command(
    name="collect-pyd-modules",
)
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
def collect_pyd_submodules(venv_path: str | None = None, regex: str | None = None, output: str | None = None) -> None:
    """
    Collects  a list of `.pyd` submodules found in the venv

    Collects and optionally writes a list of `.pyd` submodules found in the specified virtual environment.

    Args:
        output (str | None): The file path where the list of `.pyd` submodules will be written.
                             If None, the list will not be written to a file.
        regex (str | None): An optional regular expression to filter the `.pyd` submodules.
        venv_path (str | None): The path to the virtual environment. If None, the current environment is used.
    Returns:
        None: This function does not return a value. It prints the results to the console and optionally writes them to a file.
    Side Effects:
        - Prints messages to the console about the progress and results of the operation.
        - Writes the list of `.pyd` submodules to the specified output file if `output` is provided.
    Notes:
        - The function uses `get_venv_site_packages` to locate the `site-packages` directory of the virtual environment.
        - If no `.pyd` submodules are found, a message is printed to the console.
    """

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
    """
    Collects all `.pyd` modules from the specified virtual environment's site-packages directory.
    This function searches recursively for `.pyd` files within the given `venv_site_packages` directory,
    extracts their corresponding module names, and optionally filters them using a regular expression.
    Args:
        venv_site_packages (Path): The path to the virtual environment's site-packages directory.
        regex (str | None, optional): A regular expression to filter the module names. If `None`, no filtering is applied.
    Returns:
        list: A list of unique module names corresponding to the `.pyd` files found.
    """

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

    # Remove the suffix .pyd if it exists
    module_name = re.sub(r".pyd$", "", str(module_name))

    # Convert the path to a dotted module name
    return module_name.replace(os.sep, ".")
