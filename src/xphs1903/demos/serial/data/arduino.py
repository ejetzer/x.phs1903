# (c) Copyright 2026 Émile Jetzer. All Rights Reserved. 
"""Exemple de collecte de données d'une carte Arduino."""

from ....outils.clitools import argparse
from ....outils.serial import arddata

if __name__ == "__main__":
    args = argparse()
    arddata(debug=args.debug)
