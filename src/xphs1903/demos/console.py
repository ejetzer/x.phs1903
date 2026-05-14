# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Exemple de contrôle de micro-contrôleur."""
from xphs1903.outils.io import FilEntrée, FilSortie, FilTraceur
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
    commandes = FileDemandeDonnées()
    proxy, réponses = FileRéponses(), FileRéponses()
    data, fig = FileData(), Figure()
    ax = fig.add_axes((0,0,1,1))

    ligne_serie = FilAppelReponse(commandes, proxy)
    copie = FilCopie(proxy, réponses, lambda x: x, data, lambda x: x.rep)
    entrée_clavier = FilEntrée(commandes)
    sortie_écran = FilSortie(réponses)
    sortie_traceur = FilTraceur(data, ax)

    with ligne_serie, entrée_clavier, sortie_écran, copie, sortie_traceur:
        se_tourner_les_pouces()


if __name__ == '__main__':
    main()
