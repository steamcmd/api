import logging
import sys


def log_level(level: str) -> int:
    """
    Sets lowest level to log.
    """

    match level:
        case "debug":
            return logging.DEBUG
        case "info":
            return logging.INFO
        case "warning":
            return logging.WARNING
        case "error":
            return logging.ERROR
        case "critical":
            return logging.CRITICAL
        case _:
            return logging.WARNING
