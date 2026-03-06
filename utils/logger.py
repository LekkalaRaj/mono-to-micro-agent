"""
utils/logger.py
───────────────
Centralised structured logger.  All modules call `get_logger(__name__)`.
Format: ISO-8601 timestamp | level | [agent/module] | message
"""

from __future__ import annotations

import logging
import sys


_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Return a configured logger for the given module name.

    Args:
        name:  Typically __name__ of the calling module.
        level: Logging level (default INFO).
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger