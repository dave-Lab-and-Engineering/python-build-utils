# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.8] - 2025-04-17
- Added logging functionality
- Added function api for external use
- collect-pyd module can now also include py modules:w
- Changed api of collect_package_dependies to allow argument to be a string

## [0.1.5] - 2025-04-15
- Added new command line utility collect-dependencies in order to generate a list of all package dependencies
- Added new command line utility collect-pyd-modules in order to generate a list of cythonized pyd dependencies
- Added new command line utility clean-pyd-modules in order to remove all cythonized files in a venv
- Updated README.md with new tool examples

## [0.1.2] - 2025-02-22

### Added

- MPL-2.0 license
- Code coverage published on [coveralls](https://coveralls.io/github/dave-Lab-and-Engineering/python-build-utils/)
- Improved readme and coupled badges to link pypi and build status


## [0.1.1] - 2025-02-21

### Added

- New tool `pyd2wheel` in order to pack wheel files based on *.pyd files
- Improved API
- Improved unit tests for all modules

## [0.0.2] - 2025-02-10

### Added

- Initial release of `python-build-utils`.
- Added CLI tools for renaming wheel files and removing tarballs.
- Included support for custom Python version tags, platform tags, and wheel tags.
- Added documentation and examples for using the CLI tools.
- Added unit tests
