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

from python_build_utils import __version__
from python_build_utils.collect_dep_modules import collect_dependencies
from python_build_utils.collect_pyd_modules import collect_pyd_submodules
from python_build_utils.remove_tarballs import remove_tarballs
from python_build_utils.rename_wheel_files import rename_wheel_files


@click.group()
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
def cli() -> None:
    """A collection of CLI tools for Python build utilities."""


cli.add_command(collect_pyd_submodules)
cli.add_command(collect_dependencies)
cli.add_command(rename_wheel_files)
cli.add_command(remove_tarballs)

if __name__ == "__main__":
    cli()
