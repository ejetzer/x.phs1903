# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Exemple de données simulées"""

from ...outils.dummy import signal as dummy_signal
from ...outils.clitools import argparse
from ...outils.logging import basicConfig, DEBUG

def signal(*, debug: bool = False):
    if debug:
        basicConfig(DEBUG)

    dummy_signal()

if __name__ == "__main__":
    args = argparse()
    signal(debug=args.debug)
