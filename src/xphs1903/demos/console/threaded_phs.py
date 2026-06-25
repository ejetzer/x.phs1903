# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Exemple de contrôle de micro-contrôleur."""
from matplotlib.figure import Figure
from xphs1904.outils import FilCopie, se_tourner_les_pouces

from xphs1903.outils.data import FileData
from xphs1903.outils.io import Clavier, Console, Traceur
from xphs1903.outils.serie import (
    FilAppelReponse,
    FileDemandeDonnées,
    FileRéponses,
)


def main() -> None:
    """Démonstration."""
    # clavier | arduino | console
    arduino = ArduinoNanoEvery()
    clavier = Clavier(sortie=arduino._entrée)
    console = Console(entrée=arduino._sortie)

    with arduino, clavier, console:
        while True:
            time.sleep(0.001)


if __name__ == '__main__':
    main()
