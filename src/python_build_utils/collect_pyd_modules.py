"""Collect compiled (.pyd/.so) or source (.py) submodules from a virtual environment."""

import logging
import os
import re
import sys
from pathlib import Path

import click

from .constants import PYD_EXTENSION, SO_EXTENSION


logger = logging.getLogger(__name__)


@click.command(
    name="collect-pyd-modules",
    help=(
        "Collect and display compiled (.pyd/.so) or source (.py) submodules from a virtual environment.\n\n"
        "By default this collects only .pyd files (backwards-compatible). Use --ext to choose others."
    ),
)
@click.option(
    "--venv-path",
    default=None,
    help="Path to the virtual environment to scan for modules. Defaults to the current environment.",
)
@click.option(
    "--regex",
    "-r",
    default=None,
    help="Optional regular expression to filter module names.",
)
@click.option(
    "--collect-py",
    is_flag=True,
    default=False,
    help="Deprecated: collect .py files instead of compiled. (Equivalent to --ext=py)",
)
@click.option(
    "--ext",
    type=click.Choice(["pyd", "so", "py", "compiled", "all"], case_sensitive=False),
    default="pyd",
    show_default=True,
    help=(
        "Which file types to collect: "
        "pyd (.pyd), so (.so), py (.py), compiled (.pyd + .so), or all (compiled + .py)."
    ),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    help="Optional file path to write the list of found modules.",
)
def collect_pyd_modules(
    venv_path: str | None = None,
    regex: str | None = None,
    *,
    collect_py: bool = False,
    ext: str = "pyd",
    output: str | None = None,
) -> list[str] | None:
    """Collect and optionally write module names from site-packages."""
    # Back-compat: --collect-py overrides --ext
    if collect_py:
        ext = "py"

    venv_site_packages = _get_venv_site_packages(venv_path)

    if venv_site_packages is None:
        logger.error("Could not locate site-packages in the specified environment.")
        return None

    targets = _extensions_from_choice(ext)

    human_label = ", ".join(sorted(targets))
    logger.info("Collecting modules (%s) in '%s'...", human_label, venv_site_packages)

    found_modules = _find_modules_in_site_packages(
        venv_site_packages=venv_site_packages,
        regex=regex,
        extensions=targets,
    )

    if not found_modules:
        logger.info("No matching modules found.")
        return None

    click.echo("\n".join(found_modules))
    logger.info("Found %d modules.", len(found_modules))

    if output:
        output_path = Path(output)
        with output_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(found_modules))
        click.echo(f"Module list written to {output_path}")

    return found_modules


def collect_pyd_modules_from_venv(
    venv_path: str | None = None,
    regex: str | None = None,
    *,
    collect_py: bool = False,
    ext: str = "pyd",
) -> list[str]:
    """Collect submodules from the given venv; usable from Python code/tests."""
    if collect_py:
        ext = "py"

    venv_site_packages = _get_venv_site_packages(venv_path)
    if venv_site_packages is None:
        msg = f"Could not locate site-packages in the specified environment: {venv_path}"
        logger.error(msg)
        raise ValueError(msg)

    targets = _extensions_from_choice(ext)
    return _find_modules_in_site_packages(
        venv_site_packages=venv_site_packages,
        regex=regex,
        extensions=targets,
    )


def _extensions_from_choice(choice: str) -> tuple[str, ...]:
    """Map CLI --ext choice to a set of file suffixes."""
    choice = choice.lower()
    if choice == "pyd":
        return (PYD_EXTENSION,)
    if choice == "so":
        return (SO_EXTENSION,)
    if choice == "py":
        return (".py",)
    if choice == "compiled":
        return (PYD_EXTENSION, SO_EXTENSION)
    if choice == "all":
        return (PYD_EXTENSION, SO_EXTENSION, ".py")
    # Fallback (should not happen due to click.Choice)
    return (PYD_EXTENSION,)


def _get_venv_site_packages(venv_path: str | None = None) -> Path | None:
    """Get the site-packages directory from the given or current virtual environment.

    Supports:
    - Windows: <venv>/Lib/site-packages
    - Unix:    <venv>/lib/pythonX.Y/site-packages
    - Current interpreter (no venv_path): first sys.path entry containing 'site-packages'
    """
    if venv_path:
        venv = Path(venv_path).resolve()
        if not venv.exists() or not venv.is_dir():
            logger.error("Path '%s' does not exist or is not a directory.", venv)
            return None

        win_candidate = venv / "Lib" / "site-packages"
        if win_candidate.is_dir():
            return win_candidate

        # Try common Unix patterns
        lib_dir = venv / "lib"
        if lib_dir.is_dir():
            # e.g. lib/python3.12/site-packages
            for py_dir in lib_dir.glob("python*/site-packages"):
                if py_dir.is_dir():
                    return py_dir

        logger.error("Could not find site-packages under '%s'.", venv)
        return None

    return next((Path(p) for p in sys.path if "site-packages" in p), None)


def _find_modules_in_site_packages(
    venv_site_packages: Path,
    regex: str | None,
    *,
    extensions: tuple[str, ...],
) -> list[str]:
    """Find all submodules in site-packages matching the extensions and optional regex."""
    files: list[Path] = []
    for ext in extensions:
        files.extend(venv_site_packages.rglob(f"*{ext}"))

    submodules: set[str] = set()

    for file in files:
        module_name = _extract_submodule_name(file, venv_site_packages)

        if regex and not re.search(regex, module_name, re.IGNORECASE):
            continue

        submodules.add(module_name)

    return sorted(submodules)


# Examples this should normalize:
#   pkg/core.cpython-312-x86_64-linux-gnu.so           -> pkg.core
#   pkg/ext.cp312-win_amd64.pyd                        -> pkg.ext
#   pkg/sub/__init__.cpython-311-darwin.so             -> pkg.sub
#   pkg/sub/__init__.pyd                               -> pkg.sub
#   pkg/sub/module.py                                  -> pkg.sub.module
_ABI_TAG_PATTERN = re.compile(
    r"""
    \.
    (?:                 # typical variants:
       cp\d+            # cp312, cp311, etc.
      |cpython-\d+[^\./]*  # cpython-312, cpython-312-x86_64-linux-gnu, etc.
    )
    \.
    (?:pyd|so)
    $
    """,
    re.VERBOSE,
)


def _extract_submodule_name(module_file: Path, venv_site_packages: Path) -> str:
    """Convert a file path to a dotted submodule name, normalizing for .py/.pyd/.so + ABI tags."""
    relative_path = module_file.relative_to(venv_site_packages)
    s = str(relative_path)

    # 1) Remove ABI/platform tags like ".cp312-win_amd64.pyd" or ".cpython-312-x86_64-linux-gnu.so"
    s = _ABI_TAG_PATTERN.sub("", s)

    # 2) Remove trailing file suffixes
    s = re.sub(r"\.(pyd|so|py)$", "", s, flags=re.IGNORECASE)

    # 3) Convert path separators to dots
    s = s.replace(os.sep, ".")

    # 4) Map package __init__ to its package name
    if s.endswith(".__init__"):
        s = s[: -len(".__init__")]

    return s
