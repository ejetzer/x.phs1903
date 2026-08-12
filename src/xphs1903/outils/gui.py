# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Outils de création d'interface graphique."""

import logging
import re
import tkinter as tk
from tkinter import ttk
from typing import Self

import pandas as pd
import pandastable as pt
import serial.tools.list_ports
from serial import SerialException

from .acq import Tableau
from .calcul import Calcul, Identite
from .plot import Graphe, Format
from .serial import LigneSerie

__logger = logging.getLogger(__name__)
__logger.addHandler(logging.NullHandler())


class SelectionPortSerie(ttk.Frame):
    """Sélecteur de port série."""

    __logger = logging.getLogger(f'{__name__}.SelectionPortSerie')

    def __init__(self, parent: ttk.Frame | tk.Toplevel) -> None:
        """Initialise le sélecteur de ligne série."""
        super().__init__(parent)
        self.__parent = parent
        self.ligne_serie = None
        self.__build()

    def __build(self) -> None:
        """Construit les composants graphiques."""
        # Voir https://tkdocs.com/shipman/entry-validation.html
        self.valider = self.register(self.__valider)
        self.invalide = self.register(self.__invalide)
        self.valeur: tk.StringVar = tk.StringVar()
        self.valeurs: tk.StringVar = tk.StringVar(value=self.options)

        self.valeur.trace_add('write', self.__filtrer)

        self.champ: ttk.Entry = ttk.Entry(
            self,
            textvariable=self.valeur,
            validate='all',
            validatecommand=(self.valider, '%d', '%P', '%s', '%v', '%V'),
            invalidcommand=(self.invalide, '%d', '%P', '%s', '%v', '%V'),
        )
        self.defil: ttk.Scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.liste: tk.Listbox = tk.Listbox(
            self,
            height=10,
            listvariable=self.valeurs,
            selectmode=tk.SINGLE,
            yscrollcommand=self.defil.set,
            exportselection=False,
        )

        self.defil['command'] = self.liste.yview

        self.conn = ttk.Button(
            self,
            text='Connecter',
            command=self.__connect_serial,
        )
        self.conn.state(('!disabled',))

        self.disc = ttk.Button(
            self, text='Déconnecter', command=self.__disconnect_serial
        )
        self.disc.state((tk.DISABLED,))

    def __update(self) -> None:
        """Met l'affichage à jour."""
        self.__logger.debug('%s', self.ligne_serie)
        self.__filtrer(None, None, None)
        self.update()
        self.after(1000, self.__update)

    @property
    def options(self) -> list[str]:
        """Retourne la liste des options acceptables.

        Returns
        ------------------------
        list[str]
            Les options pouvant apparaître dans la liste.
        """
        return [
            x
            for x in self.comports
            if re.search(self.valeur.get(), x) is not None
        ]

    @property
    def comports(self) -> list[str]:
        """Retourne la liste des ports série.

        Returns
        ------------------------
        list[str]
            Les URLs décrivant les différents ports disponibles.
        """
        return [x.device for x in serial.tools.list_ports.comports()] + [
            'loop://'
        ]

    @property
    def selection(self) -> list[str]:
        """Retourne la sélection actuelle.

        Returns
        ------------------------
        list[str]
            Une liste des ports actuellement sélectionnés.
        """
        return [self.liste.get(i) for i in self.liste.curselection()]

    def __filtrer(self, nom: str, mode: str, op: str) -> None:
        """Sélectionne les valeurs pertinentes."""
        self.__logger.debug('%s %s %s', nom, mode, op)
        sel = self.selection
        self.valeurs.set(self.options)

        for i, opt in enumerate(self.options):
            if opt in sel:
                self.liste.selection_set(i)

    # Voir https://tkdocs.com/shipman/entry-validation.html
    def __valider(
        self,
        action: int,
        apres: str,
        avant: str,
        validate: bool,  # noqa: FBT001
        reason: str,
    ) -> bool:
        """Valide une entrée.

        Returns
        ------------------------
        True
            Si il reste des options valides.
        False
            Autrement.
        """
        self.__logger.debug(
            '%s %s %s %s %s', action, apres, avant, validate, reason
        )
        return len(self.options) > 0

    # Voir https://tkdocs.com/shipman/entry-validation.html
    def __invalide(
        self,
        action: int,
        apres: str,
        avant: str,
        validate: bool,  # noqa: FBT001
        reason: str,
    ) -> None:
        """Invalide une entrée."""
        self.__logger.debug(
            '%s %s %s %s %s', action, apres, avant, validate, reason
        )

    def __connect_serial(self) -> None:
        """Connecte la ligne série."""
        self.conn.state(('disabled',))
        sel = self.selection
        if len(sel) > 0:
            self.ligne_serie = LigneSerie(self.selection[0])
            self.__parent.lignes_series.append(self.ligne_serie)

            try:
                self.ligne_serie.open()
            except SerialException:
                pass

            if self.is_open:
                self.disc.state(('!disabled',))

        if not self.is_open:
            self.conn.state(('!disabled',))

    def __disconnect_serial(self) -> None:
        """Déconnecte la ligne série."""
        self.disc.state(('disabled',))
        self.ligne_serie.close()
        self.ligne_serie = None
        self.conn.state(('!disabled',))

    @property
    def is_open(self) -> bool:
        """Retourne l'état de la ligne série.

        Returns
        ------------------------
        False
            Si il n'y a pas de connexion.
        self.ligne_serie.open : bool
            Si la connexion est ouverte.
        """
        if self.ligne_serie is None:
            return False

        return self.ligne_serie.is_open

    def __iter__(self) -> Self:
        """Retourne soi-même.

        Returns
        ------------------------
        self
            SelectionPortSerie implémente __next__.
        """
        return self

    def __next__(self) -> str:
        """Retourne la prochaine ligne.

        Returns
        ------------------------
        ret: str
            Prochaine ligne reçue.

        Raises
        ------------------------
        StopIteration
            Si il n'y a pas d'item à lire.
        """
        if self.ligne_serie is None:
            raise StopIteration

        ret = next(self.ligne_serie)

        if ret is None:
            raise StopIteration

        return ret

    def __str__(self) -> str:
        """Retourne une chaîne descriptive de la connexion.

        Returns
        ------------------------
        ret: str
            Une chaîne décrivant la connexion.
        """
        if self.is_open:
            ret = f'Connecté à {self.ligne_serie.device}.'
        else:
            ret = 'Aucune connexion.'

        return ret

    def pack(self, **kargs: str | int) -> None:
        """Affiche avec pack."""
        self.__update()
        self.champ.grid(row=0, column=0, sticky=tk.E + tk.W)
        self.liste.grid(row=1, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.defil.grid(row=1, column=1, sticky=tk.N + tk.S)
        self.conn.grid(row=2, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.disc.grid(row=3, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        super().pack(**kargs)

    def grid(self, row: int = 0, column: int = 0, **kargs: str | int) -> None:
        """Affiche avec grid."""
        self.__update()
        self.champ.pack(sticky=tk.E + tk.W)
        self.liste.grid(row=1, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.defil.grid(row=1, column=1, sticky=tk.N + tk.S)
        self.conn.grid(row=2, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.disc.grid(row=3, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        super().grid(row=row, column=column, **kargs)


class BarreOutil(tk.Frame):
    """Barre d'outils de base."""


class BarreMenu(tk.Menu):
    """Le menu de base pour les applications de PHS1903."""

    __logger = logging.getLogger(f'{__name__}.BarreMenu')

    def __init__(self, parent: Application) -> None:
        """Initialise le menu."""
        super().__init__(parent)
        self.__parent: Application = parent
        self.__build()

    def __build(self) -> None:
        """Construire les menus."""
        # Menu principal
        menu_app = tk.Menu(self)
        self.add_cascade(label=self.__parent.name, menu=menu_app)
        menu_app.add_command(
            label=f'À propos de {self.__parent.name}',
            command=self.__parent.show_about,
        )
        menu_app.add_command(
            label='Réglages...', command=self.__parent.show_settings
        )
        menu_app.add_command(label='Quitter', command=self.__parent.quit)

        # Menu fichier
        menu_fic = tk.Menu(self)
        self.add_cascade(label='Fichier', menu=menu_fic)
        menu_fic.add_command(label='Exporter...', command=self.__parent.export)

        # Menu d'aide
        menu_aide = tk.Menu(self)
        self.add_cascade(label='Aide', menu=menu_aide)
        menu_aide.add_command(
            label='Journal de débogage', command=self.__parent.show_logger
        )
        menu_aide.add_command(
            label='Documentation du module x.phs1903',
            command=self.__parent.show_doc,
        )


class MoniteurSerie(ttk.Frame):
    """Affiche le texte envoyé via une ligne série."""

    __logger = logging.getLogger(f'{__name__}.MoniteurSerie')

    def __init__(self, parent: tk.Frame, sersel: LigneSerie) -> None:
        """Initialise le moniteur série."""
        super().__init__(parent)
        self.__parent = parent
        self.__sersel = sersel
        self.__build()

    def __build(self) -> None:
        """Construit l'affichage texte."""
        self.text = tk.Text(self, width=90, wrap=tk.WORD)
        self.labelvar = tk.StringVar(self, 'Aucune connexion.')
        self.label = ttk.Label(self, textvariable=self.labelvar)

    def pack(self, **kargs: str | int) -> None:
        """Affiche avec pack."""
        self.__update()
        self.label.pack()
        self.text.pack()
        super().pack(**kargs)

    def __update(self) -> None:
        """Met le contenu du composant de texte à jour."""
        self.__logger.debug('MoniteurSerie.update')
        self.__logger.debug('%s', self.__sersel.ligne_serie)
        self.__logger.debug('%s', self.__sersel.is_open)
        texte = '\n'.join(i for i in self.__sersel)

        if len(texte.strip()) > 0:
            self.__logger.debug('%s', len(texte))
            self.text.insert(tk.END, texte + '\n')
            self.text.see(tk.END)

        if self.__sersel.is_open:
            self.labelvar.set(str(self.__sersel))
        else:
            self.labelvar.set('Aucune connexion.')

        self.label.update()
        self.text.update()
        self.update()
        self.after(500, self.__update)


class SelectionCalcul(tk.Frame):
    """Permet de choisir entre différents calculs."""


class TableauSerie(tk.Frame):
    """Tableau affichant les données transmises via une ligne série."""

    __logger = logging.getLogger(f'{__name__}.TableauSerie')

    def __init__(self, parent: tk.Frame, sersel: SelectionPortSerie) -> None:
        """Initialise le tableau."""
        super().__init__(parent)
        self.__parent = parent
        self.__sersel = sersel
        self.__tab = None

        self.__build()

    def __build(self) -> None:
        """Crée les composants graphiques."""
        mod = pt.TableModel(pd.DataFrame())
        self.tab = pt.Table(self, mod)

    def __update(self) -> None:
        """Met le tableau et les données sous-jacentes à jour."""
        self.__logger.debug('')

        if self.__sersel.is_open:
            if self.__tab is None:
                self.__tab = Tableau(self.__sersel.ligne_serie.parse())
                self.__tab.start()

                df = self.__tab.df
                self.__logger.debug('df.columns = %s', df.columns)
                self.__logger.debug('df.size = %s', df.size)

                if df.size > 0:
                    mod = pt.TableModel(df)
                    self.tab.updateModel(mod)

            self.tab.redraw()
            self.tab.show()
        elif self.__tab is not None:
            self.__tab.close()
            self.__tab = None

        self.update()
        self.after(500, self.__update)

    def pack(self, **kargs: str | int) -> None:
        """Affiche avec pack."""
        self.__update()
        self.tab.show()
        super().pack(**kargs)

    def grid(self, **kargs: str | int) -> None:
        """Affiche avec grid."""
        self.__update()
        self.tab.show()
        super().grid(**kargs)


class TraceurSerie(tk.Frame):
    """Affiche les données transmises via la ligne série."""

    def __init__(self, parent: tk.Frame, sersel: SelectionPortSerie, fmt: Format | None = None) -> None:
        """Initialise le traceur série."""
        super().__init__(parent)
        self.__parent = parent
        self.__sersel = sersel
        self.__tab = None
        self.__fig = None
        self.__fmt = fmt
        self._build()

    @property
    def fmt(self) -> Format:
        pass

    @property
    def sersel(self) -> SelectionPortSerie:
        return self.__sersel

    @property
    def fig(self) -> Graphe:
        return self.__fig

    @fig.setter
    def fig(self, val: Graphe) -> None:
        if isinstance(val, Graphe):
            self.__fig = val
        else:
            msg = f'{val!r} is not of type Graphe.'
            raise TypeError(msg)

    @property
    def tab(self) -> Tableau:
        return self.__tab

    @tab.setter
    def tab(self, val: Tableau) -> None:
        if isinstance(val, Tableau):
            self.__tab = val
        else:
            msg = f'{val!r} is not of type Tableau.'
            raise TypeError(msg)

    @property
    def is_open(self) -> bool:
        return self.__sersel.is_open

    def _build(self) -> None:
        """Construit les composants graphiques."""

    def _update(self) -> None:
        """Vérifie que le graphe est correctement configuré."""
        if self.is_open:
            if self.fig is None:
                self.tab = Tableau(self.sersel.ligne_serie.parse())
                self.fig = Graphe(self, self.tab, format_=self.fmt)
                self.tab.start()
                self.fig.show()
        elif self.fig is not None:
            self.close()

        self.after(500, self._update)

    def close(self) -> None:
        self.__fig.close()
        self.__tab.close()
        self.__tab = None
        self.__fig = None

    def show(self) -> None:
        """Affiche le traceur série."""
        self._update()

    def pack(self, **kargs: str | int) -> None:
        """Affiche avec pack."""
        self.show()
        super().pack(**kargs)

    def grid(self, **kargs: str | int) -> None:
        """Affiche avec grid."""
        self.show()
        super().grid(**kargs)


class TraceurCalcul(TraceurSerie):
    """Affiche le résultat d'un calcul dans un graphique."""

    def __init__(
        self, parent: tk.Frame, sersel: SelectionPortSerie, calcul: Calcul, fmt: Format | None = None
    ) -> None:
        """Initialise le traceur série."""
        super().__init__(parent, sersel, fmt=fmt)
        self.__calcul = calcul

    def _update(self) -> None:
        """Vérifie que le graphe est correctement configuré."""
        if self.is_open:
            if self.fig is None:
                self.tab = Tableau(self.sersel.ligne_serie.parse())
                self.fig = Graphe(
                    self, self.tab, self.__calcul @ Identite(), format_=self.fmt
                )
                self.tab.start()
                self.fig.show()
        elif self.fig is not None:
            self.close()

        self.after(500, self._update)


class APropos(tk.Toplevel):
    """Fenêtre d'informations sur l'application."""


class Reglages(tk.Toplevel):
    """Fenêtre de réglages."""


class Exporter(tk.Toplevel):
    """Invite d'exportation."""


class FenetreMoniteurSerie(tk.Toplevel):
    """Moniteur série dans une fenêtre à part."""


class FenetreTraceurSerie(tk.Toplevel):
    """Traceur série dans une fenêtre à part."""


class Application(tk.Tk):
    """Application de base pour PHS1903."""

    def __init__(self, name: str, *, title: str | None = None) -> None:
        """Initialise l'application."""
        super().__init__()
        self.name = name

        if title is not None:
            self.title(title)

        self.lignes_series = []
        self.__build()

        self.protocol('WM_DELETE_WINDOW', self.quit)

    def __build(self) -> None:
        """Construit les composants graphiques."""
        self['menu'] = BarreMenu(self)

    # Méthodes de fonctionnalités de base
    def show_about(self) -> None:
        """Affiche les informations de l'application.

        Raises
        ------------------------
        NotImplementedError
            Cette fonction n'est pas encore implémentée.
        """
        raise NotImplementedError

    def show_settings(self) -> None:
        """Affiche les réglages de l'application.

        Raises
        ------------------------
        NotImplementedError
            Cette fonction n'est pas encore implémentée.
        """
        raise NotImplementedError

    def quit(self) -> None:
        """Quitte l'application."""
        for ls in self.lignes_series:
            ls.close()

        super().quit()

    def export(self) -> None:
        """Exporte les données affichées.

        Raises
        ------------------------
        NotImplementedError
            Cette fonction n'est pas encore implémentée.
        """
        raise NotImplementedError

    def show_logger(self) -> None:
        """Affiche les journaux de débogage.

        Raises
        ------------------------
        NotImplementedError
            Cette fonction n'est pas encore implémentée.
        """
        raise NotImplementedError

    def show_doc(self) -> None:
        """Affiche la documentation dans le navigateur.

        Raises
        ------------------------
        NotImplementedError
            Cette fonction n'est pas encore implémentée.
        """
        raise NotImplementedError


def main(*, debug: bool = False) -> None:
    """Affiche le spectre de fréquence d'un signal artificiel."""
    from .calcul import FFT, rectangle  # noqa: PLC0415

    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

        config('src.xphs1903.outils.plot', level=DEBUG)

    __logger.debug('%s', __name__)
    app = Application('xphs1903', title='Démonstration')
    ser = SelectionPortSerie(app)
    # Eg d'options:
    #   - widget = MoniteurSerie(app, ser)
    #   - widget = TableauSerie(app, ser)
    #   - widget = TraceurSerie(app, ser)
    widget = TraceurCalcul(app, ser, FFT() @ rectangle(500)(), fmt=Format())

    ser.pack(side=tk.LEFT)
    widget.pack(side=tk.RIGHT)
    app.mainloop()


if __name__ == '__main__':
    import sys

    debug = '--debug' in sys.argv
    main(debug=debug)
