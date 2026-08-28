# (c) Copyright 2026 Émile Jetzer. All Rights Reserved. 
"""Exemple de fonctionnement de communication série pour la lecture de données."""

from ....outils.clitools import argparse
from ....outils.serial import echodata

if __name__ == "__main__":
    args = argparse()
    echodata(debug=args.debug)
