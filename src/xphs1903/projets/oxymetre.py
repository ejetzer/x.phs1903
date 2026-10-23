# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Définitions pertinentes pour l'oxymètre."""

import time
import serial
import matplotlib as mpl
import numpy as np
import pandas as pd

from ..outils.serial import ArduinoNanoEvery
from ..outils.calcul import fft
from ..outils.plot import FichierGraphe

def stdlib():
    ard = serial.serial_for_url("hwgrep://Arduino&skip_busy", do_not_open=True)
    ard.baudrate = 115_200
    df = pd.DataFrame()

    ard.open()
    ard.readline()
    while True:
        ligne = str(ard.readline().strip(), encoding="utf-8")
        print(ligne)
        valeurs = ligne.split('\t')
        paires = (val.split(":") for val in valeurs)
        rangée = {nom: [float(val)] for nom, val in paires}
        rangée = pd.DataFrame(rangée)
        df = pd.concat([df, rangée])

        fig = mpl.figure.Figure()
        ax_1 = fig.add_subplot(1, 2, 1)
        ax_2 = fig.add_subplot(1, 2, 2)
        df.iloc[:, [0, 1]].plot(0, 1, ax=ax_2)
        df.iloc[:, [2, 3]].plot(0, 1, ax=ax_2)

        fft_1 = np.fft.rfft(df.iloc[:, 1]).real
        fft_2 = np.fft.rfft(df.iloc[:, 3]).real
        ax_1.plot(fft_1)
        ax_1.plot(fft_2)

        fig.savefig("graphe.png")

def phslib():
    with ArduinoNanoEvery(baudrate=115_200) as ard:
        tab = FichierGraphe(ard)
        tab.register(fft)
        tab.add_subplot("fft", (1, 2, 2))
        tab.add_subplot((0, 1), (1, 2, 1))

        with tab:
            time.sleep(10)
            tab.wait()

if __name__ == '__main__':
    phslib()
