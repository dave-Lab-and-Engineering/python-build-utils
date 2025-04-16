"""
This module provides a command-line interface (CLI) for Python build utilities.
It uses the `click` library to create a CLI group and add commands for renaming
wheel files and removing tarballs.

Functions:
    cli(): Defines the CLI group and adds commands for renaming wheel files and
           removing tarballs.
Commands:
    rename_wheel_files: Command to rename wheel files.
    remove_tarballs: Command to remove tarballs.
"""

import logging

import click

from . import __version__
from .clean_pyd_modules import clean_pyd_modules
from .cli_logger import initialize_logging
from .collect_dep_modules import collect_dependencies
from .collect_pyd_modules import collect_pyd_modules
from .pyd2wheel import pyd2wheel
from .remove_tarballs import remove_tarballs
from .rename_wheel_files import rename_wheel_files

logger = initialize_logging()


@click.group()
@click.version_option(__version__, "--version", message="Version: %(version)s", help="Show the version and exit.")
@click.option("-v", "--verbose", count=True, help="Increase verbosity level. Use -v for info, -vv for debug.")
def cli(verbose: int) -> None:
    """A collection of CLI tools for Python build utilities."""

    if verbose >= 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logger.setLevel(log_level)
    for handler in logger.handlers:
        handler.setLevel(log_level)

    if log_level <= logging.INFO:
        logger.info("🚀 Python Build Utilities CLI — ready to build, package, and manage your Python projects.")


cli.add_command(pyd2wheel)
cli.add_command(collect_pyd_modules)
cli.add_command(clean_pyd_modules)
cli.add_command(collect_dependencies)
cli.add_command(rename_wheel_files)
cli.add_command(remove_tarballs)


if __name__ == "__main__":
    cli()
