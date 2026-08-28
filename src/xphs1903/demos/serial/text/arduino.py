# (c) Copyright 2026 Émile Jetzer. All Rights Reserved. 
"""Exemple de communication avec Arduino."""

from ....outils.clitools import argparse
from ....outils.serial import ardecho

if __name__ == "__main__":
    args = argparse()
    ardecho(debug=args.debug)
