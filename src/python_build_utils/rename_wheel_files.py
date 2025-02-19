"""Rename wheel files in the dist folder of your python build directory to include platform and python version tags."""

import glob
import os
import sys
import sysconfig
import textwrap

import click

from . import __version__


@click.command(name="rename-wheel-files")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option("--dist_dir", default="dist", help="Directory containing wheel files. Default is 'dist'")
@click.option("--python_version_tag", help="Explicitly specify the python version tag. Default is cp{major}{minor}")
@click.option("--platform_tag", help="Explicitly specify the platform tag. Default is sysconfig.get_platform()")
@click.option(
    "--wheel_tag",
    help=textwrap.dedent("""
    Explicitly specify the total wheel tag.
    Default is {python_version_tag}-{python_version_tag}-{platform_tag}
    """),
)
def rename_wheel_files(dist_dir: str, python_version_tag: str, platform_tag: str, wheel_tag: str) -> None:
    """Rename wheel files in the dist folder.

    This function renames wheel files in the given distribution directory by
    replacing the "py3-none-any" tag with a custom build version tag. The
    build version tag is constructed using the provided `python_version_tag`,
    `platform_tag`, and `wheel_tag`. If `wheel_tag` is provided, it is used
    directly as the build version tag. Otherwise, the build version tag is
    constructed using the `python_version_tag` and `platform_tag`.

    Args:

        dist_dir (str): The directory containing the wheel files to be renamed.
        Default is 'dist'.

        python_version_tag (str): The Python version tag to be included in the
        new file name. Default is cp{major}{minor}.

        platform_tag (str): The platform tag to be included in the new file
        name. Default is sysconfig.get_platform().

        wheel_tag (str): The custom wheel tag to be used as the build version
        tag. If this is provided, it is used directly as the build version tag
        and the other tags are ignored. If this is not provided, the build
        tag is constructed using the `python_version_tag` and `platform_tag` as
        described above.

    Returns:
        None

    Example:
        rename_wheel_files("dist", "cp39", "win_amd64", "")
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

    found_files = False

    for wheel_file in glob.glob(f"{dist_dir}/*py3-none-any.whl"):
        found_files = True
        new_file = wheel_file.replace("py3-none-any.whl", f"{build_version_tag}.whl")
        try:
            os.rename(wheel_file, new_file)
        except FileExistsError as e:
            click.echo(f"Error {e}")
        else:
            click.echo(f"Renamed {wheel_file} -> {new_file}")

    if not found_files:
        click.echo(f"No wheel files found in {dist_dir}")
