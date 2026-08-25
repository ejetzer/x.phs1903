from ....outils.serial import echodata
from ....outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    echodata(debug=args.debug)
