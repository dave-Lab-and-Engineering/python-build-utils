"""
This script provides a command-line interface (CLI) tool to clean up `.pyd` and `.c` build modules
from a Python virtual environment. It allows filtering of files to be removed using an optional
regular expression.

Functions:
    clean_pyd_modules(venv_path: str | None, regex: str | None) -> None:
        CLI command to clean `.pyd` and `.c` files from a virtual environment.
        Accepts an optional virtual environment path and a regex filter for file names.
    clean_by_extensions(venv_site_packages: Path, regex: str | None, extension: str) -> None:
        Helper function to remove files with a specific extension from the virtual environment's
        site-packages directory. Supports filtering by regex.

CLI Options:
    --venv-path: Path to the virtual environment to scan for `.pyd` modules. Defaults to the
                 current environment if not specified.
    --regex, -r: Optional regular expression to filter `.pyd` modules by name.
    --version, -v: Displays the version of the tool and exits.
    - Scans the specified virtual environment's `site-packages` directory for `.pyd` and `.c` files.
    - Removes all matching files, optionally filtered by a regex pattern.
    - Provides feedback on the cleaning process, including errors encountered during file removal.

Dependencies:
    - `click`: For building the CLI interface.
    - `pathlib`: For filesystem path manipulations.
    - `re`: For regular expression matching.

Usage:
    Run the script as a CLI tool to clean up `.pyd` and `.c` files from a virtual environment.
    Example:
        python clean_pyd_modules.py --venv-path /path/to/venv --regex "pattern"
"""

import re
from pathlib import Path

import click

from . import __version__
from .collect_pyd_modules import get_venv_site_packages


@click.command(name="clean-pyd-modules", help="Clean all .pyd/.c build modules from a virtual environment.")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option(
    "--venv-path",
    default=None,
    help="Path to the virtual environment to scan for .pyd modules. Defaults to the current environment.",
)
@click.option(
    "--regex",
    "-r",
    default=None,
    help="Optional regular expression to filter .pyd modules by name.",
)
def clean_pyd_modules(venv_path: str | None = None, regex: str | None = None) -> None:
    """
    Clean all  *.pyd/.c files in a virtual environment. A regex filter can be applied.

    Args:
        venv_path (str | None): Path to the virtual environment. If None, the current environment is used.
        regex (str | None): Optional regex pattern to filter module names.

    Behavior:
        * Removes all .pyd submodules found under the specified virtual environment's site-packages.
        * Also, all .c files are removed.
    """
    venv_site_packages = get_venv_site_packages(venv_path)

    if not venv_site_packages:
        click.echo("Could not locate site-packages in the specified environment.")
        return

    for extension in ["*.pyd", "*.c"]:
        click.echo(f"Cleaning the {extension} files with '{regex}' filter in '{venv_site_packages}'...")
        clean_by_extensions(venv_site_packages=venv_site_packages, regex=regex, extension=extension)


def clean_by_extensions(venv_site_packages: Path, regex: str | None, extension: str) -> None:
    """
    Removes files with a specified extension from a virtual environment's site-packages directory,
    optionally filtering them by a regex pattern.
    Args:
        venv_site_packages (Path): The path to the virtual environment's site-packages directory.
        regex (str | None): A regular expression pattern to filter files by their relative paths.
                            If None, all files with the specified extension are considered.
        extension (str): The file extension to search for (e.g., '*.pyd').
    Returns:
        None: This function does not return a value.
    Side Effects:
        - Deletes matching files from the file system.
        - Outputs messages to the console using `click.echo`.
    Raises:
        Exception: If an error occurs while attempting to delete a file, an error message is displayed.
    Notes:
        - If no files with the specified extension are found, a message is displayed and the function exits.
        - If a regex filter is provided, only files matching the regex are removed.
    """

    file_candidates = list(venv_site_packages.rglob(extension))

    if not file_candidates:
        click.echo(f"No {extension} files found in {venv_site_packages}.")
        return None

    clean_any = False
    for file_to_clean in file_candidates:
        relative_path = file_to_clean.relative_to(venv_site_packages).as_posix()
        if regex is not None and not re.search(regex, relative_path, re.IGNORECASE):
            continue
        click.echo(f"Removing {file_to_clean}")
        try:
            file_to_clean.unlink()
        except Exception as e:
            click.echo(f"Error removing {file_to_clean}: {e}", err=True)
        else:
            clean_any = True
    if not clean_any:
        click.echo(f"No {extension} files with '{regex}' filter found in {venv_site_packages}.")
