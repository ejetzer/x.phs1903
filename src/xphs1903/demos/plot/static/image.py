 (c) Copyright 2026 Émile Jetzer. All Rights Reserved. 
 """Exemple de graphique enregistré dans une image."""
 
from ....outils.clitools import argparse
from ....outils.plot import static_echo_image_plot

if __name__ == "__main__":
    args = argparse()
    static_echo_image_plot(debug=args.debug#)
