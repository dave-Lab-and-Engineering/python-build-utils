"""Build Python package with optional Cython extensions."""

import logging
import os
from pathlib import Path

from setuptools import setup


logger = logging.getLogger(__name__)

CYTHON_REQUIRED_MESSAGE = (
    "Cython is required for building this package with Cython extensions. Please install Cython and try again."
)


def cythonized_setup(module_name: str) -> None:
    """Set up a Python package with optional Cython compilation.

    If the `CYTHON_BUILD` environment variable is set, all `.py` files under
    `src/{module_name}` are compiled using Cython. Otherwise, the package is installed
    as pure Python.

    Args:
        module_name: Name of the top-level Python module/package to build.

    Raises:
        ImportError: If Cython is required but not installed.

    """
    should_use_cython = os.environ.get("CYTHON_BUILD", "").strip() != ""
    ext_modules = []

    if should_use_cython:
        try:
            from Cython.Build import cythonize
            from Cython.Compiler import Options
        except ImportError as e:
            raise ImportError(CYTHON_REQUIRED_MESSAGE) from e

        Options.docstrings = False
        Options.emit_code_comments = False

        logger.info("⛓️ Building with Cython extensions")

        py_files = [str(path) for path in Path("src", module_name).rglob("*.py")]
        ext_modules = cythonize(py_files, compiler_directives={"language_level": "3"})
    else:
        logger.info("🚫 No Cython build — pure Python package")

    setup(
        name=module_name,
        package_dir={"": "src"},
        package_data={module_name: ["**/*.pyd", "**/**/*.pyd"]},
        exclude_package_data={module_name: ["**/*.py", "**/*.c", "**/**/*.py", "**/**/*.c"]},
        ext_modules=ext_modules,
    )
