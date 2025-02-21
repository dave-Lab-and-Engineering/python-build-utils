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

import click

from . import __version__
from .pyd2wheel import pyd2wheel
from .remove_tarballs import remove_tarballs
from .rename_wheel_files import rename_wheel_files


@click.group()
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
def cli() -> None:
    """A collection of CLI tools for Python build utilities."""


cli.add_command(rename_wheel_files)
cli.add_command(remove_tarballs)
cli.add_command(pyd2wheel)

if __name__ == "__main__":
    cli()
