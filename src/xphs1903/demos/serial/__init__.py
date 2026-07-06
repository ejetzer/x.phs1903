# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Programmes de démonstration."""

from ...outils.serial import ArduinoNanoEvery

def serial():
    with ArduinoNanoEvery() as arduino:
        while ( cmd := input('>>>') ):
            print(cmd, file=arduino)
            print(arduino.read())

