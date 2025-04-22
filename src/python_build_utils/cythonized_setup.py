"""
Utility for conditionally building Python packages with optional Cython extensions.

This module provides a single function, `cythonized_setup`, to facilitate building
Python packages that optionally use Cython for compiling `.py` files into extension modules.

Functions
---------
cythonized_setup(module_name: str) -> None
    Set up the package, conditionally compiling Cython extensions based on the
    `CYTHON_BUILD` environment variable.

    If `CYTHON_BUILD` is set:
        - Uses Cython to compile `.py` files under `src/{module_name}` into extension modules.
        - Imports `cythonize` and `Options` from Cython.
        - Disables docstrings and code comments in the generated Cython code.
        - Recursively finds and compiles all `.py` files in `src/{module_name}`.

    If `CYTHON_BUILD` is not set:
        - Installs the package as a pure Python package without Cython extensions.

    The function configures `setuptools.setup` with:
        - `package_dir` pointing to the `src` directory.
        - `package_data` to include compiled `.pyd` files.
        - `exclude_package_data` to exclude `.py` and `.c` files from the package.

Parameters
----------
module_name : str
    The name of the Python module/package to be built.

Returns
-------
None
"""

import glob
import os

from setuptools import setup


def cythonized_setup(module_name):
    requires_cython = os.environ.get("CYTHON_BUILD", 0)
    # requires_cython = True
    print("requires_cython:", requires_cython)
    if requires_cython:
        from Cython.Build import cythonize
        from Cython.Compiler import Options

        Options.docstrings = False
        Options.emit_code_comments = False

        print("⛓️ Building with Cython extensions")
        py_files = glob.glob(f"src/{module_name}/**/*.py", recursive=True)
        ext_modules = cythonize(py_files, compiler_directives={"language_level": "3"})
    else:
        print("🚫 No Cython build — pure Python package")
        ext_modules = []

    setup(
        name=module_name,
        package_dir={"": "src"},
        package_data={module_name: ["**/*.pyd", "**/**/*.pyd"]},
        exclude_package_data={module_name: ["**/*.py", "**/*.c", "**/**/*.py", "**/**/*.c"]},
        ext_modules=ext_modules,
    )
