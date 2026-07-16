import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from concurrent.futures import Future
import tkinter

from .calcul import Calcul, Identite
from .acq import Tableau

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())

class Graphe:
    __logger = logging.getLogger(f'{__name__}.Calcul')
    """Journal de débogage pour les objets de classe Calcul."""

    __logger.addHandler(logging.NullHandler())

    def __init__(self, root: tkinter.Frame, tab: Tableau, calcul: Calcul = None):
        self.__logger.debug('')

        self.__root: tkinter.Frame = root
        self.__logger.debug('%s', self.__root)

        self.__tab = tab
        self.__logger.debug('%s', self.__tab)

        self.__calcul = calcul if calcul is not None else Identite()
        self.__logger.debug('%s', self.__calcul)

        self.__figure = mpl.figure.Figure()
        self.__logger.debug('%s', self.__figure)

        self.__axes = self.__figure.add_axes((0, 0, 1, 1))
        self.__logger.debug('%s', self.__axes)

        self.__lignes = []

    @property
    def fig(self):
        return self.__figure

    @property
    def ax(self):
        return self.__axes

    def init_func(self, *args, **kargs) -> list:
        self.__logger.debug('')
        frame: pd.DataFrame = next(self)
        self.__logger.debug('\n%s', frame)

        items = frame.items()
        _, index = next(items)
        self.__logger.debug('\n%s', index)

        for _, col in items:
            self.__logger.debug('\n%s', col)
            plot = self.__axes.plot(index, col)
            self.__logger.debug('%s', plot)
            self.__lignes += plot

        self.__logger.debug('%s', self.__lignes)
        return self.__lignes

    def func(self) -> list:
        try:
            frame = next(self)
        except StopIteration:
            return

        self.__logger.debug('%s', frame)
        items = frame.items()
        _, index = next(items)
        self.__logger.debug('%s', index)

        for ligne, (_, col) in zip(self.__lignes, items):
            self.__logger.debug('%s', ligne)
            ligne.set_xdata(index)
            ligne.set_ydata(col)

        self.__canvas.draw()
        self.__root.after(1000, self.func)

        self.__logger.debug('%s', self.__lignes)
        return self.__lignes

    def __iter__(self):
        return self

    def __next__(self) -> pd.DataFrame:
        df: pd.DataFrame = self.__tab.df
        res: Future = self.__calcul(df)
        self.__logger.debug('%s', res)
        res: pd.DataFrame = res.result()
        self.__logger.debug('\n%s', res)
        return res

    def __enter__(self) -> Self:
        self.__logger.debug('')
        self.init_func()

        self.__canvas = FigureCanvasTkAgg(self.__figure, master=self.__root)
        self.__logger.debug('%s', self.__canvas)

        self.__root.after(1000, self.func)
        #self.__logger.debug('%s', self.__animation)

        self.__canvas.draw()
        self.__canvas.get_tk_widget().pack(
            side=tkinter.TOP,
            fill=tkinter.BOTH,
            expand=True
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.__logger.debug('')
        return False


def main(*, debug: bool = False):
    from .serial import LigneSerie
    from .acq import Tableau, aléatoire, sinus
    from .calcul import Calcul, Moyenne, Derivee, FFT
    import numpy as np
    import sys
    from functools import partial

    if debug:
        __logger.setLevel(logging.DEBUG)
        __handler = logging.StreamHandler()
        fmt: str = (
            '%(levelname)s\t'
            '%(threadName)s\t'
            '%(funcName)s (%(lineno)s)\t'
            '%(message)s'
        )
        __formatter = logging.Formatter(fmt)
        __handler.setFormatter(__formatter)
        __logger.addHandler(__handler)

    __logger.debug('%s', __name__)

    lignes = sinus(N=50)

    calcul_der: Calcul = Derivee()
    calcul_vel: Calcul = calcul_der
    calcul_acc: Calcul = calcul_der @ calcul_der
    calcul_moy: Calcul = Moyenne()
    calcul_vel_moy: Calcul = calcul_moy @ calcul_vel
    calcul_acc_moy: Calcul = calcul_moy @ calcul_acc
    calcul_fft: Calcul = FFT()

    root = tkinter.Tk()

    with LigneSerie() as com:
        __logger.debug('%s', com)
        com.print(lignes)

        def nouvelles_données(N: int = 50, count: int = 0):
            lignes = sinus(N=N, phase=count)
            com.print(lignes)
            root.after(3000, partial(nouvelles_données, N=N, count=count+N))

        with Tableau(com.parse()) as tab:
            __logger.debug('%s', tab)

            with Graphe(root, tab, calcul_fft):
                root.after(1000, nouvelles_données)
                root.mainloop()
                raise KeyboardInterrupt



    __logger.debug('Fini.')


if __name__ == '__main__':
    main(debug=False)
