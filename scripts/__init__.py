import logging

try:
    import coloredlogs
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
else:
    coloredlogs.install(level=logging.DEBUG)
