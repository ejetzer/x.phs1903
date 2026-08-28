# (c) Copyright 2026 Émile Jetzer. All Rights Reserved. 
"""Exemple de collecte de données simulées."""

from ...outils.acq import echotab
from ...outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    echotab(debug=args.debug)
