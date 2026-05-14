# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Fonctionnalités de base."""

# Activer la journalisation
import logging
from threading import Thread
from queue import Queue

logging.getLogger(__name__).addHandler(logging.NullHandler())

def paires(x: iter, n: int = 2):
    """Retourne des tranches de x de taille n.

    # Source - https://stackoverflow.com/a/1335618
    # Posted by Nadia Alramli, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-05-14, License - CC BY-SA 2.5

    list_of_slices = zip(*(iter(the_list),) * slice_size)

    """
    yield from zip( *(iter(x),) * n)

def se_tourner_les_pouces():
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

class FilCopie(Thread):

    def __init__(self, orig: Queue, *args: Queue | Callable):
        self.orig = orig
        self.args = args
        super().__init__()

    def shutdown(self):
        for q, conv in paires(self.args):
            q.shutdown()
        super().shutdown()

    def join(self):
        for q, conv in paires(self.args):
            q.join()
        super().join()

    def run(self):
        while True:
            try:
                x = self.orig.get()

                for q, conv in paires(self.args):
                     q.put(conv(x))
                self.orig.task_done()
            except ShutDown:
                self.shutdown()
                break
