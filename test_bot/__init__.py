# SPDX-License-Identifier: MIT

import logging
import logging.handlers
import pathlib

from .config import Config

_LOG_FORMAT = "%(asctime)s: [%(levelname)s] (%(threadName)s) %(name)s: %(message)s"

logging.basicConfig(
    format=_LOG_FORMAT,
    level=logging.DEBUG if Config.debug else logging.INFO,
)


def _log_to_file() -> None:
    log_format = logging.Formatter(_LOG_FORMAT)

    # Set up file logging
    log_file = pathlib.Path("./test_bot.log")

    # File handler rotates logs every 5 MB
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * (2**20),
        backupCount=2,
        encoding="utf-8",
    )
    file_handler.setFormatter(log_format)
    logging.getLogger().addHandler(file_handler)


def _set_trace_loggers() -> None:
    """Set loggers to the debug level according to the value from the DEBUG_LOGGERS env var.

    When the env var is a list of logger names delimited by a comma,
    each of the listed loggers will be set to the debug level.
    """
    level_filter = Config.debug_loggers
    if not level_filter:
        return

    for logger_name in level_filter.split(","):
        if not logger_name:
            continue
        logging.getLogger(logger_name.strip()).setLevel(logging.DEBUG)


_set_trace_loggers()

if Config.log_to_file:
    _log_to_file()
