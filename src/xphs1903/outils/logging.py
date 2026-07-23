import sys
import logging
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL

fmt: str = (
    '%(name)s:'
    '%(levelname)s\t'
    '%(threadName)s\t'
    '%(funcName)s (%(lineno)s)\t'
    '%(message)s'
)
formatter = logging.Formatter(fmt)

def config(name: str, *, level=WARNING, stream=sys.stderr) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(stream=stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

__all__ = [
    'formatter',
    'INFO',
    'WARNING',
    'DEBUG',
    'ERROR',
    'CRITICAL',
    'config'
]
