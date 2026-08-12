# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de dessin de graphiques."""

import inspect
import logging
import tkinter as tk
import typing

import matplotlib as mpl
import pandas as pd
from matplotlib import figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .calcul import Calcul, Identite

if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from concurrent.futures import Future
    from types import TracebackType
    from typing import Any, Self

    from .acq import Tableau

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
        linestyle: str = 'dotted',
        **kargs
    ) -> None:
        """Initialisation des paramètres."""
        self.__callback = callback
        self.__fig, self.__ax = None, None
        self.__loquet: threading.Lock = threading.Lock()

        self.__kargs = {
            'linestyle': linestyle
        } | kargs
        self.__bottom = None
        self.__top = None
        self.__left = None
        self.__right = None

        self.title = title
        self.xlim = xlim
        self.ylim = ylim

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

    def __call__(self, graphe: Graphe) -> None:
        """Applique le format à l'argument graphe."""
        self.__logger.debug('')


        with self:
            self.fig, self.ax = graphe.fig, graphe.ax

            self.ax.set_xlim(*self.xlim)
            self.ax.set_ylim(*self.ylim)
            self.ax.set_title(self.title)

            self.ax.set(**self.__kargs)

            if self.callback is not None:
                self.callback(self)

    def __ior__(self, other: dict[str, Any]) -> None:
        self.__kargs |= other

class BaseGraphe:

    def __init__(
        self,
        tab: Tableau,
        calcul: Calcul = None,
        format: Format | None = None
    ) -> None:
        self.tab = tab
        self.calcul = calcul
        self.format = format
        self.__fig = mpl.figure.Figure()
        self.__ax = self.__fig.add_subplot()
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
            self.__format |= kargs
            self.__format(self)

        return proxy

    @format.setter
    def format(self, val: Format) -> None:
        if isinstance(val, Format) or val is None:
            self.__format = val
        else:
            raise TypeError

    @format.deleter
    def format(self) -> None:
        self.__format = None

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
            res: Future = self.calcul(self.tab)
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

class TkGraphe(BaseGraphe):
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
        super().__init__(tab, calcul, format)

        self.__root: tk.Frame = root
        self.__logger.debug('%s', self.__root)

        self.__canvas = FigureCanvasTkAgg(self.fig, master=self.__root)

    def close(self) -> None:
        """Ferme les connexions et détruit les composants gui."""
        super().close()
        self.__canvas.get_tk_widget().destroy()

    def show(self) -> None:
        """Affiche le graphique."""
        self.widget().pack(
            side=tk.TOP, fill=tk.BOTH, expand=True
        )
        self.widget.after(1000, lambda: next(self))

    def __enter__(self) -> Self:
        """Démarre la mise à jour du graphe et l'affiche.

        Returns
        -----------------
        self
            Les objets Graphe implémentent __exit__.
        """
        self.__logger.debug('')
        super().__enter__()
        self.show()
        return self

    @property
    def canvas(self) -> FigureCanvasTkAgg:
        """Retourne l'objet FigureCanvasTkAgg sous-jacent."""
        return self.__canvas

    @property
    def widget(self) -> FigureCanvasTkAgg:
        return self.canvas.get_tk_widget()


def main(*, debug: bool = False) -> None:
    """Affiche le spectre de fréquence d'un signal artificiel."""
    from functools import partial  # noqa: PLC0415

    from .acq import Tableau, sinus  # noqa: PLC0415
    from .calcul import FFT, rectangle  # noqa: PLC0415
    from .serial import LigneSerie  # noqa: PLC0415

    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    lignes = sinus(n=50)

    fenetre: Calcul = rectangle(153)()
    calcul_fft: Calcul = FFT() @ fenetre

    root = tk.Tk()
    root.wm_title('Démonstration avec des données artificielles')

    format_fft = Format(
        title='Transformée de Fourier', xlim=(0, 0.5), ylim=None
    )

    format_sig = Format(title='Signal artificiel')

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

                    def quit_app() -> None:
                        gra1.close()
                        gra2.close()
                        root.quit()

                    root.protocol('WM_DELETE_WINDOW', quit_app)

                    __logger.debug('%s', root)

                    root.mainloop()

    __logger.debug('Fini.')


if __name__ == '__main__':
    import sys

    debug = '--debug' in sys.argv
    main(debug=debug)
