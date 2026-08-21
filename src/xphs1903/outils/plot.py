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
from matplotlib import pyplot
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from .logging import WithLogger
from .serial import LigneSerie
from .acq import Tableau
from .calcul import TableauCalcul as CalTab


from collections.abc import Callable, Mapping

if typing.TYPE_CHECKING:
    from concurrent.futures import Future
    from types import TracebackType
    from typing import Any, Self


class BaseFormat(WithLogger, Mapping):
    SETTINGS = (
        'agg_filter',
        'alpha',
        'animated',
        'clip_box',
        'clip_on',
        'clip_path',
        'figure',
        'gid',
        'in_layout',
        'label',
        'mouseover',
        'path_effects',
        'picker',
        'rasterized',
        'sketch_params',
        'snap',
        'transform',
        'url',
        'visible',
        'zorder'
    )
    DEFAULTS = {}

    def __init__(
        self,
        artist: mpl.artist.Artist,
        **kargs
    ) -> None:
        self.artist = artist

        self.__kargs = {}
        for s in self.SETTINGS:
            if kargs.get(s, None) is not None:
                self[s] = kargs[s]

    def default(self, key: str) -> Any:
        return self.DEFAULTS.get(key, None)

    @property
    def artist(self) -> mpl.artist.Artist:
        return self.__artist

    @artist.setter
    def artist(self, val: mpl.artist.Artist) -> None:
        if not isinstance(val, mpl.artist.Artist):
            raise TypeError

        self.__artist = val

    def copy(self) -> Self:
        return type(self)(**self)

    def __iter__(self) -> iter:
        return self.keys()

    def keys(self) -> iter:
        return (key for key in self.SETTINGS if self[key] is not None)

    def values(self) -> iter:
        return (self[key] for key in self.keys())

    def items(self) -> iter:
        return zip(self.keys(), self.values())

    def __contains__(self, key: str) -> bool:
        return key in self.SETTINGS

    def __len__(self) -> int:
        return len(self.SETTINGS)

    def __getitem__(self, key: str) -> Any:
        if key in self.SETTINGS and key not in self.__kargs:
            return self.default(key)

        if key in self.__kargs:
            return self.__kargs[key]

        raise KeyError

    def get(self, key: str, default: Any | None = None) -> Any:
        if key in self:
            return self[key]

        return default

    def __eq__(self, other: BaseFormat) -> bool:
        return all(a == b for a, b in zip(self.items(), other.items()))

    def __neq__(self, other: BaseFormat) -> bool:
        return not self == other

    def __setitem__(self, key: str, val: Any) -> None:
        if key not in self.SETTINGS:
            raise KeyError

        self.__kargs[key] = val

    def __delitem__(self, key: str) -> None:
        if key not in self.__kargs:
            raise KeyError

        del self.__kargs[key]

    def __or__(self, other: dict[str, Any] | BaseFormat) -> Self:
        self.checkin()

        nouv = self.copy()
        nouv |= other
        return nouv

    def __ior__(self, other: dict[str, Any] | BaseFormat) -> Self:
        self.checkin()

        if isinstance(other, type(self)):
            self.__kargs |= other.kargs
        elif isinstance(other, dict):
            self.__kargs |= other
        else:
            raise TypeError

        return self

    def __call__(self, art: mpl.artist.Artist | None = None) -> None:
        if art is None:
            art = self.artist

        art.set(**dict(self))


class FigureFormat(BaseFormat):
    SETTINGS = BaseFormat.SETTINGS + (
        'canvas',
        'constrained_layout',
        'constrained_layout_pads',
        'dpi',
        'edgecolor',
        'facecolor',
        'figheight',
        'figwidth',
        'layout_engine',
        'linewidth',
        'size_inches'
    )

    @property
    def fig(self) -> mpl.figure.Figure:
        return self.artist

    @fig.setter
    def fig(self, val: mpl.figure.Figure) -> None:
        if not isinstance(val, mpl.figure.Figure):
            raise TypeError

        self.artist = val

class AxesFormat(BaseFormat):
    SETTINGS = BaseFormat.SETTINGS + (
        'adjustable',
        'anchor',
        'aspect',
        'autoscale_on',
        'autoscalex_on',
        'autoscaley_on',
        'axes_locator',
        'axisbelow',
        'box_aspect',
        'facecolor',
        'forward_navigation_events',
        'navigate',
        'navigate_mode',
        'position',
        'prop_cycle',
        'rasterization_zorder',
        'sublotspec',
        'title',
        'xbound',
        'xinverted',
        'xlabel',
        'xlim',
        'xmargin',
        'xscale',
        'xticklabels',
        'xticks'
        'ybound',
        'yinverted',
        'ylabel',
        'ylim',
        'ymargin',
        'yscale',
        'yticklabels',
        'yticks',
    )

    @property
    def ax(self) -> mpl.axes.Axes:
        return self.artist

    @ax.setter
    def ax(self, val: mpl.axes.Axes) -> None:
        if not isinstance(val, mpl.axes.Axes):
            raise TypeError

        self.artist = val

class LineFormat(BaseFormat):
    SETTINGS = BaseFormat.SETTINGS + (
        'color',
        'dash_capstyle',
        'dash_joinstyle',
        'dashes',
        'data',
        'drawstyle',
        'fillstyle',
        'gapcolor',
        'linestyle',
        'linewidth',
        'marker',
        'markeredgecolor',
        'markeredgewidth',
        'markerfacecolor',
        'markerfacecoloralt',
        'markersize',
        'markevery',
        'pickradius',
        'solid_capstyle',
        'solid_joinstyle',
        'xdata',
        'ydata'
    )

    @property
    def line(self) -> mpl.lines.Line2D:
        return self.artist

    @line.setter
    def line(self, val: mpl.lines.Line2D) -> None:
        if not isinstance(val, mpl.lines.Line2D):
            raise TypeError

        self.artist = val

class BaseGraphe(CalTab):

    def __init__(self, com: LigneSerie | None, fmt: Format | None = None) -> None:
        self.checkin()
        super().__init__(com)
        self.__format = {}
        self.__fig = mpl.figure.Figure()
        self.add_format(self.fig)
        self.__plots = {}

    def add_format(self, art: mpl.artist.Artist) -> None:
        if isinstance(art, mpl.lines.Line2D):
            fmtcls = LineFormat
        elif isinstance(art, mpl.axes.Axes):
            fmtcls = AxesFormat
        elif isinstance(art, mpl.figure.Figure):
            fmtcls = FigureFormat
        elif isinstance(art, mpl.artist.Artist):
            fmtcls = BaseFormat
        else:
            raise TypeError

        self.__format[id(art)] = fmtcls(art)

    def get_formats(self, key: int | str | None) -> list[BaseFormat]:
        if key is None:
            return list(self.__format.values())

        objects = [self.plots[key]] + self.lines(key)
        formats = [self.__format[id(obj)] for obj in objects]
        return formats

    @property
    def fig(self) -> mpl.figure.Figure:
        self.checkin()
        return self.__fig

    @property
    def axes(self) -> list[mpl.axes.Axes]:
        self.checkin()
        return self.fig.axes

    @property
    def plots(self) -> dict[str | int, mpl.axes.Axes]:
        self.checkin()
        return self.__plots

    def add_plot(self, key: int | str, ax: mpl.axes.Axes) -> None:
        self.checkin()
        self.__plots[key] = ax

    def lines(self, key: int | str) -> list[mpl.artist.Line2D]:
        self.checkin()
        lines = self.__plots[key].get_lines()
        self.debug('lines = %s', lines)
        return lines

    def add_subplot(self, which: tuple[int | str], where: tuple = (1,1,1), **kargs) -> mpl.axes.Axes:
        self.checkin()
        self.debug('which = %s, where = %s', which, where)
        self.debug('kargs = %s', kargs)

        if not isinstance(which, tuple):
            which = (which,)

        ax = self.fig.add_subplot(*where, **kargs)
        self.add_format(ax)

        for w in which:
            self.add_plot(w, ax)

            self.debug('plot = %s', self.plots[w])
        self.frame()
        return ax

    def update(self) -> None:
        self.checkin()

        if self.updated:
            self.debug('updated = True')
            self.frame()

        self.updated = False

    def add_input(self) -> list[mpl.axes.Axes]:
        self.checkin()
        num = len(self.df.columns) // 2

        shape = (3, 3)
        if not num % 2:
            shape = (2, num//2)

        for i in range(1, num+1):
            where = shape + (i,)
            self.add_subplot(i, where)

    @property
    def updated(self) -> bool:
        self.checkin()
        return self._updated.is_set()

    @updated.setter
    def updated(self, val: bool) -> None:
        self.checkin()
        self.debug('val = %s', val)

        if not isinstance(val, bool):
            raise TypeError

        if val and not self._updated.is_set():
            self._updated.set()
        elif not val and self._updated.is_set():
            self._updated.clear()

    def frame(self, *, block: bool = False, timeout: float | None = None) -> None:
        self.checkin()

        for key in self.__plots:
            self.debug('key = %s', key)
            lines = self.lines(key)
            df = self[key]

            if df is not None:
                self.debug('df.size = %s', df.size)

            if len(lines) == 0 and df is not None and not df.empty:
                n = len(df.columns)
                self.debug('n = %s', n)
                ts, xs = df.iloc[:, 0].to_numpy(), df.iloc[:, 1].to_numpy()
                ax = self.plots[key]
                lines = ax.plot(ts, xs)

                for line in lines:
                    self.add_format(line)

                continue

            if lines is not None:
                for i, line in enumerate(lines):
                    ts, xs = df.iloc[:,2*i].to_numpy(), df.iloc[:, 2*i+1].to_numpy()
                    line.set_data(ts, xs)

        self.format()

    def save(self, path: pathlib.Path) -> None:
        self.checkin()
        self.debug('path = %s', path)
        self.frame()
        self.fig.savefig(str(path))

    def format(self, key: tuple[int | str] | None = None, **kargs) -> None:
        self.checkin()
        if isinstance(key, tuple):
            fmts = self.get_formats(key[0])
            fmt = fmts[key[1]]
            fmt |= kargs

        for fmt in self.__format.values():
            fmt()

    def wait(self) -> None:
        super().wait()
        self.frame(block=True)


class PyPlotGraphe(BaseGraphe):

    def __init__(self, com: LigneSerie, fmt: Format | None = None) -> None:
        self.checkin()
        super().__init__(com, fmt=fmt)
        pyplot.figure(id(self))

    @property
    def fig(self) -> mpl.figure.Figure:
        return pyplot.figure(id(self))

    def add_subplot(self, which: tuple[int | str], where: tuple = (1,1,1), **kargs) -> mpl.axes.Axes:
        self.checkin()
        self.debug('which = %s, where = %s', which, where)
        self.debug('kargs = %s', kargs)

        if not isinstance(which, tuple):
            which = (which,)

        ax = pyplot.subplot(*where, **kargs)

        for w in which:
            self.add_plot(w, ax)

            self.debug('plot = %s', self.plots[w])

        self.frame()
        return ax

    def show(self) -> None:
        self.checkin()
        self.frame()
        pyplot.draw()
        pyplot.show()

class CanvasGraphe(BaseGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    def __init__(
        self,
        com: LigneSerie | None,
        fmt: Format | None = None,
        *,
        CanvasClass: type[FigureCanvasAgg] = FigureCanvasAgg,
        **kargs,
    ) -> None:
        self.checkin()
        self.debug('CanvasClass = %s', CanvasClass.__name__)
        self.debug('kargs = %s', kargs)
        super().__init__(com, fmt=fmt)
        self.__canvas = None

        self.canvas = CanvasClass(self.fig, **kargs)

    @property
    def canvas(self) -> FigureCanvasAgg:
        self.checkin()
        return self.__canvas

    @canvas.setter
    def canvas(self, val: FigureCanvasAgg) -> None:
        self.checkin()
        if not isinstance(val, FigureCanvasAgg):
            raise TypeError

        if self.__canvas is not None:
            raise RuntimeError

        self.__canvas = val

    def update(self) -> None:
        self.checkin()
        super().update()
        self.draw()

    def draw(self):
        self.checkin()
        self.canvas.draw()

class FichierGraphe(CanvasGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    @typing.override
    def __init__(
        self,
        com: LigneSerie,
        *,
        fmt: Format | None = None,
        name: str | pathlib.Path = 'graphe.png'
    ) -> None:
        self.checkin()
        super().__init__(com, fmt, CanvasClass=FigureCanvasAgg)
        self.__name = Path(name)
        self.__thread = threading.Thread(target=self.__run)
        self.__loquet = threading.Lock()
        self.__arret = threading.Event()

    @property
    def name(self) -> str:
        self.checkin()
        return str(self.__name.resolve())

    def save(self, *, name: str | pathlib.Path | None = None) -> None:
        self.checkin()
        if name is None:
            name = self.name

        super().save(name)

    def __run(self) -> None:
        """Lit les nouvelles données."""
        self.checkin()
        try:
            while True:
                if self.__arret.is_set():
                    break

                self.update()

                with self.__loquet:
                    self.save()

                time.sleep(0.1)
        except Exception as err:
            self.error('', exc_info=err)
        finally:
            if not self.__arret.is_set():
                self.__arret.set()

    def close(self) -> None:
        self.checkin()
        super().close()
        self.__arret.set()
        self.__thread.join()

    def start(self) -> None:
        self.checkin()
        super().start()
        self.__thread.start()


class TkGraphe(CanvasGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    @typing.override
    def __init__(
        self,
        com: LigneSerie | None,
        *,
        root: tk.Frame,
        fmt: Format | None = None,
    ) -> None:
        """Initialise le graphe."""
        self.checkin()
        super().__init__(com, fmt=fmt, CanvasClass=FigureCanvasTkAgg, master=root)
        self.__root: tk.Frame = root
        self.__toolbar = None

    @property
    def root(self) -> tk.Frame:
        return self.__root

    @property
    def master(self) -> tk.Frame:
        return self.__root

    def close(self) -> None:
        """Ferme les connexions et détruit les composants gui."""
        self.checkin()
        super().close()

        try:
            self.widget.destroy()
        except tk.TclError:
            pass

    def update(self):
        self.checkin()
        super().update()
        if self.__toolbar is not None:
            self.toolbar.update()
        self.widget.after(1000, self.update)

    def show(self) -> None:
        """Affiche le graphique."""
        self.checkin()
        self.draw()
        self.widget.grid(
            column=0, row=0, sticky=tk.N+tk.S+tk.W+tk.E
        )
        self.widget.after(100, self.update)

    @property
    def widget(self) -> tk.Frame:
        self.checkin()
        return self.canvas.get_tk_widget()

    @property
    def toolbar(self) -> NavigationToolbar2Tk:
        if self.__toolbar is None:
            self.__toolbar = NavigationToolbar2Tk(self.canvas, self.root, pack_toolbar=False)
            self.__toolbar.update()

        return self.__toolbar


def interactive_echo_pyplot_plot(*, debug: bool = False) -> None:
    import time
    from matplotlib import pyplot as plt
    from .acq import sinus
    from .calcul import fft

    lignes = sinus()
    with LigneSerie() as com:
        tab = PyPlotGraphe(com)

        if debug:
            tab.log_to_stderr()
            tab.setLevel('debug')

        tab.register(fft)
        tab.add_subplot('fft', (1, 2, 2))
        tab.add_subplot(0, (1, 2, 1))

        with tab:
            for i in range(100):
                com.print(next(lignes))

            tab.wait()

            tab.show()

def static_echo_image_plot(*, debug: bool = False) -> None:
    import time  # noqa: PLC0415
    from .acq import sinus
    from .calcul import fft

    lignes = sinus()
    with LigneSerie() as com:
        tab = BaseGraphe(com)

        if debug:
            tab.log_to_stderr()
            tab.setLevel('debug')

        tab.register(fft)
        tab.add_subplot('fft', (1, 2, 2))
        tab.add_subplot(0, (1, 2, 1))

        with tab:
            for i in range(100):
                com.print(next(lignes))
            tab.wait()
            tab.save('graphe.png')

def dynamic_echo_image_plot(*, debug: bool = False) -> None:
    import time  # noqa: PLC0415
    from .acq import sinus
    from .calcul import fft

    lignes = sinus()
    with LigneSerie() as com:
        tab = FichierGraphe(com)

        if debug:
            tab.log_to_stderr()
            tab.setLevel('debug')

        tab.register(fft)
        tab.add_subplot(0, (1, 2, 1))
        tab.add_subplot('fft', (1, 2, 2))

        with tab:
            for i in range(100):
                com.print(next(lignes))
            tab.wait()

def static_echo_tk_plot(*, debug: bool = False) -> None:
    import time  # noqa: PLC0415
    from .acq import sinus
    from .calcul import fft

    root = tk.Tk()
    lignes = sinus()
    with LigneSerie() as com:
        tab = TkGraphe(com, root=root)

        if debug:
            tab.log_to_stderr()
            tab.setLevel('debug')

        tab.register(fft)
        tab.add_subplot(0, (1, 2, 1))
        tab.add_subplot('fft', (1, 2, 2))

        with tab:
            for i in range(100):
                com.print(next(lignes))

            tab.show()
            tab.wait()
            root.mainloop()

def dynamic_echo_tk_plot(*, debug: bool = False) -> None:
    import time  # noqa: PLC0415
    from .acq import sinus
    from .calcul import fft

    root = tk.Tk()
    lignes = sinus()
    with LigneSerie() as com:
        tab = TkGraphe(com, root=root)

        if debug:
            tab.log_to_stderr()
            tab.setLevel('debug')

        tab.register(fft)
        tab.add_subplot(0, (1, 2, 1))
        tab.add_subplot('fft', (1, 2, 2))
        tab.show()

        with tab:
            for i in range(100):
                com.print(next(lignes))

            root.mainloop()

def interactive_echo_tk_plot(*, debug: bool = False) -> None:
    import time  # noqa: PLC0415
    from .acq import sinus
    from .calcul import fft

    root = tk.Tk()
    lignes = sinus()
    with LigneSerie() as com:
        tab = TkGraphe(com, root=root)

        if debug:
            tab.log_to_stderr()
            tab.setLevel('debug')

        tab.register(fft)
        tab.add_subplot(0, (1, 2, 1))
        tab.add_subplot('fft', (1, 2, 2))
        tab.show()
        tab.toolbar.grid(column=0, row=1, sticky=tk.W+tk.E)

        with tab:
            for i in range(100):
                com.print(next(lignes))

            root.mainloop()

def static_arduino_image_plot(*, debug: bool = False) -> None:
    pass

def dynamic_arduino_image_plot(*, debug: bool = False) -> None:
    pass

def static_arduino_tk_plot(*, debug: bool = False) -> None:
    pass

def dynamic_arduino_tk_plot(*, debug: bool = False) -> None:
    pass

def interactive_arduino_tk_plot(*, debug: bool = False) -> None:
    pass
