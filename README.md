# python-build-utils

[![Release](https://img.shields.io/github/v/release/eelcovv/python-build-utils)](https://img.shields.io/github/v/release/eelcovv/python-build-utils)
[![Build status](https://img.shields.io/github/actions/workflow/status/eelcovv/python-build-utils/main.yml?branch=main)](https://github.com/eelcovv/python-build-utils/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/eelcovv/python-build-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/eelcovv/python-build-utils)
[![Commit activity](https://img.shields.io/github/commit-activity/m/eelcovv/python-build-utils)](https://img.shields.io/github/commit-activity/m/eelcovv/python-build-utils)
[![License](https://img.shields.io/github/license/eelcovv/python-build-utils)](https://img.shields.io/github/license/eelcovv/python-build-utils)

Small collection of command line utilities to assist with building your python wheels

- **Github repository**: <https://github.com/dave-Lab-and-Engineering/python-build-utils>
- **Documentation** <https://eelcovv.github.io/python-build-utils/>

## Description

### Cli-tool `python-build-utils`

```shell
(python-build-utils) PS> python-build-utils.exe --help
Usage: python-build-utils [OPTIONS] COMMAND [ARGS]...

  A collection of CLI tools for Python build utilities.

Options:
  --help  Show this message and exit.

Commands:
  remove-tarballs     Remove tarball files from dist
  rename-wheel-files  Rename wheel files in the dist folder.
  py2wheel            Rename wheel files in the dist folder.

(python-build-utils) PS> python-build-utils.exe --help
Usage: python-build-utils [OPTIONS] COMMAND [ARGS]...

  A collection of CLI tools for Python build utilities.

Options:
  --help  Show this message and exit.

Commands:
  remove-tarballs     Remove tarball files from dist.
  rename-wheel-files  Rename wheel files in the dist folder.
```

### rename-wheel-files

```shell
(python-build-utils) PS> rename-wheel-files.exe --help
Usage: rename-wheel-files [OPTIONS]

  Rename wheel files in the dist folder.

  This function renames wheel files in the given distribution directory by
  replacing the "py3-none-any" tag with a custom build version tag. The build
  version tag is constructed using the provided `python_version_tag`,
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

Options:
  --dist_dir TEXT            Directory containing wheel files. Default is
                             'dist'
  --python_version_tag TEXT  Explicitly specify the python version tag.
                             Default is cp{major}{minor}.
  --platform_tag TEXT        Explicitly specify the platform tag. Default is
                             sysconfig.get_platform().
  --wheel_tag TEXT           Explicitly specify the total wheel tag. Default is
                             {python_version_tag}-{python_version_tag}-{platform_tag}.
  --help                     Show this message and exit.
```

#### Example of using rename-wheel-file

From your project root folder, just run

```shell
rename-wheel-files
```

### remove-tarballs

```shell
(python-build-utils) PS> remove-tarballs.exe --help
Usage: remove-tarballs [OPTIONS]

  Remove tarball files from dist.

  This function removes tarball files from the given distribution directory.

  Args:     dist_dir (str): The directory containing the tarball files to be
  removed.

Options:
  --dist_dir TEXT  Directory containing wheel the files. Default is 'dist'
  --help           Show this message and exit.
```

#### Example of using remove-tarballs

From your project root folder, just run

```shell
remove-tarballs
```

### pyd2wheel tool

This is a tool to convert bare .pyd files to a wheel file such that they can be installed.

```shell
pyd2wheel .\mybinary.cp310-win_amd64.pyd --version=1.0.0
```

or from python:

```python
from python_build_utils import pyd2wheel
pyd2wheel("mybinary.cp310-win_amd64.pyd", version="1.0.0")
```

This will create a wheel file named in the same directory as the input file.
Note: The version argument is used only if the version is not already present in the filename (like in the example above).
