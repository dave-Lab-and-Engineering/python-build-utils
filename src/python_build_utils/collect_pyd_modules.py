import logging
import os
import re
import sys
from pathlib import Path

import click

logger = logging.getLogger(__name__)


@click.command(name="collect-pyd-modules", help="Collect and display .pyd submodules from a virtual environment.")
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
@click.option(
    "--collect-py",
    is_flag=True,
    default=False,
    help="If set, collect .py files instead of .pyd files.",
)
@click.option(
    "--output", "-o", type=click.Path(writable=True), help="Optional file path to write the list of found .pyd modules."
)
@click.pass_context
def collect_pyd_modules(
    ctx: click.Context,
    venv_path: str | None = None,
    regex: str | None = None,
    collect_py: bool = False,
    output: str | None = None,
) -> None:
    """
    Collects a list of `.pyd` or `.py` submodules found in a virtual environment.

    Args:
        venv_path (str | None): Path to the virtual environment. If None, the current environment is used.
        regex (str | None): Optional regex pattern to filter module names.
        collect_py (bool): If True, collect .py instead of .pyd files.
        output (str | None): File path to write the list of .pyd submodules. If None, output is printed only.

    Behavior:
        * Lists all .pyd submodules found under the specified virtual environment's site-packages.
        * Applies regex filtering if provided.
        * Prints results to the console.
        * Optionally writes the list to the specified output file.
    """
    # Get the site-packages directory of the virtual environment
    venv_site_packages = _get_venv_site_packages(venv_path)

    if not venv_site_packages:
        logger.error("Could not locate site-packages in the specified environment.")
        return

    logger.info(f"Collecting .pyd modules in '{venv_site_packages}'...")

    # Collect the modules
    pyd_sub_modules = _find_modules_in_site_packages(
        venv_site_packages=venv_site_packages, regex=regex, collect_py=collect_py
    )

    # If no modules were found, log that and return
    if not pyd_sub_modules:
        logger.info("No .pyd modules found.")
        return []

    # Output the list to stdout
    logger.info("Found the following .pyd submodules:")
    click.echo("\n".join(f"{module}" for module in pyd_sub_modules))

    # If output file is specified, write the list to that file
    if output:
        with open(output, "w") as f:
            f.write("\n".join(pyd_sub_modules))
        click.echo(f"Module list written to {output}")

    return pyd_sub_modules  # Return the list of found modules for use in other contexts


def collect_pyd_modules_from_venv(venv_path: str | None = None, regex: str | None = None) -> list:
    """
    Public API to collect a list of `.pyd` submodules found in a virtual environment.

    Args:
        venv_path (str | None): Path to the virtual environment. If None, the current environment is used.
        regex (str | None): Optional regex pattern to filter module names.

    Returns:
        list: List of found .pyd module names.
    """
    venv_site_packages = _get_venv_site_packages(venv_path)
    if not venv_site_packages:
        msg = f"Could not locate site-packages in the specified environment: {venv_path}."
        logger.error(msg)
        raise ValueError(msg)

    return _find_modules_in_site_packages(venv_site_packages=venv_site_packages, regex=regex)


def _get_venv_site_packages(venv_path: str | None = None) -> Path | None:
    """
    Get the site-packages directory for the given virtual environment path or the current environment.

    Args:
        venv_path (str | None): Path to the virtual environment. If None, uses the current environment.

    Returns:
        Path | None: The path to the site-packages directory, or None if not found.
    """
    if venv_path is not None:
        venv = Path(venv_path).resolve()
        if not venv.exists() or not venv.is_dir():
            click.echo(f"Path '{venv}' does not exist or is not a directory.")
            return None
        return venv / "Lib" / "site-packages"
    else:
        # Get the site-packages directory from the current virtual environment
        return next((Path(p) for p in sys.path if "site-packages" in p), None)


def _find_modules_in_site_packages(
    venv_site_packages: Path, regex: str | None = None, collect_py: bool = False
) -> list:
    """
    Collects all `.pyd` modules from the specified virtual environment's site-packages directory.
    This function searches recursively for `.pyd` files within the given `venv_site_packages` directory,
    extracts their corresponding module names, and optionally filters them using a regular expression.

    Args:
        venv_site_packages (Path): The path to the virtual environment's site-packages directory.
        regex (str | None, optional): A regular expression to filter the module names. If `None`, no filtering is applied.
        collect_py (bool): If True, collect .py instead of .pyd files.

    Returns:
        list: A list of unique module names corresponding to the `.pyd` files found.
    """

    extension = ".py" if collect_py else ".pyd"

    pyd_files = list(venv_site_packages.rglob(f"*{extension}"))

    submodules = []
    for file in pyd_files:
        module_name = _extract_submodule_name(module_file=file, venv_site_packages=venv_site_packages)

        if regex is not None and not re.search(regex, module_name, re.IGNORECASE):
            continue

        # Remove the .__init__ part of the module name if it exists
        module_name = re.sub(r"\.__init__", "", module_name)

        if module_name not in submodules:
            submodules.append(module_name)

    return submodules


def _extract_submodule_name(module_file: Path, venv_site_packages: Path) -> str:
    """
    Extract the submodule name from a .pyd/.py file path by removing the platform-specific suffix
    and the path leading to the module.

    Args:
        module_file (Path): The full path to the .pyd file.
        venv_site_packages (Path): The site-packages directory of the virtual environment.

    Returns:
        str: The submodule name in the format 'module.submodule'.
    """
    # Get the relative path from the site-packages directory
    relative_path = module_file.relative_to(venv_site_packages)

    # Remove the platform-specific suffix (e.g., cp312-win_amd64.pyd)
    module_name = re.sub(r"\.cp\d+.*\.(pyd|py)$", "", str(relative_path))

    # Remove the suffix .pyd if it exists
    module_name = re.sub(r".(pyd|py)$", "", str(module_name))

    # Convert the path to a dotted module name
    return module_name.replace(os.sep, ".")
