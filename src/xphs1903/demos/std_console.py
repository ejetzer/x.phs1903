import logging
import time
from queue import Empty, Queue, ShutDown
from threading import Thread

import numpy
from matplotlib import pyplot as plt
from serial import Serial

logging.basicConfig(level=logging.ERROR)

PORT = '/dev/cu.usbmodemFA13101'
FIGNAME = 'test_fig.pdf'

commandes = Queue()
proxy = Queue()
réponses = Queue()
data = Queue()

files = [commandes, proxy, réponses, data]

ser = Serial(PORT, 115_200)
plt.ion()
ligne1, *_ = plt.plot([], [])
ligne2, *_ = plt.plot([], [])
plt.ylim(0, 5000)
plt.xlim(auto=True)
plt.show()
plt.pause(0.001)


def serie(commandes, ser, proxy):
    while True:
        try:
            com = commandes.get(timeout=0.01)
        except ShutDown:
            proxy.shutdown()
            ser.close()
            break
        except Empty:
            if ser.in_waiting:
                rep = str(ser.readline(), encoding='utf-8')
                try:
                    proxy.put(rep)
                except ShutDown:
                    ser.close()
                    break
        else:
            ser.write(bytes(com, encoding='utf-8'))
            commandes.task_done()
        time.sleep(0.001)


def parse(x):
    cols = x.split()
    vals = [int(c.split(':')[1]) for c in cols]
    return vals


def copie(proxy, réponses, data):
    while True:
        try:
            x = proxy.get()
        except ShutDown:
            réponses.shutdown()
            data.shutdown()
            break
        else:
            réponses.put(x)
            try:
                x = parse(x)
            except Exception:
                continue
            else:
                data.put(x)
            finally:
                proxy.task_done()
        time.sleep(0.001)


def clavier(commandes):
    while True:
        com = input('>>>')

        try:
            commandes.put(com)
        except ShutDown:
            break
        time.sleep(0.001)


def sortie(réponses):
    while True:
        try:
            rep = réponses.get().strip()
        except ShutDown:
            break
        else:
            print(rep)
            réponses.task_done()
        time.sleep(0.001)


fs = (serie, copie, clavier, sortie)
fils = [
    Thread(target=serie, args=(commandes, ser, proxy)),
    Thread(target=copie, args=(proxy, réponses, data)),
#    Thread(target=clavier, args=(commandes,), daemon=True),
    Thread(target=sortie, args=(réponses,), daemon=True),
]

for fil in fils:
    fil.start()

while all(fil.is_alive() for fil in fils):
    try:
        ds = data.get()
        logging.info('ds = %s', ds)
        logging.info('xdata = %s', ligne1.get_xdata())
        logging.info('ydata = %s', ligne1.get_ydata())
        logging.info('xdata = %s', ligne2.get_xdata())
        logging.info('ydata = %s', ligne2.get_ydata())
        ligne1.set_xdata(numpy.append(ligne1.get_xdata(), ds[0]))
        ligne1.set_ydata(numpy.append(ligne1.get_ydata(), ds[1]))
        ligne2.set_xdata(numpy.append(ligne2.get_xdata(), ds[0]))
        ligne2.set_ydata(numpy.append(ligne2.get_ydata(), ds[2]))
        data.task_done()
        plt.xlim(0, ds[0])
        plt.pause(0.001)
        time.sleep(0.001)
    except KeyboardInterrupt:
        commandes.shutdown()
        proxy.shutdown()
        réponses.shutdown()
        data.shutdown()
        break
    except ShutDown:
        break

for f in files:
    f.shutdown()

for f in fils:
    f.join(timeout=1)
