# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""Auditeur de la ligne série sur le port sélectionné."""

import logging

from serial import Serial

from xphs1903.outils import choix

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

s = Serial(baudrate=115200)
s.port = choix().device

input('Prêt?')

logger.info('--- Allez! ---')
try:
    s.open()
    while True:
        bloc = s.read_until(b'\r\n\r\n')
        print(bloc.decode('utf-8'))
except KeyboardInterrupt:
    logger.info('Arrêt par ^C.')
finally:
    s.close()
    logger.info('--- Sortie. ---')
