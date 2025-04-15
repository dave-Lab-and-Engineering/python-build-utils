# python-build-utils

[![GitHub Release](https://img.shields.io/github/v/release/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/releases/tag/0.1.1)
[![PyPI Version](https://img.shields.io/pypi/v/python-build-utils)](https://pypi.org/project/python-build-utils/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/dave-Lab-and-Engineering/python-build-utils/main.yml?branch=main)](https://github.com/dave-Lab-and-Engineering/python-build-utils/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/dave-Lab-and-Engineering/python-build-utils/badge.svg)](https://coveralls.io/github/dave-Lab-and-Engineering/python-build-utils)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/commits/main)
[![License](https://img.shields.io/github/license/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/blob/main/LICENSE)

Small collection of command line utilities to assist with building your python wheels

- **Github repository**: <https://github.com/dave-Lab-and-Engineering/python-build-utils>
- **Documentation** <https://dave-lab-and-engineering.github.io/python-build-utils/>

## Description

### Cli-tool `python-build-utils --help`

```text
Usage: python-build-utils [OPTIONS] COMMAND [ARGS]...

  A collection of CLI tools for Python build utilities.

Options:
  -v, --version  Show the version and exit.
  --help         Show this message and exit.

Commands:
  collect-dependencies  Collect and display dependencies for one or more...
  collect-pyd-modules   Collect and display .pyd submodules from a...
  pyd2wheel             Create a wheel from a compiled python *.pyd file.
  remove-tarballs       Remove tarball files from dist.
  rename-wheel-files    Rename wheel files in the dist folder.
```

### Cli-tool `rename-wheel-files --help`

```text
Usage: rename-wheel-files [OPTIONS]

  Rename wheel files in a distribution directory by replacing the default
  'py3-none-any' tag with a custom one.

Options:
  -v, --version              Show the version and exit.
  --dist-dir TEXT            Directory containing wheel files. Defaults to
                             'dist'.
  --python-version-tag TEXT  Python version tag to include in the new file
                             name (e.g., cp310). Defaults to
                             'cp{major}{minor}' of the current Python.
  --platform-tag TEXT        Platform tag to include in the new file name.
                             Defaults to the current platform value from
                             sysconfig.
  --wheel-tag TEXT           Full custom wheel tag to replace 'py3-none-any'.
                             If provided, this is used directly, ignoring the
                             other tag options. Default format is: {python_ver
                             sion_tag}-{python_version_tag}-{platform_tag}
  --help                     Show this message and exit.
```

#### Example of using rename-wheel-file

From your project root folder, just run

```shell
rename-wheel-files
```

### Cli-tool `remove-tarballs --help`

```text
Usage: remove-tarballs [OPTIONS]

  Remove tarball files from dist.

  This function removes tarball files from the given distribution directory.

  Args:     dist_dir (str): The directory containing the tarball files to be
  removed.

  Returns:     None

  Example:     remove_tarballs("dist")

Options:
  -v, --version    Show the version and exit.
  --dist_dir TEXT  Directory containing wheel the files. Default is 'dist'
  --help           Show this message and exit.
```

#### Example of using remove-tarballs

From your project root folder, just run

```shell
remove-tarballs
```

### Cli-tool `pyd2wheel --help`

``` text
Usage: pyd2wheel [OPTIONS] PYD_FILE

  Create a Python wheel file from a compiled .pyd file.

Options:
  -v, --version           Show the version and exit.
  --package-version TEXT  Version of the package. If not provided, the version
                          is extracted from the file name.
  --abi-tag TEXT          ABI tag for the wheel. Defaults to 'none'.
  --help                  Show this message and exit.
```

This is a tool to convert bare .pyd files to a wheel file such that they can be installed.

```shell
pyd2wheel .\mybinary.cp310-win_amd64.pyd --package_version 1.0.0
```

or from python:

```python
from python_build_utils import pyd2wheel
pyd2wheel("mybinary.cp310-win_amd64.pyd", package_version="1.0.0")
```

This will create a wheel file named in the same directory as the input file.

Note: The version argument is used only if the version is not already present in the filename (like in the example above).
