from ....outils.serial import ardecho
from ....outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    ardecho(debug=args.debug)
