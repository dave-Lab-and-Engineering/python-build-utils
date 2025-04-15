""" """

import click

from . import __version__
from .collect_pyd_modules import collect_all_pyd_modules, get_venv_site_packages


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

    click.echo(f"Collecting .pyd modules in '{venv_site_packages}'...")
    pyd_sub_modules = collect_all_pyd_modules(venv_site_packages=venv_site_packages, regex=regex)

    if not pyd_sub_modules:
        click.echo("No .pyd modules found.")
    else:
        click.echo("Found the following .pyd submodules:")
        click.echo("\n".join(f"- {module}" for module in pyd_sub_modules))
