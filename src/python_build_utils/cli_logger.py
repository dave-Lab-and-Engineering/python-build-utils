import logging

from rich.logging import RichHandler

from . import LOGGER_NAME


def initialize_logging() -> logging.Logger:
    """Gets the DAVE_SUITE_LOGGER_NAME logger and sets up a console handler if not already present."""

    _logger = logging.getLogger(LOGGER_NAME)
    _logger.setLevel(logging.WARNING)  # Set logger level here ✅

    # Ensure the dave-suite logger captures logs from child loggers (including DAVE)
    _logger.propagate = True

    if not _logger.hasHandlers():
        # Console handler
        console_handler = RichHandler(show_time=True, show_path=True, rich_tracebacks=True)

        console_handler.setLevel(logging.WARNING)
        _logger.addHandler(console_handler)

    return _logger
