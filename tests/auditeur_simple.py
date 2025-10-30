from serial.tools.list_ports import comports
from serial.tools.miniterm import Miniterm, key_description
from serial import Serial
import logging

def choix():
    ports_disponibles = comports()
    for i, c in enumerate(ports_disponibles):
        print(f'[{i}]\t{c.description}\t{c.device}')
    
    sélection = input('Quel port?')
    if sélection.isdigit() and int(sélection) in range(len(ports_disponibles)):
        return ports_disponibles[int(sélection)]
    else:
        raise ValueError('Choix invalide.')

if __name__ == '__main__':
    s = Serial(baudrate=1000000)
    s.port = choix().device
    s.open()
    m = Miniterm(s, echo=False, eol='lf', filters=[])
    m.exit_character = '\x1d'
    m.menu_character = '\x14'
    m.raw = False
    m.set_rx_encoding('UTF-8')
    m.set_tx_encoding('UTF-8')
    
    logging.basicConfig(level=logging.INFO)
    
    logging.info(f'--- Miniterm sur {m.serial.name}, {m.serial.bytesize}, {m.serial.parity}, {m.serial.stopbits} ---')
    logging.info(f'--- Quitter: {key_description(m.exit_character)} | Menu: {key_description(m.menu_character)} | Aide: {key_description(m.menu_character)} {key_description("\x08")}')
    input('Prêt?')
    
    m.start()
    try:
        m.join(True)
    except KeyboardInterrupt:
        logging.info('Arrêt par ^C.')
    finally:
        logging.info('--- Sortie. ---')
        m.join()
        m.close()