import logging
import os

from . import config

logging.basicConfig(
    format="%(asctime)s: [%(levelname)s] (%(threadName)s) %(name)s: %(message)s",
    level=logging.DEBUG if config.Client.debug else logging.INFO,
)


def _set_trace_loggers() -> None:
    """
    Set loggers to the debug level according to the value from the DEBUG_LOGGERS env var.

    When the env var is a list of logger names delimited by a comma,
    each of the listed loggers will be set to the debug level.
    """
    level_filter = config.Client.debug_loggers
    if not level_filter:
        return

    for logger_name in level_filter.split(","):
        if not logger_name:
            continue
        logging.getLogger(logger_name.strip()).setLevel(logging.DEBUG)


_set_trace_loggers()
