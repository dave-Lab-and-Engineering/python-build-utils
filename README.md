# python-build-utils

[![GitHub Release](https://img.shields.io/github/v/release/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/releases/tag/0.1.1)
[![PyPI Version](https://img.shields.io/pypi/v/python-build-utils)](https://pypi.org/project/python-build-utils/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/dave-Lab-and-Engineering/python-build-utils/main.yml?branch=main)](https://github.com/dave-Lab-and-Engineering/python-build-utils/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/dave-Lab-and-Engineering/python-build-utils/badge.svg)](https://coveralls.io/github/dave-Lab-and-Engineering/python-build-utils)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/commits/main)
[![License](https://img.shields.io/github/license/dave-Lab-and-Engineering/python-build-utils)](https://github.com/dave-Lab-and-Engineering/python-build-utils/blob/main/LICENSE)

Small collection of command line utilities to assist with building your Python wheels.

- GitHub repository: https://github.com/dave-Lab-and-Engineering/python-build-utils
- Documentation: https://dave-lab-and-engineering.github.io/python-build-utils/

---

## Installation

Install via PyPI:

```shell
pip install python-build-utils[all]
```

The optional [all] extra installs additional dependencies like pipdeptree, used by tools like collect-dependencies.

---

## Description

A collection of CLI tools for managing Python build artifacts, dependencies, and wheel files.

---

## CLI Tools Overview

Check available commands:

```text
python-build-utils --help

Usage: python-build-utils [OPTIONS] COMMAND [ARGS]...

  A collection of CLI tools for Python build utilities.

Options:
  -v, --version  Show the version and exit.
  --help         Show this message and exit.

Commands:
  clean-pyd-modules     Clean all .pyd/.c build modules from a virtual environment.
  collect-dependencies  Collect and display dependencies for one or more packages.
  collect-pyd-modules   Collect and display .pyd submodules from a virtual environment.
  pyd2wheel             Create a Python wheel file from a compiled .pyd file.
  remove-tarballs       Remove tarball files from dist.
  rename-wheel-files    Rename wheel files in a distribution directory by tag.
```

---

### clean-pyd-modules

```text
python-build-utils clean-pyd-modules --help 
Usage: clean-pyd-modules [OPTIONS]

  Clean all .pyd/.c build modules in src path.

Options:
  -v, --version     Show the version and exit.
  --src-path TEXT   Path to the src folder to scan for .pyd modules. Defaults to 'src'.
  -r, --regex TEXT  Optional regex to filter .pyd modules by name.
  --help            Show this message and exit.
```

Example:

clean-pyd-modules --regex dave

Removes .pyd and .c files from the src/ folder filtered by name.

---

### collect-dependencies

Usage: collect-dependencies [OPTIONS]

  Collect and display dependencies for one or more Python packages.

Options:
  -v, --version       Show the version and exit.
  -p, --package TEXT  Name of the Python package(s) to collect dependencies for. Can be given multiple times.
  -o, --output PATH   Optional file path to write the list of dependencies.
  --help              Show this message and exit.

---

### collect-pyd-modules

Usage: collect-pyd-modules [OPTIONS]

  Collect and display .pyd submodules from a virtual environment.

Options:
  -v, --version      Show the version and exit.
  --venv-path TEXT   Path to the virtual environment. Defaults to the current.
  -r, --regex TEXT   Optional regex to filter .pyd modules by name.
  -o, --output PATH  Optional file path to write the list of found .pyd modules.
  --help             Show this message and exit.

---

### rename-wheel-files

Usage: rename-wheel-files [OPTIONS]

  Rename wheel files in a distribution directory by replacing 'py3-none-any' with a custom tag.

Options:
  -v, --version              Show the version and exit.
  --dist-dir TEXT            Directory containing wheel files. Defaults to 'dist'.
  --python-version-tag TEXT  Python version tag (e.g. cp310). Defaults to the current Python.
  --platform-tag TEXT        Platform tag. Defaults to the current platform value.
  --wheel-tag TEXT           Full custom wheel tag to replace 'py3-none-any'.
  --help                     Show this message and exit.

Example:

rename-wheel-files

---

### remove-tarballs

Usage: remove-tarballs [OPTIONS]

  Remove tarball files from dist.

Options:
  -v, --version    Show the version and exit.
  --dist_dir TEXT  Directory containing tarball files. Defaults to 'dist'.
  --help           Show this message and exit.

Example:

remove-tarballs

---

### pyd2wheel

Usage: pyd2wheel [OPTIONS] PYD_FILE

  Create a Python wheel file from a compiled .pyd file.

Options:
  -v, --version           Show the version and exit.
  --package-version TEXT  Version of the package. If omitted, the version is extracted from the filename.
  --abi-tag TEXT          ABI tag for the wheel. Defaults to 'none'.
  --help                  Show this message and exit.

Example (CLI)

pyd2wheel .\mybinary.cp310-win_amd64.pyd --package_version 1.0.0

Example (Python)

from python_build_utils import pyd2wheel
pyd2wheel("mybinary.cp310-win_amd64.pyd", package_version="1.0.0")

The wheel is created in the same directory as the .pyd file.

---
