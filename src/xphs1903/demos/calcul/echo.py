from ...outils.calcul import echocalc
from ...outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    echocalc(debug=args.debug)
