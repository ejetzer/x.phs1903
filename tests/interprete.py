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
    s = Serial(baudrate=115200)
    s.port = choix().device
    
    logging.basicConfig(level=logging.INFO)
    
    input('Prêt?')
    
    logging.info('--- Allez! ---')
    try:
        s.open()
        while True:
            bloc = s.read_until(b'\r\n\r\n')
            print(bloc.decode('utf-8'))
    except KeyboardInterrupt:
        logging.info('Arrêt par ^C.')
    finally:
        s.close()
        logging.info('--- Sortie. ---')