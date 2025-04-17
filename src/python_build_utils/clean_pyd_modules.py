"""
This script provides a command-line interface (CLI) tool to clean up `.pyd` and `.c` build modules
from a Python src directory. It allows filtering of files to be removed using an optional
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

import logging
import re
from pathlib import Path

import click

logger = logging.getLogger(__name__)


@click.command(name="clean-pyd-modules", help="Clean all .pyd/.c build modules in src path.")
@click.option(
    "--src-path",
    default="src",
    help="Path to the src folder to scan for .pyd modules. Defaults to 'src' in the current folder.",
)
@click.option(
    "--regex",
    "-r",
    default=None,
    help="Optional regular expression to filter .pyd modules by name.",
)
@click.pass_context
def clean_pyd_modules(ctx: click.Context, src_path: str | None = None, regex: str | None = None) -> None:
    """
    Clean all  *.pyd/.c files in a virtual environment. A regex filter can be applied.

    Args:
        venv_path (str | None): Path to the virtual environment. If None, the current environment is used.
        regex (str | None): Optional regex pattern to filter module names.

    Behavior:
        * Removes all .pyd submodules found under the specified virtual environment's site-packages.
        * Also, all .c files are removed.
    """
    src_path_to_search = _get_src_path(src_path)

    if src_path_to_search is None:
        logger.error(f"Could not locate src path: {src_path_to_search}.")
    else:
        for extension in ["*.pyd", "*.c"]:
            logger.info(f"Cleaning the {extension} files with '{regex}' filter in '{src_path}'...")
            clean_by_extensions(src_path=src_path_to_search, regex=regex, extension=extension)


def _get_src_path(src_path: str | None = None) -> Path | None:
    """
    Get the site-packages directory for the given virtual environment path or the current environment.

    Args:
        venv_path (str | None): Path to the virtual environment. If None, uses the current environment.

    Returns:
        Path | None: The path to the site-packages directory, or None if not found.
    """
    if src_path is not None:
        src = Path(src_path).resolve()
        if not src.exists() or not src.is_dir():
            logger.error(f"Path '{src}' does not exist or is not a directory.")
            return None
        return src
    else:
        # Get the site-packages directory from the current virtual environment
        return Path(".").resolve() / "src"


def clean_by_extensions(src_path: Path, regex: str | None, extension: str) -> None:
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
    Raises:
        Exception: If an error occurs while attempting to delete a file, an error message is displayed.
    Notes:
        - If no files with the specified extension are found, a message is displayed and the function exits.
        - If a regex filter is provided, only files matching the regex are removed.
    """

    file_candidates = list(src_path.rglob(extension))

    if not file_candidates:
        logger.info(f"No {extension} files found in {src_path}.")
        return None

    clean_any = False
    for file_to_clean in file_candidates:
        relative_path = file_to_clean.relative_to(src_path).as_posix()
        if regex is not None and not re.search(regex, relative_path, re.IGNORECASE):
            continue
        logger.info(f"Removing {file_to_clean}")
        try:
            file_to_clean.unlink()
        except Exception as e:
            logger.warning(f"Error removing {file_to_clean}: {e}")
        else:
            clean_any = True
    if not clean_any:
        logger.info(f"No {extension} files with '{regex}' filter found in {src_path}.")
