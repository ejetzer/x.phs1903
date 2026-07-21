# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
import logging
import tkinter as tk
import typing

import pandas as pd
import matplotlib as mpl
from matplotlib import figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .calcul import Calcul, Identite

if typing.TYPE_CHECKING:
    from concurrent.futures import Future
    from types import TracebackType
    from typing import Self, Callable

    from .acq import Tableau

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())


class Format:
    __logger = logging.getLogger(f'{__name__}.Format')
    """Journal de débogage pour les objets de classe Format."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        *,
        callback: Callable = None,
        xlim: tuple | None = None,
        ylim: tuple | None = None,
        title: str = 'Graphe',
        linestyle: str = 'dotted'
    ) -> None:
        self.__callback = None
        self.__fig = None
        self.__ax = None
        self.__bottom = None
        self.__top = None
        self.__left = None
        self.__right = None
        self.__title = title
        self.__linestyle = linestyle

        self.xlim = xlim
        self.ylim = ylim

    @property
    def xlim(self):
        if self.__ax is None:
            return self.__left, self.__right

        minimum = self.__left
        maximum = self.__right
        xss = [ligne.get_data()[0] for ligne in self.__ax.get_lines()]

        if self.__left is None:
            minimum = min(min(xs) for xs in xss)

        if self.__right is None:
            maximum = max(max(xs) for xs in xss)

        return minimum, maximum

    @xlim.setter
    def xlim(self, value):
        if value is None:
            self.__left = self.__right = None
        elif len(value) == 2:
            self.__left, self.__right = value

    @property
    def ylim(self):
        if self.__ax is None:
            return self.__bottom, self.__top

        minimum = self.__bottom
        maximum = self.__top
        yss = [ligne.get_data()[1] for ligne in self.__ax.get_lines()]

        if self.__left is None:
            minimum = min(min(ys) for ys in yss)

        if self.__right is None:
            maximum = max(max(ys) for ys in yss)

        return minimum, maximum

    @ylim.setter
    def ylim(self, value):
        if value is None:
            self.__bottom = self.__top = None
        elif len(value) == 2:
            self.__bottom, self.__top = value

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value

    def __call__(self, graphe: Graphe) -> None:
        self.__logger.debug('')
        self.__fig = graphe.fig
        self.__ax = graphe.ax

        try:
            self.__ax.set_xlim(*self.xlim)
            self.__ax.set_ylim(*self.ylim)
            self.__ax.set_title(self.title)

            if self.__callback is not None:
                self.__callback(self.__fig, self.__ax)
        finally:
            self.__fig = None
            self.__ax = None


class Graphe:
    __logger = logging.getLogger(f'{__name__}.Graphe')
    """Journal de débogage pour les objets de classe Graphe."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        root: tk.Frame,
        tab: Tableau,
        calcul: Calcul = None,
        *,
        format_: Format = None
    ) -> None:
        self.__logger.debug('')

        self.__root: tk.Frame = root
        self.__logger.debug('%s', self.__root)

        self.__tab = tab
        self.__logger.debug('%s', self.__tab)

        self.__calcul = calcul if calcul is not None else Identite()
        self.__logger.debug('%s', self.__calcul)

        self.__figure: figure.Figure = figure.Figure()
        self.__logger.debug('%s', self.__figure)
        self.__canvas = FigureCanvasTkAgg(self.__figure, master=self.__root)

        self.__axes = self.__figure.add_subplot()
        self.__logger.debug('%s', self.__axes)

        self.__lignes = []
        self.__format = format_ if isinstance(format_, Format) else Format()
        self.__pending_res = None
        self.__count = 0

    @property
    def fig(self) -> mpl.figure.Figure:
        return self.__figure

    @property
    def ax(self) -> mpl.axes.Axes:
        return self.__axes

    def close(self):
        self.__calcul.shutdown()
        self.__tab.close()

    def func(self) -> list | None:
        self.__count += 1
        self.__logger.info('#%s', self.__count)
        try:
            frame = next(self)
            self.__logger.debug('%s', type(frame))
        except StopIteration as err:
            self.__logger.info('', exc_info=err)
            return self.__lignes
        except Exception as err:
            self.__logger.warning('', exc_info=err)
            raise

        if isinstance(frame, pd.DataFrame):
            self.__logger.debug('frame.size = %s', frame.size)
            if frame.size > 0:
                items = frame.items()
                _, index = next(items)
                self.__logger.debug('index.size = %s', index.size)

                for ligne, (_, col) in zip(self.__lignes, items, strict=False):
                    self.__logger.debug('%s (%s items)', col.name, col.size)
                    self.__logger.debug('%s', ligne)

                    ligne.set_xdata(index)
                    ligne.set_ydata(col)

                for _, col in items:
                    self.__logger.debug('%s (%s items)', col.name, col.size)
                    plot = self.__axes.plot(index, col, '+-')
                    self.__lignes += plot

            self.__logger.debug('%s', self.__lignes)

        try:
            self.__format(self)
        except Exception as err:
            self.__logger.debug('', exc_info=err)
        else:
            self.__canvas.draw()
        finally:
            self.__root.after(1000, self.func)

        self.__logger.debug('%s', self.__lignes)
        return self.__lignes

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> pd.DataFrame:
        res = pd.DataFrame()

        if self.__pending_res is None:
            df: pd.DataFrame = self.__tab.df
            res: Future = self.__calcul(df)
        else:
            res = self.__pending_res
            self.__pending_res = None

        self.__logger.debug('%s', type(res))

        try:
            res: pd.DataFrame = res.result(timeout=0.01)
        except TimeoutError as err:
            self.__logger.debug('', exc_info=err)
            self.__pending_res = res
            res = pd.DataFrame()
        except Exception as err:
            self.__logger.debug('', exc_info=err)
            raise

        self.__logger.debug('%s', type(res))
        return res

    def __enter__(self) -> Self:
        self.__logger.debug('')
        self.func()
        self.__logger.debug('%s', self.__canvas)

        self.__canvas.get_tk_widget().pack(
            side=tk.TOP, fill=tk.BOTH, expand=True
        )
        return self

    @property
    def canvas(self) -> FigureCanvasTkAgg | None:
        return self.__canvas

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.close()
        self.__logger.debug('')
        return False  # Re-raise the exception please


def main(*, debug: bool = False) -> None:
    """Affiche le spectre de fréquence d'un signal artificiel."""
    from functools import partial  # noqa: PLC0415

    from .acq import Tableau, sinus  # noqa: PLC0415
    from .calcul import rectangle, FFT  # noqa: PLC0415
    from .serial import LigneSerie  # noqa: PLC0415

    if debug:
        #__parent = logging.getLogger('src.xphs1903')
        __calcul = logging.getLogger('src.xphs1903.calcul')
        __logger.setLevel(logging.DEBUG)
        __calcul.setLevel(logging.DEBUG)
        #__parent.setLevel(logging.DEBUG)
        __handler = logging.StreamHandler()
        fmt: str = (
            '%(name)s:'
            '%(levelname)s\t'
            '%(threadName)s\t'
            '%(funcName)s (%(lineno)s)\t'
            '%(message)s'
        )
        __formatter = logging.Formatter(fmt)
        __handler.setFormatter(__formatter)
        __logger.addHandler(__handler)
        __calcul.addHandler(__handler)
        #__parent.addHandler(__handler)

    __logger.debug('%s', __name__)

    lignes = sinus(n=50)

    fenetre: Calcul = rectangle(153)()
    calcul_fft: Calcul = FFT() @ fenetre

    root = tk.Tk()
    root.wm_title('Démonstration avec des données artificielles')

    format_fft = Format(
        title='Transformée de Fourier',
        xlim=(0, 0.5)
    )

    format_sig = Format(
        title='Signal artificiel'
    )

    with LigneSerie() as com:
        __logger.debug('%s', com)
        com.print(lignes)

        def nouvelles_données(n: int = 50, count: int = 0) -> None:
            lignes = sinus(n=n, phase=count)
            com.print(lignes)
            root.after(1000, partial(nouvelles_données, n=n, count=count + n))

        with Tableau(com.parse()) as tab:
            __logger.debug('%s', tab)

            with Graphe(root, tab, calcul_fft, format_=format_fft) as gra1:
                __logger.debug('%s', gra1)
                gra1.ax.set_title('Transformée de Fourier')
                gra1.ax.set_xlabel('Fréquence')
                gra1.ax.set_ylabel('Intensité (UA)')
                gra1.ax.legend(['F[x]', 'F[y]'])

                with Graphe(root, tab, fenetre, format_=format_sig) as gra2:
                    gra2.ax.set_xlabel('Temps')
                    gra2.ax.set_ylabel('Potentiel simulé')
                    gra2.ax.legend(['x', 'y'])

                    __logger.debug('%s', root)
                    root.after(1000, nouvelles_données)

                    def quit():
                        gra1.close()
                        gra2.close()
                        root.quit()

                    root.protocol('WM_DELETE_WINDOW', lambda: quit())

                    __logger.debug('%s', root)
                    root.mainloop()

    __logger.debug('Fini.')


if __name__ == '__main__':
    import sys

    debug = '--debug' in sys.argv
    main(debug=debug)
