# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de dessin de graphiques."""

import functools
import pathlib
import threading
import time
import tkinter as tk
import typing
from collections.abc import MutableMapping
from pathlib import Path

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)

from .acq import sinus
from .calcul import TableauCalcul as CalTab
from .calcul import fft
from .exceptions import (
    CanvasAlreadySetError,
    IncorrectFormatKeyError,
    IncorrectFormatTypeError,
    NotAxesTypeError,
    NotFigureTypeError,
    NotLine2DTypeError,
    UpdatedPropertyTypeError,
    WrongArtistTypeError,
    WrongCanvasTypeError,
)
from .logging import WithLogger, suppress
from .serial import LigneSerie

if typing.TYPE_CHECKING:
    from typing import Any, ClassVar, Self


class BaseFormat(WithLogger, MutableMapping):
    """Objet de paramétrage pour un :obj:`Artist` de matplotlib."""

    SETTINGS: tuple[str] = (
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
        'zorder',
    )
    """Paramètres permis."""

    DEFAULTS: ClassVar[dict[str, Any]] = {}
    """Valeurs par défaut pour les paramètres."""

    # Les valeurs par défaut son vérifiées par
    # matplotlib, d'où l'annotation :obj:`Any`.
    def __init__(self, artist: mpl.artist.Artist, **kargs: Any) -> None:
        """Enregistre les paramètres et l':obj:`Artist`."""
        self.artist = artist

        self.__kargs = {}
        for s in self.SETTINGS:
            if kargs.get(s, None) is not None:
                self[s] = kargs[s]

    # Les valeurs par défaut son vérifiées par
    # matplotlib, d'où l'annotation :obj:`Any`.
    def default(self, key: str) -> Any:  # noqa: ANN401
        """Trouve la valeur par défaut pour key.

        Returns
        ---------------------------
        Any
        """
        return self.DEFAULTS.get(key, None)

    @property
    def artist(self) -> mpl.artist.Artist:
        """L'objet :obj:`Artist` paramétré."""
        return self.__artist

    @artist.setter
    def artist(self, val: mpl.artist.Artist) -> None:
        """L'objet :obj:`Artist` paramétré."""
        if not isinstance(val, mpl.artist.Artist):
            raise WrongArtistTypeError(val)

        self.__artist = val

    def copy(self) -> Self:
        """Crée un objet du même type avec les mêmes valeurs.

        Returns
        ---------------------------
        Self
            Une copie.
        """
        return type(self)(**dict(self))

    def __iter__(self) -> iter[str]:
        """Alias pour self.keys.

        Returns
        ---------------------------
        self.keys(): iter[str]
        """
        return self.keys()

    @functools.cached
    def keys(self) -> iter[str]:
        """Un itérateur sur le clés fixées.

        Returns
        ---------------------------
        iter[str]
        """
        return iter([key for key in self.SETTINGS if self[key] is not None])

    def values(self) -> iter[Any]:
        """Un itérateur sur les valeurs fixées.

        Returns
        ---------------------------
        iter[Any]
        """
        return iter([self[key] for key in self.keys()])

    def items(self) -> iter[tuple[str, Any]]:
        """Un itérateur sur les paires (clé, valeur).

        Returns
        ---------------------------
        iter[tuple(str, Any)]
        """
        return zip(self.keys(), self.values(), strict=True)

    @functools.cached
    def __contains__(self, key: str) -> bool:
        """Vérifie si le paramètre key existe.

        Returns
        ---------------------------
        True
            Si le paramètre existe.
        False
            Si le paramètre n'existe pas.
        """
        return key in self.SETTINGS

    @functools.cached
    def __len__(self) -> int:
        """Calcule le nombre de paramètres.

        Returns
        ---------------------------
        int
            Le nombre de paramètres.
        """
        return len(self.SETTINGS)

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        """Obtiens la valeur d'un paramètre.

        Raises
        ---------------------------
        IncorrectFormatKeyError
            Quand la clé utilisée n'est pas acceptée
            par l'objet :class:`mpl.artist.Artist`.

        Returns
        ---------------------------
        Any
            Valeur par défaut, si la valeur n'a pas été fixée.
        Any
            La valeur fixée, si elle l'a été.
        """  # noqa: DOC502
        if key in self.SETTINGS and key not in self.__kargs:
            return self.default(key)

        if key in self.__kargs:
            return self.__kargs[key]

        raise IncorrectFormatKeyError(self, key)

    # Les valeurs de paramètres sont définies par
    # matplotlib, et nous n'en faisons aucune
    # vérification ici, d'où l'utilisation de
    # l'annotation :obj:`Any`.
    def get(self, key: str, default: Any | None = None) -> Any:  # noqa: ANN401
        """Obtiens la valeur d'un paramètre.

        Returns
        ---------------------------
        Any
            La valeur du paramètre tel que retournée par
            matplotlib.
        """
        if key in self:
            return self[key]

        return default

    def __eq__(self, other: BaseFormat) -> bool:
        """Vérifie l'égalité des paramètres.

        Returns
        ---------------------------
        True
            Si tous les paramètres et leurs valeurs sont égales.
        False
            Si au moins un paramètre n'existe que dans un objet,
            ou que la valeur d'au moins un paramètre n'est pas
            égale dans les deux objets.
        """
        return all(
            a == b for a, b in zip(self.items(), other.items(), strict=True)
        )

    def __hash__(self) -> None:
        """Hache la valeur courante de l'objet."""
        return hash(tuple(self.items()))

    # Les valeurs données aux paramètres sont vérifiées
    # par matplotlib à l'application des paramètres.
    # Pour l'instant, aucune vérification n'est faite
    # dans ce module, et c'est pourquoi on utilise
    # l'annotation :obj:`Any`.
    def __setitem__(self, key: str, val: Any) -> None:  # noqa: ANN401
        """Fixe la valeur d'un paramètre."""
        if key not in self.SETTINGS:
            raise IncorrectFormatKeyError(self, key)

        self.__kargs[key] = val

    def __delitem__(self, key: str) -> None:
        """Réinitialise un paramètre à sa valeur par défaut."""
        if key not in self.__kargs:
            raise IncorrectFormatKeyError(self, key)

        del self.__kargs[key]

    def __or__(self, other: dict[str, Any] | BaseFormat) -> Self:
        """Retourne un objet de format mis à jour à partir d'un autre objet.

        Returns
        ---------------------------
        Self
            Un nouvel objet, combinant les deux objets initiaux.
        """
        self.checkin()

        nouv = self.copy()
        nouv |= other
        return nouv

    def __ior__(self, other: dict[str, Any] | BaseFormat) -> Self:
        """Mets le format à jour à partir d'un autre objet.

        Returns
        ---------------------------
        Self
            L'objet initial, mis à jour.
        """
        self.checkin()

        if isinstance(other, type(self)):
            self.__kargs |= other.kargs
        elif isinstance(other, dict):
            self.__kargs |= other
        else:
            raise IncorrectFormatTypeError(self, other)

        return self

    def __call__(self, art: mpl.artist.Artist | None = None) -> None:
        """Applique le format à un objet Artist."""
        if art is None:
            art = self.artist
        art.set(**dict(self))


class FigureFormat(BaseFormat):
    """Paramètres de format d'une figure."""

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
        'size_inches',
    )

    @property
    def fig(self) -> mpl.figure.Figure:
        """Figure."""
        return self.artist

    @fig.setter
    def fig(self, val: mpl.figure.Figure) -> None:
        """Figure."""
        if not isinstance(val, mpl.figure.Figure):
            raise NotFigureTypeError(val)

        self.artist = val


class AxesFormat(BaseFormat):
    """Paramètres de format d'un système d'axes."""

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
        'xticksybound',
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
        """Système d'axes."""
        return self.artist

    @ax.setter
    def ax(self, val: mpl.axes.Axes) -> None:
        """Système d'axes."""
        if not isinstance(val, mpl.axes.Axes):
            raise NotAxesTypeError(val)

        self.artist = val


class LineFormat(BaseFormat):
    """Paramètres de formatage pour un tracé."""

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
        'ydata',
    )

    @property
    def line(self) -> mpl.lines.Line2D:
        """Tracé sur le graphique."""
        return self.artist

    @line.setter
    def line(self, val: mpl.lines.Line2D) -> None:
        """Tracé sur le graphique."""
        if not isinstance(val, mpl.lines.Line2D):
            raise NotLine2DTypeError(val)

        self.artist = val


class BaseGraphe(CalTab):
    """Graphe de base."""

    def __init__(self, com: LigneSerie | None) -> None:
        """Défini les objets de dessin."""
        self.checkin()
        super().__init__(com)
        self.__format = {}
        self.__fig = mpl.figure.Figure()
        self.add_format(self.fig)
        self.__plots = {}

    def add_format(self, art: mpl.artist.Artist) -> None:
        """Ajoute un format du bon type associé à art."""
        if isinstance(art, mpl.lines.Line2D):
            fmtcls = LineFormat
        elif isinstance(art, mpl.axes.Axes):
            fmtcls = AxesFormat
        elif isinstance(art, mpl.figure.Figure):
            fmtcls = FigureFormat
        elif isinstance(art, mpl.artist.Artist):
            fmtcls = BaseFormat
        else:
            raise WrongArtistTypeError(art)

        self.__format[id(art)] = fmtcls(art)

    def get_formats(self, key: int | str | None) -> list[BaseFormat]:
        """Obtiens la liste des formats enregistrés.

        Returns
        ---------------------------
        list[BaseFormat]
            Une liste des objets de formatage de la figure pour
            le graphe correspondant à key.
        """
        if key is None:
            return list(self.__format.values())

        objects = [self.plots[key]] + self.lines(key)
        return [self.__format[id(obj)] for obj in objects]

    @property
    def fig(self) -> mpl.figure.Figure:
        """Figure active."""
        self.checkin()
        return self.__fig

    @property
    def axes(self) -> list[mpl.axes.Axes]:
        """Systèmes d'axes actifs."""
        self.checkin()
        return self.fig.axes

    @property
    def plots(self) -> dict[str | int, mpl.axes.Axes]:
        """Liste interne des systèmes d'axes."""
        self.checkin()
        return self.__plots

    def add_plot(self, key: int | str, ax: mpl.axes.Axes) -> None:
        """Ajoute un système d'axes à la liste interne."""
        self.checkin()
        self.__plots[key] = ax

    def lines(self, key: int | str) -> list[mpl.lines.Line2D]:
        """Lignes tracées pour la colonne key.

        Returns
        ---------------------------
        list[mpl.lines.Line2D]
            Une liste des tracés du graphe.
        """
        self.checkin()
        lines = self.__plots[key].get_lines()
        self.debug('lines = %s', lines)
        return lines

    def add_subplot(
        self, which: tuple[int | str], where: tuple = (1, 1, 1), **kargs: Any
    ) -> mpl.axes.Axes:
        """Ajoute un sous-graphique à la figure.

        Returns
        ---------------------------
        mpl.axes.Axes
            Le système d'axes pour le graphique.
        """
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
        """Mise à jour conditionnelle du graphique."""
        self.checkin()

        if self.updated:
            self.debug('updated = True')
            self.frame()

        self.updated = False

    def add_input(self) -> list[mpl.axes.Axes]:
        """Ajoute un sous-graphique par colonne de données."""
        self.checkin()
        num = len(self.df.columns) // 2

        ncols, nrows = 1, 1
        while ncols * nrows < num:
            if nrows < ncols:
                nrows += 1
            else:
                ncols += 1
        shape = (ncols, nrows)

        for i in range(1, num + 1):
            where = shape + (i,)
            self.add_subplot(i, where)

    @property
    def updated(self) -> bool:
        """Si les données ont été mises à jour."""
        self.checkin()
        return self._updated.is_set()

    @updated.setter
    def updated(self, val: bool) -> None:
        """Si les données ont été mises à jour."""
        self.checkin()
        self.debug('val = %s', val)

        if not isinstance(val, bool):
            raise UpdatedPropertyTypeError(val)

        if val and not self._updated.is_set():
            self._updated.set()
        elif not val and self._updated.is_set():
            self._updated.clear()

    def frame(self) -> None:
        """Met à jour les données du graphique."""
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
                    ts, xs = (
                        df.iloc[:, 2 * i].to_numpy(),
                        df.iloc[:, 2 * i + 1].to_numpy(),
                    )
                    line.set_data(ts, xs)

        self.format()

    def save(self, path: pathlib.Path) -> None:
        """Enregistre l'image."""
        self.checkin()
        self.debug('path = %s', path)
        self.frame()
        self.fig.savefig(str(path))

    def format(
        self, key: tuple[int | str] | None = None, **kargs: Any
    ) -> None:
        """Applique le format aux éléments du graphique."""
        self.checkin()
        if isinstance(key, tuple):
            fmts = self.get_formats(key[0])
            fmt = fmts[key[1]]
            fmt |= kargs

        for fmt in self.__format.values():
            fmt()

    def wait(self) -> None:
        """Attends que l'affichage soit à jour."""
        super().wait()
        self.frame(block=True)


class PyPlotGraphe(BaseGraphe):
    """Enrobage deplt."""

    def __init__(self, com: LigneSerie) -> None:
        """Enregistre une nouvelle figure dansplt."""
        self.checkin()
        super().__init__(com)
        plt.figure(id(self))

    @property
    def fig(self) -> mpl.figure.Figure:
        """La figure active dansplt."""
        return plt.figure(id(self))

    def add_subplot(
        self, which: tuple[int | str], where: tuple = (1, 1, 1), **kargs: Any
    ) -> mpl.axes.Axes:
        """Ajoute un sous-graphique à la figure.

        Returns
        ---------------------------
        mpl.axes.Axes
            L'objet Axes contenant le sous-graphique.
        """
        self.checkin()
        self.debug('which = %s, where = %s', which, where)
        self.debug('kargs = %s', kargs)

        if not isinstance(which, tuple):
            which = (which,)

        ax = plt.subplot(*where, **kargs)

        for w in which:
            self.add_plot(w, ax)

            self.debug('plot = %s', self.plots[w])

        self.frame()
        return ax

    def show(self) -> None:
        """Affiche le graphique avec plt."""
        self.checkin()
        self.frame()
        plt.draw()
        plt.show()


class CanvasGraphe(BaseGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    def __init__(
        self,
        com: LigneSerie | None,
        *,
        canvas_class: type[FigureCanvasAgg] = FigureCanvasAgg,
        **kargs: Any,
    ) -> None:
        """Configure la classe parente."""
        self.checkin()
        self.debug('CanvasClass = %s', canvas_class.__name__)
        self.debug('kargs = %s', kargs)
        super().__init__(com)
        self.__canvas = None

        self.canvas = canvas_class(self.fig, **kargs)

    @property
    def canvas(self) -> FigureCanvasAgg:
        """Canevas du graphique."""
        self.checkin()
        return self.__canvas

    @canvas.setter
    def canvas(self, val: FigureCanvasAgg) -> None:
        """Valide la valeur à assigner à canevas."""
        self.checkin()
        if not isinstance(val, FigureCanvasAgg):
            raise WrongCanvasTypeError(val)

        if self.__canvas is not None:
            raise CanvasAlreadySetError(self.__canvas)

        self.__canvas = val

    def update(self) -> None:
        """Mets à jour les données du graphique."""
        self.checkin()
        super().update()
        self.draw()

    def draw(self) -> None:
        """Redessine le dessin."""
        self.checkin()
        self.canvas.draw()


class FichierGraphe(CanvasGraphe):
    """Encapsulation d'un tableau et canvas pour afficher un graphe."""

    @typing.override
    def __init__(
        self,
        com: LigneSerie,
        *,
        name: str | pathlib.Path = 'graphe.png',
    ) -> None:
        """Création des objets d'exécution parallèle."""
        self.checkin()
        super().__init__(com, CanvasClass=FigureCanvasAgg)
        self.__name = Path(name)
        self.__thread = threading.Thread(target=self.__run)
        self.__loquet = threading.Lock()
        self.__arret = threading.Event()

    @property
    def name(self) -> str:
        """Nom du fichier pour enregistrer le graphique."""
        self.checkin()
        return str(self.__name.resolve())

    def save(self, *, name: str | pathlib.Path | None = None) -> None:
        """Enregistre l'image."""
        self.checkin()
        if name is None:
            name = self.name

        super().save(name)

    def __run(self) -> None:
        """Lit les nouvelles données."""
        self.checkin()
        with suppress(self, Exception):
            while True:
                if self.__arret.is_set():
                    break

                self.update()

                with self.__loquet:
                    self.save()

                time.sleep(0.1)

        if not self.__arret.is_set():
            self.__arret.set()

    def close(self) -> None:
        """Arrête l'exécution des fils."""
        self.checkin()
        super().close()
        self.__arret.set()
        self.__thread.join()

    def start(self) -> None:
        """Démarre l'exécution des fils."""
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
    ) -> None:
        """Initialise le graphe."""
        self.checkin()
        super().__init__(com, CanvasClass=FigureCanvasTkAgg, master=root)
        self.__root: tk.Frame = root
        self.__toolbar = None

    @property
    def root(self) -> tk.Frame:
        """Parent des composants Tk."""
        return self.__root

    @property
    def master(self) -> tk.Frame:
        """Parent des composants Tk."""
        return self.__root

    def close(self) -> None:
        """Ferme les connexions et détruit les composants gui."""
        self.checkin()
        super().close()

        try:
            self.widget.destroy()
        except tk.TclError:
            pass

    def update(self) -> None:
        """Mets à jour le graphique."""
        self.checkin()
        super().update()
        if self.__toolbar is not None:
            self.toolbar.update()
        self.widget.after(1000, self.update)

    def show(self) -> None:
        """Affiche le graphique."""
        self.checkin()
        self.draw()
        self.widget.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.widget.after(100, self.update)

    @property
    def widget(self) -> tk.Frame:
        """Composant Tk du canevas du graphique."""
        self.checkin()
        return self.canvas.get_tk_widget()

    @property
    def toolbar(self) -> NavigationToolbar2Tk:
        """Barre de navigation associée au graphe affiché."""
        if self.__toolbar is None:
            self.__toolbar = NavigationToolbar2Tk(
                self.canvas, self.root, pack_toolbar=False
            )
            self.__toolbar.update()

        return self.__toolbar


def interactive_echo_pyplot_plot(*, debug: bool = False) -> None:
    """Affiche des données simulées avecplt."""
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
            for _i in range(100):
                com.print(next(lignes))

            tab.wait()
            tab.show()


def static_echo_image_plot(*, debug: bool = False) -> None:
    """Compile et enregistre des données simulées."""
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
            for _i in range(100):
                com.print(next(lignes))
            tab.wait()
            tab.save('graphe.png')


def dynamic_echo_image_plot(*, debug: bool = False) -> None:
    """Enregistre des données simulées."""
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
            for _i in range(100):
                com.print(next(lignes))
            tab.wait()


def static_echo_tk_plot(*, debug: bool = False) -> None:
    """Compile et affiche des données simulées."""
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
            for _i in range(100):
                com.print(next(lignes))

            tab.show()
            tab.wait()
            root.mainloop()


def dynamic_echo_tk_plot(*, debug: bool = False) -> None:
    """Affiche des données simulées."""
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
            for _i in range(100):
                com.print(next(lignes))

            root.mainloop()


def interactive_echo_tk_plot(*, debug: bool = False) -> None:
    """Affiche des données simulées."""
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
        tab.toolbar.grid(column=0, row=1, sticky=tk.W + tk.E)

        with tab:
            for _i in range(100):
                com.print(next(lignes))

            root.mainloop()


def static_arduino_image_plot(*, debug: bool = False) -> None:
    """Compile et enregistre les données reçues d'un Arduino."""


def dynamic_arduino_image_plot(*, debug: bool = False) -> None:
    """Enregistre les données reçues d'un Arduino."""


def static_arduino_tk_plot(*, debug: bool = False) -> None:
    """Compile et affiche les données reçues d'un Arduino."""


def dynamic_arduino_tk_plot(*, debug: bool = False) -> None:
    """Affiche les données reçues d'un Arduino."""


def interactive_arduino_tk_plot(*, debug: bool = False) -> None:
    """Affiche les données reçues d'un Arduino."""
