# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Exemple de contrôle de micro-contrôleur."""
from matplotlib.figure import Figure
from xphs1904.outils import FilCopie, se_tourner_les_pouces

from xphs1903.outils.data import FileData
from xphs1903.outils.io import FilEntrée, FilSortie, Traceur
from xphs1903.outils.serie import (
    FilAppelReponse,
    FileDemandeDonnées,
    FileRéponses,
)


def main() -> None:
    """Démonstration."""
    arduino, clavier, tty = console(ArduinoNanoEvery)
    traceur = Traceur(tty)

    with arduino, clavier, tty:
        while True:
            traceur.màj()


if __name__ == '__main__':
    main()
