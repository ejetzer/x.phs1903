# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Exemple de contrôle de micro-contrôleur."""
from xphs1903.outils.io import FilEntrée, FilSortie
from xphs1903.outils.serie import (
    FilAppelReponse,
    FileDemandeDonnées,
    FileRéponses,
)


def main() -> None:
    """Démonstration."""
    commandes = FileDemandeDonnées()
    réponses = FileRéponses()
    ligne_serie = FilAppelReponse(commandes, réponses)
    entrée_clavier = FilEntrée(commandes)
    sortie_écran = FilSortie(réponses)

    with ligne_serie, entrée_clavier, sortie_écran:
        while True:
            time.sleep(1)


if __name__ == '__main__':
    main()
