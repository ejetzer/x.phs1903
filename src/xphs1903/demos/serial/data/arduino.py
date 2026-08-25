from ....outils.serial import arddata
from ....outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    arddata(debug=args.debug)
