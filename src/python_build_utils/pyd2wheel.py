"""
This module provides functionality to create a wheel file from a .pyd file.

Classes:
    PydFileFormatError: Exception raised for errors in the .pyd file format.

Functions:
    pyd2wheel(pyd_file: Path, package_version: Optional[str | None] = None, abi_tag=Optional[str | None]) -> Path:
        CLI interface for converting a .pyd file to a wheel file.

    convert_pyd_to_wheel(pyd_file: Path, package_version: str | None = None, abi_tag: str | None = None) -> Path:
"""

import hashlib
import os
import re
import shutil
from pathlib import Path

import click

from . import __version__
from .exceptions import PydFileFormatError, PydFileSuffixError, VersionNotFoundError


@click.command(name="pyd2wheel")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.argument("pyd_file", type=click.Path(exists=True))
@click.option("--package_version", help="The version of the package.", default=None)
@click.option("--abi_tag", help="The ABI tag of the package. Default is 'none'.", default=None)
def pyd2wheel(pyd_file: Path, package_version: str | None = None, abi_tag: str | None = None) -> Path | None:
    """Create a wheel from a compiled python *.pyd file."""

    return convert_pyd_to_wheel(pyd_file, package_version, abi_tag)


def convert_pyd_to_wheel(pyd_file: Path, package_version: str | None = None, abi_tag: str | None = None) -> Path | None:
    """
    Creates a wheel from a .pyd file.

    Args:
        pyd_file (Path): The path to the .pyd file.
        package_version (str | None, optional): The version of the package. If not provided, it will be extracted
            from the filename. Defaults to None.
        abi_tag (str | None, optional): The ABI tag for the wheel. If not provided, defaults to "none".

    Returns:
        Path: The path to the created wheel file.
    """
    pyd_file = Path(pyd_file)
    try:
        name, version_from_filename, python_version, platform = _extract_pyd_file_info(pyd_file)
    except (PydFileFormatError, PydFileSuffixError) as e:
        click.echo(e, err=True)
        return None

    try:
        package_version = _get_package_version(package_version, version_from_filename)
    except VersionNotFoundError as e:
        click.echo(e, err=True)
        return None

    if abi_tag is None:
        abi_tag = "none"

    _display_wheel_info(name, package_version, python_version, platform, abi_tag)

    wheel_file_name = f"{name}-{package_version}-{python_version}-{abi_tag}-{platform}.whl"
    root_folder = create_temp_directory(pyd_file)
    dist_info = create_dist_info_directory(root_folder, name, package_version)

    _create_metadata_file(dist_info, name, package_version)
    _create_wheel_file(dist_info, python_version, abi_tag, platform)
    _create_record_file(root_folder, dist_info)

    wheel_file_path = _create_wheel_archive(pyd_file, wheel_file_name, root_folder)
    click.echo(f"created wheel file: {wheel_file_path}")
    click.echo(f"{'-' * 80}")

    shutil.rmtree(root_folder)
    return wheel_file_path


def _make_metadata_content(name: str, version: str) -> str:
    """Create the metadata for the wheel file."""
    meta_data = "Metadata-Version: 2.1\n"
    meta_data += f"Name: {name}\n"
    meta_data += f"Version: {version}\n"
    return meta_data


def _make_wheel_content(python_version: str, abi_tag: str, platform: str) -> str:
    """Create the wheel data for the wheel file."""
    wheel_data = "Wheel-Version: 1.0\n"
    wheel_data += "Generator: bdist_wheel 1.0\n"
    wheel_data += "Root-Is-Purelib: false\n"
    wheel_data += f"Tag: {python_version}-{abi_tag}-{platform}\n"
    wheel_data += "Build: 1"
    return wheel_data


def _make_record_content(root_folder: Path) -> str:
    """Create the RECORD file content for the wheel.

    RECORD is a list of (almost) all the files in the wheel and their secure hashes.
    """
    record_content = ""
    # loop over all the files in the wheel and add them to the RECORD file
    for root, _, files in os.walk(root_folder):
        for file in files:
            # get the hash of the file using sha256
            sha256_hash = hashlib.sha256()

            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                while chunk := f.read(4096):  # Read in 4KB chunks
                    sha256_hash.update(chunk)

            sha256_digest = sha256_hash.hexdigest()

            file_size_in_bytes = os.path.getsize(os.path.join(root, file))

            # officially the HASH should be added here
            record_content += f"{root}/{file},sha256={sha256_digest},{file_size_in_bytes}\n"

    # add record itself
    record_content += f"{root_folder}/RECORD,,\n"
    return record_content


def _extract_pyd_file_info(pyd_file: Path) -> tuple:
    """Extract the name, version, python version, and platform from the pyd file name."""
    # remove suffix and split the filename on the hyphens

    if pyd_file.suffix != ".pyd":
        raise PydFileSuffixError(pyd_file.name)

    bare_file_name = pyd_file.stem

    # Assume the base_file_name is like:
    #   dummy-0.1.0-py311-win_amd64"  or
    #   dummy-0.1.0.py311-win_amd64"  or
    # where the version can be 0, 0.1, or 0.1.1 and at least a python version and a platform are provided
    match = re.match(r"(.*?)-((?:\d\.){0,2}\d)[.-](.*)-(.*)", bare_file_name)
    if match:
        name, package_version, python_version, platform = match.groups()
        return name, package_version, python_version, platform

    # Assume base_file_name is like  DAVEcore.cp310-win_amd64
    # i.e. the version is not provided and the build version and platform are separated by a dot
    match = re.match(r"(.*?)\.(.*)-(.*)", bare_file_name)
    if match:
        name, python_version, platform = match.groups()
        package_version = None
        return name, package_version, python_version, platform

    raise PydFileFormatError(bare_file_name)


def _get_package_version(package_version: str | None, version_from_filename: str | None) -> str:
    """Get the package version from the provided version or the pyd file name."""
    if package_version is None and version_from_filename is not None:
        return version_from_filename

    if package_version is None:
        raise VersionNotFoundError

    return package_version


def _display_wheel_info(name: str, package_version: str, python_version: str, platform: str, abi_tag: str) -> None:
    """Display the wheel information."""
    field_width = 25
    click.echo(f"{'=' * 80}")
    click.echo(f"{'Field':<{field_width}}{'Value'}")
    click.echo(f"{'-' * 80}")
    click.echo(f"{'Name:':<{field_width}}{name}")
    click.echo(f"{'Version:':<{field_width}}{package_version}")
    click.echo(f"{'Python Version:':<{field_width}}{python_version}")
    click.echo(f"{'Platform:':<{field_width}}{platform}")
    click.echo(f"{'ABI Tag:':<{field_width}}{abi_tag}")
    click.echo(f"{'-' * 80}")


def create_temp_directory(pyd_file: Path) -> Path:
    """Create a temporary directory to store the contents of the wheel file."""
    root_folder = pyd_file.parent / "wheel_temp"
    root_folder.mkdir(exist_ok=True)
    shutil.copy(pyd_file, root_folder / pyd_file.name)
    return root_folder


def create_dist_info_directory(root_folder: Path, name: str, package_version: str) -> Path:
    """Create the .dist-info directory."""
    dist_info = root_folder / f"{name}-{package_version}.dist-info"
    dist_info.mkdir(exist_ok=True)
    return dist_info


def _create_metadata_file(dist_info: Path, name: str, package_version: str) -> None:
    """Create the METADATA file."""
    metadata_filename = dist_info / "METADATA"
    metadata_content = _make_metadata_content(name, package_version)
    with open(metadata_filename, "w", encoding="utf-8") as f:
        f.write(metadata_content)


def _create_wheel_file(dist_info: Path, python_version: str, abi_tag: str, platform: str) -> None:
    """Create the WHEEL file."""
    wheel_content = _make_wheel_content(python_version, abi_tag, platform)
    with open(dist_info / "WHEEL", "w", encoding="utf-8") as f:
        f.write(wheel_content)


def _create_record_file(root_folder: Path, dist_info: Path) -> None:
    """Create the RECORD file."""
    record_content = _make_record_content(root_folder)
    record_filename = dist_info / "RECORD"
    with open(record_filename, "w", encoding="utf-8") as f:
        f.write(record_content)


def _create_wheel_archive(pyd_file: Path, wheel_file_name: str, root_folder: Path) -> Path:
    """Create the .whl file by zipping the contents of the temporary directory."""
    wheel_file_path = pyd_file.parent / wheel_file_name
    result_file = wheel_file_path.with_suffix(".zip")
    if result_file.exists():
        result_file.unlink()
    created_name = shutil.make_archive(str(wheel_file_path), "zip", root_folder)
    if wheel_file_path.exists():
        wheel_file_path.unlink()
    os.rename(created_name, wheel_file_path)
    return wheel_file_path
