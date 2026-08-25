from ...outils.calcul import ardcalc
from ...outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    ardcalc(debug=args.debug)
