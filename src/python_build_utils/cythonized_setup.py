# This file replaces parts of setup.py with a Cythonized version.
# USe:
# from python_build_utils.cythonized_setup import cythonized_setup

# if __name__ == "__main__":
#     cythonized_setup("your_module_name")

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