from logging import getLogger

from matplotlib import pyplot as plt

import sys

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)

from . import loop, setdown, setup

logging = getLogger(__name__)


def main():
    params = setup()

    try:
        # Cette boucle est infinie à toutes fins pratiques, càd équivalente à
        # while True:
        #   ...
        # Techniquement, elle s'arrête quand la fenêtre du graphique est fermée,
        # ou que l'utilisateur entre ^C sur la ligne de commande.
        while len(plt.get_fignums()) > 0:
            params = loop(*params)
    except KeyboardInterrupt:
        # Détection de la combinaison ^C pour arrêter le programme
        logging.critical("Sortie forcée par l'utilisateur.")
    except Exception:
        logging.exception("Erreur inattendue dans l'exécution du programme.")
        raise
    finally:
        # Procédures de fin
        # Ce bloc est toujours exécuté, peu importe la raison de l'arrêt
        # du programme.
        # eg: libérer le port série pour qu'il puisse être utilisé par d'autres
        # programmes.
        logging.info('Fin.')
        setdown(*params)


if __name__ == '__main__':
    main()
