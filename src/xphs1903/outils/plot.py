# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de dessin de graphiques."""

import inspect
import logging
import tkinter as tk
import time
import typing
import threading
from pathlib import Path

import matplotlib as mpl
import pandas as pd
from matplotlib import figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .acq import Tableau
from .calcul import Calcul, Identite

if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from concurrent.futures import Future
    from types import TracebackType
    from typing import Any, Self


__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())


class WrongBoundaryTypeError(TypeError):
    """Indique que les limites d'axes sont invalides."""

    def __init__(self, value: Any) -> None:  # noqa: ANN401
        """Définit le message d'erreur selon value."""
        msg: str = f"{value=} n'est pas une limite adéquate."
        super().__init__(msg)


DIM_GRA: int = 2
"""Nombre de dimensions des graphiques décrits par Graphe et Format."""

N_COTES: int = 2
"""Nombre de valeurs des limites de chaque axe."""


class Format:
    """Paramètres d'un Graphe."""

    AXES_SET: Final[tuple[str]] = (
        'xlim',
        'ylim',
        'title'
    )

    LINE_SET: Final[tuple[str]] = (
        'linestyle',
        'marker',
    )

    LINESTYLES: Final[tuple[str]] = (
        '',  # Vide
        '-',  # Solide
        ':',  # Pointillé
        '--',  # Tirets
        '-.'  # Point-tirets
    )

    MARKERS: Final[tuple[str]] = (
        '',  # Vide
        '.',  # Point
        ',',  # Pixel
        '1',  # Étoile à trois branches
        '+',  # Croix
        'x',  # Croix oblique
        '|',  # Ligne verticale
        '_'  # Ligne horizontale
    )

    __logger = logging.getLogger(f'{__name__}.Format')
    """Journal de débogage pour les objets de classe Format."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        *,
        callback: Callable | None = None,
        xlim: tuple | None = None,
        ylim: tuple | None = None,
        title: str = 'Graphe',
        linestyle: str = ':',
        marker: str = '+',
        legend: tuple[str] | None = None,
        **kargs
    ) -> None:
        """Initialisation des paramètres."""
        self.__callback = callback
        self.__fig, self.__ax = None, None
        self.__loquet: threading.Lock = threading.Lock()

        self.__kargs = kargs
        self.__bottom = None
        self.__top = None
        self.__left = None
        self.__right = None

        self.title = title
        self.xlim = xlim
        self.ylim = ylim
        self.linestyle = linestyle
        self.marker = marker

        self.__legend = tuple()
        if legend is not None:
            self.legend = legend

    @property
    def legend(self) -> tuple[str]:
        if self.ax is None:
            return tuple(self.__legend)

        h, l = self.ax.get_legend_handles_labels()
        if len(h) > 0 and len(l) == len(h):
            self.__legend = tuple(l)

        if self.__legend is None:
            self.__legend = tuple()

        return self.__legend

    @legend.setter
    def legend(self, val: tuple[str] | None) -> None:
        val = tuple(val)
        if not all(isinstance(v, str) for v in val):
            raise TypeError

        if len(self.__legend) > 0 and len(val) != len(self.__legend):
            raise ValueError

        self.__legend = val

    @property
    def title(self) -> str:
        if callable(self.__title):
            return str(self.__title(self))
        else:
            return str(self.__title)

    @title.setter
    def title(self, val: str | Callable) -> None:
        if callable(val):
            sig = inspect.signature(val)
            args = sig.parameters

            if len(args) != 1:
                raise ValueError

            self.__title = val
        else:
            self.__title = str(val)

    @property
    def xlim(self) -> tuple[float, float]:
        """Calcule les limites en x."""
        if self.__ax is None:
            return self.__left, self.__right

        minimum = self.__left
        maximum = self.__right
        xss = [ligne.get_data()[0] for ligne in self.__ax.get_lines()]

        if len(xss) == 0 or any(len(xs) == 0 for xs in xss):
            return 0, 1

        if self.__left is None:
            minimum = min(min(xs) for xs in xss) - 1

        if self.__right is None:
            maximum = max(max(xs) for xs in xss) + 1

        return minimum, maximum

    @xlim.setter
    def xlim(self, value: tuple[float, float] | None) -> None:
        """Valide les limites en x.

        Raises
        -----------------
        WrongBoundaryTypeError
            Si value n'est pas un tuple de deux éléments ou None.
        """
        if value is None:
            self.__left = self.__right = None
        elif len(value) == N_COTES:
            self.__left, self.__right = value
        else:
            raise WrongBoundaryTypeError(value)

    @xlim.deleter
    def xlim(self) -> None:
        self.__left = self.__right = None

    @property
    def ylim(self) -> tuple[float, float]:
        """Calcule les limites en y."""
        if self.__ax is None:
            return self.__bottom, self.__top

        minimum = self.__bottom
        maximum = self.__top
        yss = [ligne.get_data()[1] for ligne in self.__ax.get_lines()]

        if len(yss) == 0 or any(len(ys) == 0 for ys in yss):
            return 0, 1

        if self.__left is None:
            minimum = min(min(ys) for ys in yss) - 1

        if self.__right is None:
            maximum = max(max(ys) for ys in yss) + 1

        return minimum, maximum

    @ylim.setter
    def ylim(self, value: tuple[float, float] | None) -> None:
        """Valide les limites en y.

        Raises
        -----------------
        WrongBoundaryTypeError
            Si value n'est pas un tuple de deux éléments ou None.
        """
        if value is None:
            self.__bottom = self.__top = None
        elif len(value) == N_COTES:
            self.__bottom, self.__top = value
        else:
            raise WrongBoundaryTypeError(value)

    @ylim.deleter
    def ylim(self) -> None:
        self.__bottom = self.__top = None

    @property
    def callback(self) -> Callable:
        return self.__callback

    @callback.setter
    def callback(self, val: Callable) -> None:
        if not callable(val):
            raise TypeError

        sig = inspect.signature(sig)
        args = sig.parameters

        if len(args) != 1:
            raise ValueError

        self.__callback = val

    @callback.deleter
    def callback(self) -> None:
        self.__callback = None

    @property
    def linestyle(self) -> str:
        return self.__kargs.get('linestyle', '-')

    @linestyle.setter
    def linestyle(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError

        if val not in self.LINESTYLES:
            raise ValueError

        self.__kargs['linestyle'] = val

    @property
    def marker(self) -> str:
        return self.__kargs.get('marker', '.')

    @marker.setter
    def marker(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError

        if val not in self.MARKERS:
            raise ValueError

        self.__kargs['marker'] = val


    def __enter__(self) -> Self:
        self.__loquet.acquire()
        return self

    def __exit__(self, *exc) -> bool:
        del self.fig, self.ax
        self.__loquet.release()
        return False

    @property
    def fig(self) -> mpl.figure.Figure:
        return self.__fig

    @fig.setter
    def fig(self, val: mpl.figure.Figure) -> None:
        if isinstance(val, mpl.figure.Figure):
            self.__fig = val
        else:
            raise TypeError

    @fig.deleter
    def fig(self) -> None:
        self.__fig = None

    @property
    def ax(self) -> mpl.axes.Axes:
        return self.__ax

    @ax.setter
    def ax(self, val: mpl.axes.Axes) -> None:
        if isinstance(val, mpl.axes.Axes):
            self.__ax = val
        else:
            raise TypeError

    @ax.deleter
    def ax(self) -> None:
        self.__ax = None

    @property
    def lines(self) -> list[Line2D]:
        return self.ax.get_lines()

    def __call__(self, graphe: Graphe) -> None:
        """Applique le format à l'argument graphe."""
        self.__logger.debug('')

        with self:
            self.fig, self.ax = graphe.fig, graphe.ax

            self.ax.set_xlim(*self.xlim)
            self.ax.set_ylim(*self.ylim)
            self.ax.set_title(self.title)

            for arg, val in self.__kargs.items():
                if arg in self.AXES_SET:
                    getattr(self.ax, f'set_{arg}')(gettatr(self, arg))

                if arg in self.LINE_SET:
                    for line in self.lines:
                        getattr(line, f'set_{arg}')(getattr(self, arg))

            self.ax.legend(self.lines, self.legend)

            if self.callback is not None:
                self.callback(self)

    def __ior__(self, other: dict[str, Any]) -> Self:
        self.__kargs |= other
        return self

class BaseGraphe:
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    __logger = logging.getLogger(f'{__name__}.BaseGraphe')
    """Journal de débogage pour les objets de classe TkGraphe."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        tab: Tableau,
        calcul: Calcul = None,
        fmt: Format | None = None
    ) -> None:
        self.tab = tab
        self.calcul = calcul
        self.format = fmt
        self.__fig = mpl.figure.Figure()
        self.__ax = self.fig.add_subplot()
        self.__res, self.__pending_res = None, None
        self.__count = 0

    @property
    def fig(self) -> mpl.figure.Figure:
        return self.__fig

    @property
    def ax(self) -> mpl.axes.Axes:
        return self.__ax

    @property
    def tab(self) -> Tableau:
        return self.__tab

    @tab.setter
    def tab(self, val: Tableau) -> None:
        if isinstance(val, Tableau):
            self.__tab = val
        else:
            raise TypeError

    @property
    def df(self) -> pd.DataFrame:
        return self.tab.df

    @property
    def calcul(self) -> Calcul:
        if self.__calcul is None:
            return Identité()
        else:
            return self.__calcul

    @calcul.setter
    def calcul(self, val: Calcul) -> None:
        if isinstance(val, Calcul) or val is None:
            self.__calcul = val
        else:
            raise TypeError

    @calcul.deleter
    def calcul(self) -> None:
        self.__calcul = None

    @property
    def format(self) -> Callable:

        def null(**kargs) -> None:
            pass

        if self.__format is None:
            return null

        def proxy(**kargs) -> None:
            if self.__format is not None:
                self.__format |= kargs
                self.__format(self)

        return proxy

    @format.setter
    def format(self, val: Format) -> None:
        if isinstance(val, Format) or val is None:
            self.__format = val
        else:
            raise TypeError

    def close(self) -> None:
        self.tab.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc) -> bool:
        self.close()
        return False

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> None:
        """Retourne le prochain ensemble de données.

        Returns
        -----------------
        res: pandas.DataFrame
            Les dernières données obtenues.
        """
        if self.__res is None:
            self.__res = pd.DataFrame()

        old_res = self.__res

        if self.__pending_res is None:
            try:
                res: Future = self.calcul(self.tab)
            except:
                raise StopIteration
        else:
            res = self.__pending_res
            self.__pending_res = None

        try:
            res: pd.DataFrame = res.result(timeout=0.1)
        except TimeoutError as err:
            self.__logger.debug('', exc_info=err)
            self.__pending_res = res
            res = old_res
        except Exception as err:
            self.__logger.debug('', exc_info=err)
            raise
        else:
            self.plot(res)
            self.__count += 1

        self.__logger.debug('%s', type(res))
        self.__res = res
        return res

    @property
    def lines(self) -> list[mpl.artist.Line2D]:
        return self.ax.get_lines()

    def plot(self, df: pandas.DataFrame) -> None:
        if df.size == 0:
            return

        items = df.items()
        _, index = next(items)
        ys = [y for _, y in items]

        if self.__count == 0:
            for y in ys:
                self.ax.plot(index, y)

        for ligne, y in zip(self.lines, ys):
            ligne.set(xdata=index, ydata=y)

        self.format()

    def savefig(self, nom: pathlib.Path) -> None:
        self.fig.savefig(str(nom))

class CanvasGraphe(BaseGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    __logger = logging.getLogger(f'{__name__}.CanvasGraphe')
    """Journal de débogage pour les objets de classe TkGraphe."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        tab: Tableau,
        calcul: Calcul | None = None,
        format: Format | None = None,
        CanvasClass: type[FigureCanvasAgg] = FigureCanvasAgg,
        **kargs,
    ) -> None:
        super().__init__(tab, calcul, format)
        self.__canvas = None

        self.canvas = CanvasClass(self.fig, **kargs)

    @property
    def canvas(self) -> FigureCanvasAgg:
        return self.__canvas

    @canvas.setter
    def canvas(self, val: FigureCanvasAgg) -> None:
        if not isinstance(val, FigureCanvasAgg):
            raise TypeError

        if self.__canvas is not None:
            raise RuntimeError

        self.__canvas = val

    def update(self) -> None:
        next(self)
        self.draw()

    def draw(self):
        self.canvas.draw()

    def __enter__(self) -> Self:
        super().__enter__()
        return self


class InlineGraphe(CanvasGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    __logger = logging.getLogger(f'{__name__}.InlineGraphe')
    """Journal de débogage pour les objets de classe TkGraphe."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        tab: Tableau,
        calcul: Calcul | None,
        format: Format | None
    ) -> None:
        super().__init__(tab, calcul, format, FigureCanvasAgg)

class FichierGraphe(CanvasGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    __logger = logging.getLogger(f'{__name__}.InlineGraphe')
    """Journal de débogage pour les objets de classe TkGraphe."""

    __logger.addHandler(logging.NullHandler())

    @typing.override
    def __init__(
        self,
        name: pathlib.Path | str,
        tab: Tableau,
        calcul: Calcul | None,
        format: Format | None
    ) -> None:
        super().__init__(tab, calcul, format, FigureCanvasAgg)
        self.__name = Path(name)
        self.__thread = threading.Thread(target=self.__run)
        self.__loquet = threading.Lock()
        self.__arret = threading.Event()

    @property
    def name(self) -> str:
        return str(self.__name.resolve())

    def __run(self) -> None:
        """Lit les nouvelles données."""
        for l in self:
            if self.__arret.is_set():
                break

            with self.__loquet:
                self.savefig(self.name)

            time.sleep(0.1)

    def stop(self) -> None:
        self.__arret.set()

    def join(self):
        self.__thread.join()

    def __enter__(self) -> Self:
        super().__enter__()
        self.__thread.start()
        return self

    def __exit__(self, *exc) -> bool:
        self.__arret.set()
        self.__thread.join()
        super().__exit__()


class TkGraphe(CanvasGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    __logger = logging.getLogger(f'{__name__}.TkGraphe')
    """Journal de débogage pour les objets de classe TkGraphe."""

    __logger.addHandler(logging.NullHandler())

    @typing.override
    def __init__(
        self,
        root: tk.Frame,
        tab: Tableau,
        calcul: Calcul | None = None,
        format: Format | None = None,
    ) -> None:
        """Initialise le graphe."""
        self.__logger.debug('')
        super().__init__(tab, calcul, format, FigureCanvasTkAgg, master=root)
        self.__root: tk.Frame = root

    def close(self) -> None:
        """Ferme les connexions et détruit les composants gui."""
        super().close()
        self.widget.destroy()

    def update(self):
        super().update()
        self.widget.after(1000, self.update)

    def show(self) -> None:
        """Affiche le graphique."""
        self.draw()
        self.widget.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True
        )
        self.widget.after(1000, self.update)

    @property
    def widget(self) -> FigureCanvasTkAgg:
        return self.canvas.get_tk_widget()



def main(*, debug: bool = False) -> None:
    """Affiche le spectre de fréquence d'un signal artificiel."""
    import time

    from functools import partial  # noqa: PLC0415

    from .acq import Tableau, sinus  # noqa: PLC0415
    from .calcul import FFT, rectangle  # noqa: PLC0415
    from .serial import LigneSerie  # noqa: PLC0415

    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    lignes = sinus(n=160)

    fenetre: Calcul = rectangle(153)()
    calcul_fft: Calcul = FFT() @ fenetre

    format_fft = Format(
        title='Transformée de Fourier',
        xlim=(0, 0.5),
        ylim=None,
        xlabel='Fréquence',
        ylabel='Intensité',
        linestyle='-',
        marker='',
        legend=['F[x]', 'F[y]']
    )

    with LigneSerie() as com:
        __logger.debug('%s', com)
        com.print(lignes)

        with Tableau(com.parse()) as tab:
            __logger.debug('%s', tab)

            with FichierGraphe('gra1.png', tab, calcul_fft, format=format_fft) as gra1:
                __logger.debug('%s', gra1)

                while (a := input('?')):
                    com.print(lignes)

                com.close()

                __logger.debug('Fini')

            __logger.debug('Fini')

        __logger.debug('Fini')

    __logger.debug('Fini.')



if __name__ == '__main__':
    import sys

    debug = '--debug' in sys.argv
    main(debug=debug)
