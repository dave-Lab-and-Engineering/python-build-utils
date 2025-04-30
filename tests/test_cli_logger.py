import logging
from unittest.mock import patch

from python_build_utils import LOGGER_NAME, cli_logger


def test_initialize_logging_adds_handler_when_none_present():
    logger = logging.getLogger(LOGGER_NAME)

    # Patch hasHandlers to return False and monitor addHandler
    with (
        patch.object(logger, "hasHandlers", return_value=False),
        patch.object(logger, "addHandler") as mock_add_handler,
    ):
        returned = cli_logger.initialize_logging()

        assert mock_add_handler.called
        assert returned is logger


def test_initialize_logging_skips_add_handler_when_present():
    logger = logging.getLogger(LOGGER_NAME)

    # Patch hasHandlers to return True and ensure addHandler is not called
    with patch.object(logger, "hasHandlers", return_value=True), patch.object(logger, "addHandler") as mock_add_handler:
        returned = cli_logger.initialize_logging()

        mock_add_handler.assert_not_called()
        assert returned is logger


def test_initialize_logging_does_not_duplicate_handlers():
    logger = logging.getLogger(LOGGER_NAME)
    existing_count = len(logger.handlers)

    cli_logger.initialize_logging()
    cli_logger.initialize_logging()  # Call again to check duplication

    # Should not have added a second handler
    assert len(logger.handlers) == existing_count or len(logger.handlers) == 1
