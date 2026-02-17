# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""Console de communication très simple."""

import logging

from serial import Serial  # noqa: PLC0415
from serial.tools.miniterm import (  # noqa: PLC0415
    Miniterm,
    key_description,
)

from xphs1903.outils import choix

logger = logging.getLogger(__name__)

s = Serial(baudrate=115200)
s.port = choix().device
s.open()
m = Miniterm(s, echo=False, eol='lf', filters=[])
m.exit_character = '\x1d'
m.menu_character = '\x14'
m.raw = False
m.set_rx_encoding('UTF-8')
m.set_tx_encoding('UTF-8')

logging.basicConfig(level=logging.INFO)

ligne_info = '--- Miniterm sur {}, {}, {}'
logger.info(
    ligne_info.format(
        m.serial.name,
        m.serial.parity,
        m.serial.stopbits,
    )
)
ligne_info = '--- Quitter: {} | Menu: {} | Aide: {} {}'
logger.info(
    ligne_info.format(
        key_description(m.exit_character),
        key_description(m.menu_character),
        key_description(m.menu_character),
        key_description('\x08'),
    )
)
input('Prêt?')

m.start()
try:
    m.join(transmit_only=True)
except KeyboardInterrupt:
    logger.info('Arrêt par ^C.')
finally:
    logger.info('--- Sortie. ---')
    m.join()
    m.close()
