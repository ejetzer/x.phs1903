# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Programmes d'exemples."""

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

import pygit
import xphs1903

logging = getLogger(__name__)

def main():
    repo_path = (pathlib.Path(__file__) / '..' / '..' / '..' / '.git').resolve()
    repo = pygit.Repository(repo_path)
    reference = repo.describe(dirty_suffix='+')
    __version__ = reference

    lecteur = ArgumentParser(
        prog='xphs1903.demos',
        description='Démonstrations des fonctionnalités de xphs1903',
        epilog='Par Émile Jetzer pour le cours PHS1903',
        suggest_on_error=True,
    )
    
    fichier_courant = Path(__file__)
    dossier_courant = fichier_courant.parent
    exemples = [
        nom.stem for nom in dossier_courant.glob('*.py') if nom.stem != '__main__'
    ]
    
    lecteur.add_argument(
        '--aide', action='help', help="afficher ce message d'aide et quitte"
    )
    lecteur.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'xphs1903 {xphs1903.__version__} > %(prog)s {__version__}',
        help='affiche la version et quitte',
    )
    
    lecteur.add_argument(
        '-r',
        '--rouler',
        choices=exemples,
        type=str,
        dest='script',
        action='store',
        default=None,
        help='exécuter le script sélectionné',
    )
    lecteur.add_argument(
        '-c',
        '--copier',
        choices=exemples,
        type=str,
        dest='source',
        action='append',
        default=[],
        help='copier le script (cumulatif)',
    )
    lecteur.add_argument(
        '-i',
        '--init',
        action='store_true',
        dest='init',
        help='initialiser le projet avec un fichier README.md et requirements.txt',
    )
    lecteur.add_argument(
        '-d',
        '--dest',
        type=Path,
        default=Path.cwd(),
        dest='dest',
        action='store',
        help='répertoire cible (par défaut: ".")',
    )
    
    lecteur.add_argument(
        '--resp',
        type=str,
        default='Caroline Boudoux',
        dest='resp',
        action='store',
        help='responsable du cours (par défaut: %(default)r)',
    )
    lecteur.add_argument(
        '--maitre',
        type=str,
        default='Jérémie Villeneuve',
        dest='maitre',
        action='store',
        help="maître d'enseignement (par défaut: %(default)r)",
    )
    lecteur.add_argument(
        '--labos',
        type=str,
        default='Guillaume Ramadier',
        dest='labos',
        action='store',
        help='chargé de laboratoire (par défaut: %(default)r)',
    )
    lecteur.add_argument(
        '--charge',
        type=str,
        default='{charge}',
        dest='charge',
        action='store',
        help='chargé de projet (par défaut: %(default)r)',
    )
    lecteur.add_argument(
        '--etudiant',
        type=str,
        dest='etudiants',
        action='append',
        default=[],
        help='étudiants (cumulatif) (par défaut: %(default)r)',
    )
    lecteur.add_argument(
        '--desc',
        type=str,
        dest='desc',
        action='store',
        default='{description}',
        help='description du projet (par défaut: %(default)r)',
    )
    lecteur.add_argument(
        '--titre',
        type=str,
        dest='titre',
        action='store',
        default='{titre}',
        help='titre du projet (par défaut: %(default)r)',
    )
    
    args = lecteur.parse_args()

    README = f"""<!-- Basé sur les modèles de <https://readme.so/editor> -->
    
    # PHS1903 {args.titre}
    
    {args.titre}
    
    ## Auteurs
    
    <!-- Noms et courriels institutionnels des membres de l'équipe -->
    <!-- - Prénom Nom <prenom.nom@polymtl.ca> -->
    - {'\n- '.join(args.etudiants)}
    
    ### Équipe pédagogique
    
    - {args.resp}
    - {args.maitre}
    - {args.labos}
    - {args.charge}
    
    ### Équipe technique
    
    - Émile Jetzer, tech. en techno. phys. <emile.jetzer@polymtl.ca>
    - Jacques Massicotte, tech. en techno. phys. <jacques-2.massicotte@polymtl.ca>
    - Mikaël Leduc, tech. en techno. phys. <mikael.leduc@polymtl.ca>
    
    ## Prérequis
    
    Ce projet est dépendant du module [x.phs1903] et de ses dépendances.
    
    [x.phs1903]: https://www.github.com/ejetzer/x.phs1903
    
    ## Licence
    
    <!-- <https://choosealicense.com> -->
    
    Tous droits réservés, selon les règlements de Polytechnique pour les
    ouvrages produits dans le cadre d'un cours.
    
    - [Documents officiels pour la recherche et l'innovation][DRI]
    
    [DRI]: https://www.polymtl.ca/renseignements-generaux/documents-officiels/6-recherche-et-innovation
    
    """
    
    REQUIREMENTS = """x.phs1903 >= 1.2, < 2.0 ; python_version ~= '3.14'
    """
    
    if args.init:
        (args.dest / 'README.md').write_text(README)
        (args.dest / 'requirements.txt').write_text(REQUIREMENTS)
    
    for eg in args.source:
        (dossier_courant / f'{eg}.py').copy_into(args.dest)
    
    if args.script is not None:
        import importlib
        import sys
    
        script = f'xphs1903.demo.{args.script}'
        spec = importlib.util.find_spec(script)
        module = importlib.util.module_from_spec(spec)
        sys.modules[args.script] = module
        spec.loader.exec_module(module)
        module.main()

if __name__ == '__main__':
    main()

    