"""Rename wheel files in the dist folder of your python build directory to include platform and python version tags."""

import glob
import logging
import os
import sys
import sysconfig
import textwrap

import click

logger = logging.getLogger(__name__)


@click.command(
    name="rename-wheel-files",
    help="Rename wheel files in a distribution directory by replacing the default 'py3-none-any' tag with a custom one.",
)
@click.option("--dist-dir", default="dist", help="Directory containing wheel files. Defaults to 'dist'.")
@click.option(
    "--python-version-tag",
    help="Python version tag to include in the new file name (e.g., cp310). Defaults to 'cp{major}{minor}' of the current Python.",
)
@click.option(
    "--platform-tag",
    help="Platform tag to include in the new file name. Defaults to the current platform value from sysconfig.",
)
@click.option(
    "--wheel-tag",
    help=textwrap.dedent("""
        Full custom wheel tag to replace 'py3-none-any'.
        If provided, this is used directly, ignoring the other tag options.
        Default format is: {python_version_tag}-{python_version_tag}-{platform_tag}
    """).strip(),
)
@click.pass_context
def rename_wheel_files(
    ctx: click.Context, dist_dir: str, python_version_tag: str, platform_tag: str, wheel_tag: str
) -> None:
    """
    Renames wheel files in a given distribution directory by replacing the
    'py3-none-any' tag with a custom wheel tag.

    Args:
        dist_dir (str): Directory containing the wheel files. Defaults to 'dist'.
        python_version_tag (str): Python version tag (e.g., cp39). If not provided, defaults to 'cp{major}{minor}'.
        platform_tag (str): Platform tag (e.g., win_amd64). If not provided, uses the current platform.
        wheel_tag (str): Full custom wheel tag. If provided, this is used directly.

    Behavior:
        - If --wheel-tag is provided, it is used for renaming.
        - Otherwise, constructs a wheel tag based on --python-version-tag and --platform-tag.
        - Renames all files in the directory matching '*py3-none-any.whl'.
        - Displays renaming actions or warnings if no files found.

    Example:
        rename-wheel-files --dist-dir dist --python-version-tag cp39 --platform-tag win_amd64
    """
    if wheel_tag:
        build_version_tag = wheel_tag
    else:
        if not python_version_tag:
            python_version_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
        if not platform_tag:
            platform_tag = sysconfig.get_platform().replace("-", "_")
        build_version_tag = f"{python_version_tag}-{python_version_tag}-{platform_tag}"

    dist_dir = dist_dir.rstrip("/")

    wheel_files = glob.glob(f"{dist_dir}/*py3-none-any.whl")

    if not wheel_files:
        logger.info(f"No matching wheel files found in '{dist_dir}'")
        return

    for wheel_file in wheel_files:
        new_file = wheel_file.replace("py3-none-any.whl", f"{build_version_tag}.whl")
        try:
            os.rename(wheel_file, new_file)
        except FileExistsError:
            logger.exception("Error")
        else:
            logger.info(f"Renamed: {wheel_file} → {new_file}")
