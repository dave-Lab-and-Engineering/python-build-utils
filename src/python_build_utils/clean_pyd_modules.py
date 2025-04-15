""" """

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
    Collects a list of `.pyd` submodules found in a virtual environment.

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
