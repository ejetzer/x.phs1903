from ...outils.acq import ardtab
from ...outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    ardtab(debug=args.debug)
