import os
import shutil
from pathlib import Path
import hashlib

import click

from . import __version__


@click.command(name="pyd2wheel")
@click.argument('pyd_file', type=click.Path(exists=True))
@click.option(
    "--version",
    help="The version of the package.",
    default=None)
@click.option(
    "--abi_tag",
    help="The ABI tag of the package. Default is 'none'.",
    default="none")
def pyd2wheel(pyd_file: Path or str,
              version: str or None = None,
              abi_tag = 'none'):
    """This function creates a wheel from a pyd file.

    The wheel is created in the same directory as the pyd file.

    Args:
        pyd_file (Path or str): The path to the pyd file.
        version (str): The version of the package.
        abi_tag (str): The ABI tag of the package. Default is 'none'.

    The binary format of a wheel is described here: https://packaging.python.org/en/latest/specifications/binary-distribution-format/#binary-distribution-format

    Wheel .dist-info directories include at a minimum METADATA, WHEEL, and RECORD.

    METADATA is the package metadata, the same format as PKG-INFO as found at the root of sdists.
    WHEEL is the wheel metadata specific to a build of the package.
    RECORD is a list of (almost) all the files in the wheel and their secure hashes and file-size in bytes

    """
    pyd_file = Path(pyd_file)

    # extract the name, version, python version, and platform from the pyd file name
    try:
        try:
            name, version, python_version, platform = pyd_file.stem.split('-')
        except:
            # assume filename like DAVEcore.cp310-win_amd64.pyd
            name, python_version, platform = pyd_file.stem.replace('.','-').split('-')
    except:
        msg = 'The pyd file name should be in the format {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.pyd or\n {distribution}.{python tag}-{platform tag}.pyd\n'
        msg += f'\nGot pyd_file: {pyd_file}'

        raise ValueError(msg)

    assert version is not None, 'The version of the package should be provided as it can not be extracted from the pyd file name.'

    print('name:', name)
    print('version:', version)
    print('python_version:', python_version)
    print('platform:', platform)
    print('abi_tag:', abi_tag)


    # File Format
    #     File name convention
    #     The wheel filename is {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl.
    #     For example, distribution-1.0-1-py27-none-any.whl is the first build of a package called ‘distribution’, and is compatible with Python 2.7 (any Python 2.7 implementation), with no ABI (pure Python), on any CPU architecture.
    wheel_file_name = f'{name}-{version}-{python_version}-{abi_tag}-{platform}.whl'


    # create a temporary directory to store the contents of the wheel file

    root_folder = pyd_file.parent / 'wheel_temp'
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
    dist_info = root_folder / f'{name}-{version}.dist-info'
    dist_info.mkdir(exist_ok=True)
    #
    # ERROR: dummy has an invalid wheel, could not read 'dummy-0.1.0.dist-info/WHEEL'
    # file: KeyError("There is no item named 'dummy-0.1.0.dist-info/WHEEL' in the archive")

    # {distribution}-{version}.dist-info/METADATA is Metadata version 1.1 or greater format metadata.
    metadata = dist_info / 'METADATA'
    metadata_content = f'''Metadata-Version: 2.1
Name: {name}
Version: {version}
'''

    with open(metadata, 'w') as f:
        f.write(metadata_content)

    # {distribution}-{version}.dist-info/WHEEL is metadata about the archive itself in the same basic key: value format:
    wheel_content = f'''Wheel-Version: 1.0
Generator: bdist_wheel 1.0
Root-Is-Purelib: false
Tag: {python_version}-{abi_tag}-{platform}
Build: 1'''


    # create the RECORD file
    # RECORD is a list of (almost) all the files in the wheel and their secure hashes.

    # loop over all the files in the wheel and add them to the RECORD file
    record_content = ''
    for root, dirs, files in os.walk(root_folder):
        for file in files:

            # get the hash of the file using sha256
            sha256_hash = hashlib.sha256()

            with open(os.path.join(root, file), 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)

            sha256_digest = sha256_hash.hexdigest()

            file_size_in_bytes = os.path.getsize(os.path.join(root, file))

            record_content += f'{root}/{file},sha256={sha256_digest},{file_size_in_bytes}\n'   # officially the HASH should be added here

    # add record itself
    record_content += f'{dist_info}/RECORD,,\n'

    record = dist_info / 'RECORD'
    with open(record, 'w') as f:
        f.write(record_content)



    # make the WHEEL file
    with open(dist_info / 'WHEEL', 'w') as f:
        f.write(wheel_content)


    # create the .whl file by zipping the contents of the temporary directory
    wheel_file_path = pyd_file.parent / wheel_file_name

    # remove the existing wheel file if it exists
    result_file = wheel_file_path.with_suffix('.zip')
    if result_file.exists():
        result_file.unlink()

    created_name = shutil.make_archive(str(wheel_file_path), 'zip', root_folder)

    # rename the zip file to a .whl file
    if wheel_file_path.exists():
        wheel_file_path.unlink()
    os.rename(created_name, wheel_file_path)

    print('created wheel file:', wheel_file_path)

    # remove the temporary directory
    shutil.rmtree(root_folder)

    return wheel_file_path

