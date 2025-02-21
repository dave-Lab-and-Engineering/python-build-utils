"""This module creates a wheel from a pyd file."""

import hashlib
import os
import shutil
from pathlib import Path

import click

PYD_FILE_FORMATS = {
    "long": "{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.pyd",
    "short": "{distribution}.{python tag}-{platform tag}.pyd",
}


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

            with open(os.path.join(root, file), "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            sha256_digest = sha256_hash.hexdigest()

            file_size_in_bytes = os.path.getsize(os.path.join(root, file))

            # officially the HASH should be added here
            record_content += f"{root}/{file},sha256={sha256_digest},{file_size_in_bytes}\n"

    # add record itself
    record_content += f"{root_folder}/RECORD,,\n"
    return record_content


@click.command(name="pyd2wheel")
@click.argument("pyd_file", type=click.Path(exists=True))
@click.option("--version", help="The version of the package.", default=None)
@click.option("--abi_tag", help="The ABI tag of the package. Default is 'none'.", default="none")
def pyd2wheel(pyd_file: Path | str, version: str | None = None, abi_tag="none"):
    """This function creates a wheel from a pyd file.

    The wheel is created in the same directory as the pyd file.

    Args:
        pyd_file (Path or str): The path to the pyd file.
        version (str): The version of the package.
        abi_tag (str): The ABI tag of the package. Default is 'none'.

    Notes:
    * The binary format of a wheel is described [here]
    (https://packaging.python.org/en/latest/specifications/binary-distribution-format/#binary-distribution-format)

    * Wheel .dist-info directories include at a minimum METADATA, WHEEL, and RECORD.

        - METADATA is the package metadata, the same format as PKG-INFO as found at the root of sdists.
        - WHEEL is the wheel metadata specific to a build of the package.
        - RECORD is a list of (almost) all the files in the wheel and their secure hashes and file-size in bytes

    File Format:

        File name convention
        The wheel filename is {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl.
        For example, distribution-1.0-1-py27-none-any.whl is the first build of a package called *distribution*,
        and is compatible with Python 2.7 (any Python 2.7 implementation), with no ABI (pure Python), on any CPU
        architecture.
    """
    pyd_file = Path(pyd_file)

    # extract the name, version, python version, and platform from the pyd file name
    try:
        try:
            name, version, python_version, platform = pyd_file.stem.split("-")
        except AttributeError:
            # assume filename like DAVEcore.cp310-win_amd64.pyd
            name, python_version, platform = pyd_file.stem.replace(".", "-").split("-")
    except AttributeError as err:
        message = "The pyd file name should be one of these formats: "
        message += "\n - " + "\n - ".join(PYD_FILE_FORMATS.values())
        message += f"\nGot pyd_file: {pyd_file}"
        click.echo(message, err=True)
        raise AttributeError from err

    if version is None:
        # try to extract the version from the pyd file name
        version = pyd_file.stem.split("-")[1]
        message = "The version of the package should be provided as it can not be extracted from the pyd file name."
        click.echo(message, err=True)
        raise ValueError(message)

    click.echo("name:", name)
    click.echo("version:", version)
    click.echo("python_version:", python_version)
    click.echo("platform:", platform)
    click.echo("abi_tag:", abi_tag)

    wheel_file_name = f"{name}-{version}-{python_version}-{abi_tag}-{platform}.whl"

    # create a temporary directory to store the contents of the wheel file

    root_folder = pyd_file.parent / "wheel_temp"
    root_folder.mkdir(exist_ok=True)

    # File contents
    #   The contents of a wheel file,
    #   the root of the archive, contains all files to be installed in purelib or platlib as specified in WHEEL.

    # copy the pyd file to the root of the archive
    shutil.copy(pyd_file, root_folder / pyd_file.name)

    # we need a dist folder
    # ERROR: dummy has an invalid wheel, .dist-info directory not found

    #
    # # {distribution}-{version}.dist-info/ contains metadata.
    dist_info = root_folder / f"{name}-{version}.dist-info"
    dist_info.mkdir(exist_ok=True)
    #
    # ERROR: dummy has an invalid wheel, could not read 'dummy-0.1.0.dist-info/WHEEL'
    # file: KeyError("There is no item named 'dummy-0.1.0.dist-info/WHEEL' in the archive")

    # {distribution}-{version}.dist-info/METADATA is Metadata version 1.1 or greater format metadata.
    metadata_filename = dist_info / "METADATA"
    metadata_content = make_metadata_content(name, version)

    with open(metadata_filename, "w", encoding="utf-8") as f:
        f.write(metadata_content)

    # {distribution}-{version}.dist-info/WHEEL is metadata about the archive itself in the same basic key: value format:
    wheel_content = make_wheel_content(python_version, abi_tag, platform)
    with open(dist_info / "WHEEL", "w", encoding="utf-8") as f:
        f.write(wheel_content)

    record_content = make_record_content(root_folder)
    record_filename = dist_info / "RECORD"

    with open(record_filename, "w", encoding="utf-8") as f:
        f.write(record_content)

    # create the .whl file by zipping the contents of the temporary directory
    wheel_file_path = pyd_file.parent / wheel_file_name

    # remove the existing wheel file if it exists
    result_file = wheel_file_path.with_suffix(".zip")
    if result_file.exists():
        result_file.unlink()

    created_name = shutil.make_archive(str(wheel_file_path), "zip", root_folder)

    # rename the zip file to a .whl file
    if wheel_file_path.exists():
        wheel_file_path.unlink()
    os.rename(created_name, wheel_file_path)

    click.echo(f"created wheel file: {wheel_file_path}")

    # remove the temporary directory
    shutil.rmtree(root_folder)

    return wheel_file_path
