# (c) Copyright 2026 Émile Jetzer. All Rights Reserved. 
"""Exemple de calculs sur des données simulées."""

from ...outils.calcul import echocalc
from ...outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    echocalc(debug=args.debug)
