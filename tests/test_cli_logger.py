"""Unit tests for CLI logger initialization logic in `cli_logger`.

Verifies:
- Handler is added when none exists.
- Handler is not duplicated.
- Logger instance returned is consistent.
"""

import logging
from unittest.mock import patch

from python_build_utils import LOGGER_NAME, cli_logger


def test_initialize_logging_adds_handler_when_none_present() -> None:
    """Ensure a handler is added if no handlers are present on the logger."""
    logger = logging.getLogger(LOGGER_NAME)

    with (
        patch.object(logger, "hasHandlers", return_value=False),
        patch.object(logger, "addHandler") as mock_add_handler,
    ):
        returned = cli_logger.initialize_logging()

        assert mock_add_handler.called
        assert returned is logger


def test_initialize_logging_skips_add_handler_when_present() -> None:
    """Ensure no new handler is added if one already exists."""
    logger = logging.getLogger(LOGGER_NAME)

    with patch.object(logger, "hasHandlers", return_value=True), patch.object(logger, "addHandler") as mock_add_handler:
        returned = cli_logger.initialize_logging()

        mock_add_handler.assert_not_called()
        assert returned is logger


def test_initialize_logging_does_not_duplicate_handlers() -> None:
    """Check that no duplicate handlers are added on repeated calls."""
    logger = logging.getLogger(LOGGER_NAME)
    existing_count = len(logger.handlers)

    cli_logger.initialize_logging()
    cli_logger.initialize_logging()  # Call again

    final_count = len(logger.handlers)
    assert final_count in {existing_count, 1}
