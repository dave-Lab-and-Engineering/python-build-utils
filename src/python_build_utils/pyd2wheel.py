"""This module creates a wheel from a pyd file."""

import hashlib
import os
import re
import shutil
from pathlib import Path
from typing import Optional

import click

from . import __version__

PYD_FILE_FORMATS = {
    "long": "{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.pyd",
    "short": "{distribution}.{python tag}-{platform tag}.pyd",
}


class PydFileFormatError(Exception):
    """Exception raised for errors in the pyd file format."""

    def __init__(self, filename: str):
        self.filename = filename
        self.message = (
            f"File information could not be extracted from file {filename}. "
            f"Two formats are supported: {PYD_FILE_FORMATS['long']} or {PYD_FILE_FORMATS['short']}"
        )
        super().__init__(self.message)


@click.command(name="pyd2wheel")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.argument("pyd_file", type=click.Path(exists=True))
@click.option("--package_version", help="The version of the package.", default=None)
@click.option("--abi_tag", help="The ABI tag of the package. Default is 'none'.", default="none")
def pyd2wheel(pyd_file: Path, package_version: Optional[str | None] = None, abi_tag=Optional[str | None]) -> Path:
    """Cli interface of pyd2wheel function."""
    return convert_pyd_to_wheel(pyd_file, package_version, abi_tag)


def convert_pyd_to_wheel(pyd_file: Path, package_version: str | None = None, abi_tag: str | None = None) -> Path:
    """Creates a wheel from a pyd file."""
    pyd_file = Path(pyd_file)
    name, version_from_filename, python_version, platform = extract_pyd_file_info(pyd_file)
    package_version = get_package_version(package_version, version_from_filename)
    abi_tag = abi_tag or "none"

    display_wheel_info(name, package_version, python_version, platform, abi_tag)

    wheel_file_name = f"{name}-{package_version}-{python_version}-{abi_tag}-{platform}.whl"
    root_folder = create_temp_directory(pyd_file)
    dist_info = create_dist_info_directory(root_folder, name, package_version)

    create_metadata_file(dist_info, name, package_version)
    create_wheel_file(dist_info, python_version, abi_tag, platform)
    create_record_file(root_folder, dist_info)

    wheel_file_path = create_wheel_archive(pyd_file, wheel_file_name, root_folder)
    click.echo(f"created wheel file: {wheel_file_path}")

    shutil.rmtree(root_folder)
    return wheel_file_path


def make_metadata_content(name: str, version: str) -> str:
    """Create the metadata for the wheel file."""
    meta_data = "Metadata-Version: 2.1\n"
    meta_data += f"Name: {name}\n"
    meta_data += f"Version: {version}\n"
    return meta_data


def make_wheel_content(python_version: str, abi_tag: str, platform: str) -> str:
    """Create the wheel data for the wheel file."""
    wheel_data = "Wheel-Version: 1.0\n"
    wheel_data += "Generator: bdist_wheel 1.0\n"
    wheel_data += "Root-Is-Purelib: false\n"
    wheel_data += f"Tag: {python_version}-{abi_tag}-{platform}\n"
    wheel_data += "Build: 1"
    return wheel_data


def make_record_content(root_folder: Path) -> str:
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


def extract_pyd_file_info(pyd_file: Path) -> tuple:
    """Extract the name, version, python version, and platform from the pyd file name."""
    # remove suffix and split the filename on the hyphens

    bare_file_name = pyd_file.stem

    # Assume the base_file_name is like: dummy-0.1.0-py311-win_amd64"
    # where the version can be 0, 0.1, or 0.1.1 and at least a python version and a platform are provided
    match = re.match(r"(.*?)-((?:\d\.){0,2}\d)-(.*)-(.*)", bare_file_name)
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


def get_package_version(package_version: str | None, version_from_filename: str | None) -> str:
    """Get the package version from the provided version or the pyd file name."""
    if package_version is None and version_from_filename is not None:
        return version_from_filename

    if package_version is None:
        message = "The version of the package should be provided as it can not be extracted from the pyd file name."
        click.echo(message, err=True)
        raise ValueError(message)

    return package_version


def display_wheel_info(name: str, package_version: str, python_version: str, platform: str, abi_tag: str) -> None:
    """Display the wheel information."""
    click.echo(f"{'Field':<15}{'Value'}")
    click.echo(f"{'-' * 30}")
    click.echo(f"{'Name:':<15}{name}")
    click.echo(f"{'Version:':<15}{package_version}")
    click.echo(f"{'Python Version:':<15}{python_version}")
    click.echo(f"{'Platform:':<15}{platform}")
    click.echo(f"{'ABI Tag:':<15}{abi_tag}")


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


def create_metadata_file(dist_info: Path, name: str, package_version: str) -> None:
    """Create the METADATA file."""
    metadata_filename = dist_info / "METADATA"
    metadata_content = make_metadata_content(name, package_version)
    with open(metadata_filename, "w", encoding="utf-8") as f:
        f.write(metadata_content)


def create_wheel_file(dist_info: Path, python_version: str, abi_tag: str, platform: str) -> None:
    """Create the WHEEL file."""
    wheel_content = make_wheel_content(python_version, abi_tag, platform)
    with open(dist_info / "WHEEL", "w", encoding="utf-8") as f:
        f.write(wheel_content)


def create_record_file(root_folder: Path, dist_info: Path) -> None:
    """Create the RECORD file."""
    record_content = make_record_content(root_folder)
    record_filename = dist_info / "RECORD"
    with open(record_filename, "w", encoding="utf-8") as f:
        f.write(record_content)


def create_wheel_archive(pyd_file: Path, wheel_file_name: str, root_folder: Path) -> Path:
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
