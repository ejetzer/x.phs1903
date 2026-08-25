from ....outils.serial import echo
from ....outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    echo(debug=args.debug)
