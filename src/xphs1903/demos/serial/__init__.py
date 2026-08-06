# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Programmes de démonstration."""

from ...outils.serial import ArduinoNanoEvery


def serial() -> None:
    """Communication avec un Arduino Nano Every."""
    with ArduinoNanoEvery() as ard:
        while cmd := input('>>>'):
            ard.print(cmd)
            print(next(ard))
