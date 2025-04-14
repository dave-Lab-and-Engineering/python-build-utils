"""Collect all the dependencies for a given package ."""

import click

from . import __version__


@click.command(name="collect-dep-modules")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option("--package", help="Name of the python package to collect all dependencies")
def collect_dependencies(package: str) -> None:
    """Collect all the dependencies.

    Args:

        package (str): Name of the package to collect all dependencies.

    Returns:
        None

    Example:
        rename_wheel_files("dist", "cp39", "win_amd64", "")
    """

    click.echo(f"Collecting {package} dependencies...")
