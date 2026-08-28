# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Exemple d'acquisition avec une carte Arduino."""

from ...outils.acq import ardtab
from ...outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    ardtab(debug=args.debug)
