from ....outils.plot import static_echo_image_plot
from ....outils.clitools import argparse

if __name__ == "__main__":
    args = argparse()
    static_echo_image_plot(debug=args.debug)
