# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Exemple de communication série."""

from ....outils.clitools import argparse
from ....outils.serial import echo

if __name__ == "__main__":
    args = argparse()
    echo(debug=args.debug)
