# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaire de journalisation pour le débogage."""

import logging
import sys
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from typing import Final, TextIO

fmt: Final[str] = (
    '%(name)s:'
    '%(levelname)s\t'
    '%(threadName)s\t'
    '%(funcName)s (%(lineno)s)\t'
    '%(message)s'
)
"""Chaîne de formatage par défaut."""

formatter: Final[logging.Formatter] = logging.Formatter(fmt)
"""Format par défaut pour les journaux."""


def config(
    name: str, *, level: float = WARNING, stream: TextIO = sys.stderr
) -> None:
    """Configuration de base pour un Logger nommé par name."""
    logger: Final[logging.Logger] = logging.getLogger(name)
    logger.setLevel(level)
    handler: Final[logging.BaseHandler] = logging.StreamHandler(stream=stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def system() -> str:
    import platform
    import json

    ret: dict[str, str] = {
        'platform': platform.platform(),
        'python': platform.python_implementation()+platform.python_version()
    }

    return json.dumps(ret)

__all__: Final[list[str]] = [
    'CRITICAL',
    'DEBUG',
    'ERROR',
    'INFO',
    'WARNING',
    'config',
    'system',
    'formatter',
]
