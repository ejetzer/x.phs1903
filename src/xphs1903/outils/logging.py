# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
# ruff: noqa: LOG015
"""Utilitaire de journalisation pour le débogage."""

import functools
import inspect
import logging
import sys
import threading
import time
from contextlib import AbstractContextManager
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from types import TracebackType
    from typing import Any, Final, Self, TextIO

import rich.console
from rich.logging import RichHandler

from .functools import staticproperty

FMT: Final[str] = (
    "%(asctime)s:"
    "%(name)s:"
    "%(levelname)s\t"
    "%(threadName)s\t"
    "%(funcName)s (%(lineno)s)\t"
    "%(message)s"
)
"""Chaîne de formatage par défaut."""

formatter: Final[logging.Formatter] = logging.Formatter(FMT)
"""Format par défaut pour les journaux."""


class WithLogger:
    """Classe abstraite pour faciliter la journalisation."""

    @functools.cached_property
    def logger(self) -> logging.Logger:
        """Logger par défaut pour une instance."""
        cls = type(self)
        mod, cls = cls.__module__, cls.__name__
        return logging.getLogger(f"{mod}.{cls}.{id(self)}")

    # ruff ne remarque pas les staticproperty
    # alors on ignore DOC201 manuellement.
    @staticproperty
    def formatter() -> logging.Formatter:
        """Objet de formatage par défaut."""  # noqa: DOC201
        return formatter

    # ruff ne remarque pas les staticproperty
    # alors on ignore DOC201 manuellement.
    @staticproperty
    def fstring() -> str:
        """Chaîne de formatage par défaut."""  # noqa: DOC201
        return FMT

    # ruff ne remarque pas les staticproperty
    # alors on ignore DOC201 manuellement.
    @staticproperty
    def levels() -> dict[str, float]:
        """Niveaux de messages d'erreur."""  # noqa: DOC201
        return {
            "debug": DEBUG,
            "info": INFO,
            "warning": WARNING,
            "error": ERROR,
            "critical": CRITICAL,
        }

    def log(self, level: float, msg: str, *args: Any, **kargs: Any) -> None:
        """Afficher un message d'erreur."""
        kargs["stacklevel"] = kargs.get("stacklevel", 1) + 1
        self.logger.log(level, msg, *args, **kargs)

    def debug(
        self,
        msg: str,
        *args: Any,
        exc_info: BaseException | None = None,
        **kargs: Any,
    ) -> None:
        """Transmet une information de débogage.

        Devrait être utilisée pour les détails mineurs et
        précis.

        See also
        ----------------------
        logging-levels
        """
        if exc_info is not None:
            kargs["exc_info"] = exc_info

        kargs["stacklevel"] = kargs.get("stacklevel", 1) + 1
        self.log(DEBUG, msg, *args, **kargs)

    def info(
        self,
        msg: str,
        *args: Any,
        exc_info: BaseException | None = None,
        **kargs: Any,
    ) -> None:
        """Transmets une information utile.

        Devrait être utilisée pour les détails pertinents
        pour l'utilisateur.

        See also
        ----------------------
        logging-levels
        """
        if exc_info is not None:
            kargs["exc_info"] = exc_info

        kargs["stacklevel"] = kargs.get("stacklevel", 1) + 1
        self.log(INFO, msg, *args, **kargs)

    def warning(
        self,
        msg: str,
        *args: Any,
        exc_info: BaseException | None = None,
        **kargs: Any,
    ) -> None:
        """Indique un avertissement.

        Devrait être utilisée pour les erreurs nécessitant
        potentiellement une action de l'usager.

        See also
        ----------------------
        logging-levels
        """
        if exc_info is not None:
            kargs["exc_info"] = exc_info

        kargs["stacklevel"] = kargs.get("stacklevel", 1) + 1
        self.log(WARNING, msg, *args, **kargs)

    def error(
        self,
        msg: str,
        *args: Any,
        exc_info: BaseException | None = None,
        **kargs: Any,
    ) -> None:
        """Indique une erreur.

        Devrait être utilisée pour indiquer qu'une tâche n'a
        pas pu être accomplie.

        See Also
        ----------------------
        logging-levels
        """
        if exc_info is not None:
            kargs["exc_info"] = exc_info

        kargs["stacklevel"] = kargs.get("stacklevel", 1) + 1
        self.log(ERROR, msg, *args, **kargs)

    def critical(
        self,
        msg: str,
        *args: Any,
        exc_info: BaseException | None = None,
        **kargs: Any,
    ) -> None:
        """Indique une erreur critique.

        Devrait être utilisée pour les erreurs nécessitant
        de quitter le logiciel.

        See also
        ----------------------
        logging-levels
        """
        if exc_info is not None:
            kargs["exc_info"] = exc_info

        kargs["stacklevel"] = kargs.get("stacklevel", 1) + 1
        self.log(CRITICAL, msg, *args, **kargs)

    # Le nom setLevel utilise la convention motsChameaux
    # pour correspondre au module :mod:`logging`.
    def setLevel(self, level: float | str) -> None:  # noqa: N802
        """Règle le niveau d'erreurs à afficher."""
        if isinstance(level, str):
            level = self.levels[level]

        self.logger.setLevel(level)

    set_level = setLevel

    # Le nom addHandler utilise la convention motsChameaux
    # pour correspondre au module :mod:`logging`.
    def addHandler(self, handler: logging.Handler) -> None:  # noqa: N802
        """Ajoute un gérant d'erreurs."""
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    add_handler = addHandler

    def log_to_stream(self, stream: TextIO) -> None:
        """Envoie les rapports d'erreur à un flot ouvert."""
        handler = logging.StreamHandler(stream=stream)
        self.addHandler(handler)

    def log_to_file(self, path: Path) -> None:
        """Envoie les rapports d'erreur à un fichier."""
        stream = path.open(encoding="utf-8")
        self.log_to_stream(stream)

    def log_to_stderr(
        self, *, use_rich: bool = False, **kargs: bool | str | int
    ) -> None:
        """Configure la sortie d'erreur standard."""
        if not use_rich:
            self.log_to_stream(sys.stderr)
        else:
            kargs = {
                "console": rich.console.Console(stderr=True),
                "show_time": True,
                "show_level": True,
                "enable_link_path": True,
                "rich_traceback": True,
            } | kargs
            self.logger.addHandler(RichHandler(**kargs))

    def checkin(self) -> None:
        """Note l'entrée dans une fonction."""
        frame = inspect.stack()[1].frame
        name = frame.f_code.co_name
        thread = threading.current_thread().name
        self.debug("Checkin: %s starting in %s.", name, thread, stacklevel=2)


class SuppressAndLogContextManager(AbstractContextManager):
    def __init__(
        self,
        has_logger: WithLogger,
        *excs: BaseException,
        final: Callable | None = None,
    ) -> None:
        self.__excs = excs
        self.__has_logger = has_logger
        self.__final = final

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exctype: type[BaseException] | None,
        excinst: BaseException | None,
        exctb: TracebackType | None,
    ) -> bool | None:
        if self.__final is not None:
            self.__final()

        if exctype is not None and exctype not in self.__excs:
            self.__has_logger.error(
                "%s has occurred.", exctype.__name__, exc_info=excinst
            )
            return False

        if exctype is not None:
            self.__has_logger.warning(
                "%s was suppressed.", exctype.__name__, exc_info=excinst
            )
            return True

        return None


suppress = SuppressAndLogContextManager
"""Alias pour :class:`SuppressAndLogContextManager`."""


def config(
    name: str,
    *,
    level: float = WARNING,
    stream: TextIO = sys.stderr,
    use_rich: bool = False,
) -> None:
    """Configuration de base pour un Logger nommé par name."""
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(level)

    if not use_rich:
        handler = logging.StreamHandler(stream=stream)
        handler.setFormatter(formatter)
    else:
        handler = RichHandler(
            console=rich.console.Console(stderr=True), rich_tracebacks=True
        )

    logger.addHandler(handler)


# :func:`basicConfig` reprend le nom d'une fonction du module :mod:`logging`
# :func:`basic_config` est un alias disponible et favorisé.
def basic_config(level: float = WARNING, *, use_rich: bool = True) -> None:
    """Configuration de base pour un logger de module ou script."""
    frame = inspect.stack()[1].frame
    name = frame.f_globals["__name__"]
    config(name, level=level, use_rich=use_rich)


basicConfig = basic_config  # noqa: N816


def system() -> str:
    """Obtient des informations utiles sur le système.

    Returns
    ----------------------
    str
        Informations en JSON
    """
    import json  # noqa: PLC0415
    import platform  # noqa: PLC0415

    ret: dict[str, str] = {
        "platform": platform.platform(),
        "python": platform.python_implementation() + platform.python_version(),
    }

    return json.dumps(ret)


def ez_log(
    level: int,
    msg: str,
    *args: str,
    logger: str | None = None,
    exc_info: BaseException | None = None,
    **kargs: Any,
) -> None:
    if logger is None:
        # On va chercher l'information des frames supérieurs.
        kargs["stacklevel"] = kargs.get("stacklevel", 1) + 1
        frame = inspect.stack()[
            kargs["stacklevel"]
        ].frame  # On veut l'environnement de l'appel de la fonction.
        # On en assume un peu sur la structure du code
        # pour estimer un nom de module et de logger.
        name = frame.f_code.co_name

        module = frame.f_globals["__name__"]
        if frame.f_back is not None and name in frame.f_back.f_locals:
            module = frame.f_back.f_locals[name].__module__

        logger = f"{module}.{name}"

    logger = logging.getLogger(logger)
    logger.log(level, msg, *args, exc_info=exc_info, **kargs)


def debug(
    msg: str, *args: str, exc_info: BaseException | None = None, **kargs: Any
) -> None:
    """Transmet une information de débogage.

    Devrait être utilisée pour les détails mineurs et
    précis.

    See also
    ----------------------
    logging-levels
    """
    kargs["stacklevel"] = kargs.get("stacklevel", 1)
    ez_log(DEBUG, msg, *args, exc_info=exc_info, **kargs)


def info(
    msg: str, *args: str, exc_info: BaseException | None = None, **kargs: Any
) -> None:
    """Transmets une information utile.

    Devrait être utilisée pour les détails pertinents
    pour l'utilisateur.

    See also
    ----------------------
    logging-levels
    """
    kargs["stacklevel"] = kargs.get("stacklevel", 1)
    ez_log(INFO, msg, *args, exc_info=exc_info, **kargs)


def warning(
    msg: str, *args: str, exc_info: BaseException | None = None, **kargs: Any
) -> None:
    """Indique un avertissement.

    Devrait être utilisée pour les erreurs nécessitant
    potentiellement une action de l'usager.

    See also
    ----------------------
    logging-levels
    """
    kargs["stacklevel"] = kargs.get("stacklevel", 1)
    ez_log(WARNING, msg, *args, exc_info=exc_info, **kargs)


def error(
    msg: str, *args: str, exc_info: BaseException | None = None, **kargs: Any
) -> None:
    """Indique une erreur.

    Devrait être utilisée quand une fonction
    n'a pas pu être exécutée.

    See also
    ----------------------
    logging-levels
    """
    kargs["stacklevel"] = kargs.get("stacklevel", 1)
    ez_log(ERROR, msg, *args, exc_info=exc_info, **kargs)


def critical(
    msg: str, *args: str, exc_info: BaseException | None = None, **kargs: Any
) -> None:
    """Indique une erreur critique.

    Devrait être utilisée pour les erreurs nécessitant
    de quitter le logiciel.

    See also
    ----------------------
    logging-levels
    """
    kargs["stacklevel"] = kargs.get("stacklevel", 1)
    ez_log(CRITICAL, msg, *args, exc_info=exc_info, **kargs)


def profile(f: Callable) -> Callable:
    """Mesure le temps d'exécution et assure la journalisation.

    Parameters
    ----------------------
    f: Callable
        Une fonction à profiler.

    Returns
    ----------------------
    wrapped_f: Callable
        La fonction enrobée de code de profilage.
    """

    # Dans :func:`wrapped_f`, on ignore les erreurs
    # de style LOG015: root-logger-call, parce qu'il s'agit
    # de faux positifs. Les fonctions du module
    # :mod:`xphs1903.outils.logging` n'utilisent pas
    # le logger global.
    @functools.wraps(f)
    def wrapped_f(*args: Any, **kargs: Any) -> Any:  # noqa: ANN401
        log_name = f"{f.__module__}.{f.__name__}"

        debug("Début de l'exécution de %s...", f.__name__, logger=log_name)
        debut = time.time()
        try:
            res = f(*args, **kargs)
        except Exception as err:
            fin = time.time()
            temps_exec = fin - debut
            debug("%s s'est exécutée en %ss.", f.__name__, temps_exec)
            error(  # noqa: TRY400
                "Erreur dans l'exécution de %s.",
                f.__name__,
                logger=log_name,
                exc_info=err,
            )
            raise
        else:
            fin = time.time()
            temps_exec = fin - debut
            debug("%s s'est exécutée en %ss.", f.__name__, temps_exec)
            debug("%s a retourné %r.", f.__name__, res)

        return res

    return wrapped_f


__all__: Final[list[str]] = [
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "INFO",
    "WARNING",
    "WithLogger",
    "basic_config",
    "config",
    "critical",
    "debug",
    "error",
    "formatter",
    "info",
    "profile",
    "suppress",
    "system",
    "warning",
]
