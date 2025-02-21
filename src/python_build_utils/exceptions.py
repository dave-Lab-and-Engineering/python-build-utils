"""Exceptions for the python_build_utils package."""

PYD_FILE_FORMATS = {
    "long": "{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.pyd",
    "short": "{distribution}.{python tag}-{platform tag}.pyd",
}


class PydFileSuffixError(Exception):
    """Exception raised for errors in the pyd file format."""

    def __init__(self, filename: str) -> None:
        message = f"The file {filename} does not of type '.pyd'.\nQuitting now."
        super().__init__(message)


class PydFileFormatError(Exception):
    """Exception raised for errors in the pyd file format."""

    def __init__(self, filename: str) -> None:
        message = (
            f"File information could not be extracted from file {filename}.\n"
            f"Two formats are supported:\n -- {PYD_FILE_FORMATS['long']}\n -- {PYD_FILE_FORMATS['short']}"
        )
        super().__init__(message)


class VersionNotFoundError(Exception):
    """Exception raised if no version was found or given."""

    def __init__(self) -> None:
        message = (
            "The version of the package should be provided\nIt can not be extracted from the pyd file.\n"
            "Please run with the --package_version <version> option."
        )
        super().__init__(message)
