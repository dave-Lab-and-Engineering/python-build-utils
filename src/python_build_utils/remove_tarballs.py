"""Remove the tar.gz files from the dist build folder."""

import glob
import os
import textwrap

import click

from . import __version__


@click.command(name="remove-tarballs")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option(
    "--dist_dir",
    default="dist",
    help=textwrap.dedent("""
    Directory containing wheel the files.
    Default is 'dist'
"""),
)
def remove_tarballs(dist_dir: str) -> None:
    """Remove tarball files from dist.

    This function removes tarball files from the given distribution directory.

    Args:
        dist_dir (str): The directory containing the tarball files to be removed.

    Returns:
        None

    Example:
        remove_tarballs("dist")
    """

    dist_dir = dist_dir.rstrip("/")

    found_files = False

    for tarball_file in glob.glob(f"{dist_dir}/*.tar.gz"):
        found_files = True
        try:
            os.remove(tarball_file)
        except FileNotFoundError as e:
            click.echo(f"Error {e}")
        else:
            click.echo(f"Removed {tarball_file}")

    if not found_files:
        click.echo(f"No tarball files found in {dist_dir}")
