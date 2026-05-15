# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Exemple de contrôle de micro-contrôleur."""
from xphs1903.outils.io import FilEntrée, FilSortie, Traceur
from xphs1903.outils.serie import (
    FilAppelReponse,
    FileDemandeDonnées,
    FileRéponses,
)
from xphs1903.outils.data import FileData
from xphs1904.outils import FilCopie, se_tourner_les_pouces
from matplotlib.figure import Figure


def main() -> None:
    """Démonstration."""
    ser = FilSérie()
    clavier, tty = console(intermédiaire=ser)
    traceur = Traceur(tty)

    with ser, clavier, tty:
        while True:
            traceur.màj()


if __name__ == '__main__':
    main()
