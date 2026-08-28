# (c) Copyright 2026 Émile Jetzer. All Rights Reserved. 
"""Exemple de calculs sur des données prises avec un Arduino."""

from ...outils.calcul import ardcalc
from ...outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    ardcalc(debug=args.debug)
