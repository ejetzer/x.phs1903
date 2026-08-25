# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Outils de création d'interface graphique."""

import re
import tkinter as tk
from tkinter import ttk
from typing import Self

import matplotlib as mpl
import pandas as pd
import pandastable as pt
import serial.tools
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from serial import SerialException

from .acq import Tableau
from .exceptions import InvalidCommandTypeError
from .logging import DEBUG, WithLogger, basicConfig, info
from .serial import LigneSerie


class SelectionPortSerie(ttk.Frame, WithLogger):
    """Sélecteur de port série."""

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

        self.valeur.trace_add("write", self.__filtrer)

        self.champ: ttk.Entry = ttk.Entry(
            self,
            textvariable=self.valeur,
            validate="all",
            validatecommand=(self.valider, "%d", "%P", "%s", "%v", "%V"),
            invalidcommand=(self.invalide, "%d", "%P", "%s", "%v", "%V"),
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

        self.defil["command"] = self.liste.yview

        self.conn = ttk.Button(
            self,
            text="Connecter",
            command=self.__connect_serial,
        )
        self.conn.state(("!disabled",))

        self.disc = ttk.Button(
            self, text="Déconnecter", command=self.__disconnect_serial
        )
        self.disc.state((tk.DISABLED,))

        self.baudvar = tk.StringVar(self, "9 600")
        self.baudmenu = tk.OptionMenu(self, self.baudvar, "9 600", "115 200")

    @property
    def baudrate(self) -> None:
        """Débit maximal de communication."""
        val = self.baudvar.get()
        val = val.replace(" ", "")
        return int(val)

    def __update(self) -> None:
        """Met l'affichage à jour."""
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
            "loop://"
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

    # La signature est imposée par Tk, donc certains arguments
    # ne sont pas utilisés.
    def __filtrer(self, nom: str, mode: str, op: str) -> None:  # noqa: ARG002
        """Sélectionne les valeurs pertinentes."""
        sel = self.selection
        self.valeurs.set(self.options)

        for i, opt in enumerate(self.options):
            if opt in sel:
                self.liste.selection_set(i)

    # Voir https://tkdocs.com/shipman/entry-validation.html
    # La signature est imposée par Tk, donc certains arguments
    # ne sont pas utilisés.
    def __valider(
        self,
        action: int,  # noqa: ARG002
        apres: str,  # noqa: ARG002
        avant: str,  # noqa: ARG002
        validate: bool,  # noqa: FBT001,ARG002
        reason: str,  # noqa: ARG002
    ) -> bool:
        """Valide une entrée.

        Returns
        ------------------------
        True
            Si il reste des options valides.
        False
            Autrement.
        """
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

    def __connect_serial(self) -> None:
        """Connecte la ligne série."""
        self.conn.state(("disabled",))
        sel = self.selection
        baud = self.baudrate
        self.baudmenu.configure(state="disabled")
        if len(sel) > 0:
            self.ligne_serie = LigneSerie(sel[0], baud)
            self.__parent.lignes_series.append(self.ligne_serie)

            try:
                self.ligne_serie.open()
            except SerialException:
                pass

            if self.is_open:
                self.disc.state(("!disabled",))

        if not self.is_open:
            self.conn.state(("!disabled",))

    def __disconnect_serial(self) -> None:
        """Déconnecte la ligne série."""
        self.disc.state(("disabled",))
        self.ligne_serie.close()
        self.ligne_serie = None
        self.conn.state(("!disabled",))
        self.baudmenu.configure(state="active")

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

        ret = self.ligne_serie.next(block=False)

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
            ret = f"Connecté à {self.ligne_serie.device}."
        else:
            ret = "Aucune connexion."

        return ret

    def show(self) -> None:
        """Affiche les composants Tk."""
        self.__update()
        self.champ.grid(row=0, column=0, columnspan=2, sticky=tk.E + tk.W)
        self.liste.grid(
            row=1, column=0, columnspan=2, sticky=tk.E + tk.W + tk.N + tk.S
        )
        self.defil.grid(row=1, column=2, sticky=tk.N + tk.S)
        self.baudmenu.grid(row=2, column=0, columnspan=2, sticky=tk.W + tk.E)
        self.conn.grid(row=3, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.disc.grid(row=3, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

    def pack(self, **kargs: str | int) -> None:
        """Affiche avec pack."""
        self.show()
        super().pack(**kargs)

    def grid(self, row: int = 0, column: int = 0, **kargs: str | int) -> None:
        """Affiche avec grid."""
        self.show()
        super().grid(row=row, column=column, **kargs)


class BarreMenu(tk.Menu, WithLogger):
    """Le menu de base pour les applications de PHS1903."""

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
            label=f"À propos de {self.__parent.name}",
            command=self.__parent.show_about,
        )
        menu_app.add_command(
            label="Réglages...", command=self.__parent.show_settings
        )
        menu_app.add_command(label="Quitter", command=self.__parent.quit)

        # Menu fichier
        menu_fic = tk.Menu(self)
        self.add_cascade(label="Fichier", menu=menu_fic)
        menu_fic.add_command(label="Exporter...", command=self.__parent.export)

        # Menu d'aide
        menu_aide = tk.Menu(self)
        self.add_cascade(label="Aide", menu=menu_aide)
        menu_aide.add_command(
            label="Journal de débogage", command=self.__parent.show_logger
        )
        menu_aide.add_command(
            label="Documentation du module x.phs1903",
            command=self.__parent.show_doc,
        )


class MoniteurSerie(ttk.Frame, WithLogger):
    """Affiche le texte envoyé via une ligne série."""

    def __init__(self, parent: tk.Frame, sersel: LigneSerie) -> None:
        """Initialise le moniteur série."""
        super().__init__(parent)
        self.__sersel = sersel
        self.__build()

    def __build(self) -> None:
        """Construit l'affichage texte."""
        self.clear_button = ttk.Button(
            self, text="Effacer", command=self.__clear
        )
        self.text = tk.Text(self, width=90, wrap=tk.WORD)
        self.text.tag_config("prompt", foreground="green")
        self.text.tag_config("entry", foreground="blue")
        self.labelvar = tk.StringVar(self, "Aucune connexion.")
        self.label = ttk.Label(self, textvariable=self.labelvar)
        self.entryvar = tk.StringVar(self)
        self.entry = ttk.Entry(self, textvariable=self.entryvar)
        self.eol_var = tk.StringVar(self, "\\n")
        self.eol_select = tk.OptionMenu(
            self, self.eol_var, "'\\n'", "'\\r'", "'\\r\\n'", "''"
        )
        self.send_button = ttk.Button(
            self, text="Envoyer", command=self.__send
        )

    @property
    def eol(self) -> str:
        """Caractère de fin de commande."""
        sel = self.eol_var.get()
        return sel.strip("'").replace("\\n", "\n").replace("\\r", "\n")

    @property
    def command(self) -> str:
        """Commande entrée dans la ligne de commande."""
        return self.entryvar.get()

    @command.setter
    def command(self, val: str) -> None:
        """Commande entrée dans la ligne de commande."""
        if not isinstance(val, str):
            raise InvalidCommandTypeError(val)

        self.entryvar.set(val)

    def __send(self) -> None:
        cmd = self.command
        self.__sersel.ligne_serie.print(cmd, end=self.eol)
        self.text.insert(tk.END, ">>> ", "prompt")
        self.text.insert(tk.END, f"{cmd}\n", "entry")
        self.command = ""

    def __clear(self) -> None:
        self.text.delete("1.0", tk.END)

    def pack(self, **kargs: str | int) -> None:
        """Affiche avec pack."""
        self.__update()
        self.label.grid(column=0, row=0, columnspan=4, sticky=tk.W)
        self.clear_button.grid(column=4, row=0, sticky=tk.W + tk.E)
        self.text.grid(column=0, row=1, columnspan=5)
        self.entry.grid(column=0, row=2, columnspan=5, sticky=tk.E + tk.W)
        self.eol_select.grid(column=3, row=3, sticky=tk.E + tk.W)
        self.send_button.grid(column=4, row=3, sticky=tk.E + tk.W)
        super().pack(**kargs)

    def __update(self) -> None:
        """Met le contenu du composant de texte à jour."""
        texte = "\n".join(i for i in self.__sersel)

        if len(texte.strip()) > 0:
            self.text.insert(tk.END, texte + "\n")
            self.text.see(tk.END)

        if self.__sersel.is_open:
            self.labelvar.set(str(self.__sersel))
        else:
            self.labelvar.set("Aucune connexion.")

        self.label.update()
        self.text.update()
        self.update()
        self.after(500, self.__update)


class TraceurSerie(ttk.Frame, WithLogger):
    """Traceur série analogue à celui de l'IDE Arduino."""

    def __init__(self, parent: tk.Frame, sersel: LigneSerie) -> None:
        """Initialise le moniteur série."""
        self.checkin()
        super().__init__(parent)
        self.__sersel = sersel
        self.__tab = None
        self.__build()

    def __build(self) -> None:
        """Construit l'affichage texte."""
        self.checkin()
        self.clear_button = ttk.Button(
            self, text="Effacer", command=self.__clear
        )
        self.plot_frame = ttk.Frame(self)
        self.figure = mpl.figure.Figure()
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.toolbar = NavigationToolbar2Tk(
            self.canvas, self.plot_frame, pack_toolbar=False
        )
        self.labelvar = tk.StringVar(self, "Aucune connexion.")
        self.label = ttk.Label(self, textvariable=self.labelvar)
        self.entryvar = tk.StringVar(self)
        self.entry = ttk.Entry(self, textvariable=self.entryvar)
        self.eol_var = tk.StringVar(self, "\\n")
        self.eol_select = tk.OptionMenu(
            self, self.eol_var, "'\\n'", "'\\r'", "'\\r\\n'", "''"
        )
        self.send_button = ttk.Button(
            self, text="Envoyer", command=self.__send
        )

    @property
    def lines(self) -> list[mpl.lines.Line2D]:
        """Traces du graphique."""
        return self.axes.get_lines()

    @property
    def canvas_widget(self) -> tk.Frame:
        """Composant Tk du canevas."""
        return self.canvas.get_tk_widget()

    @property
    def eol(self) -> str:
        """Caractère de fin de commande."""
        self.checkin()
        sel = self.eol_var.get()
        return sel.strip("'").replace("\\n", "\n").replace("\\r", "\n")

    @property
    def command(self) -> str:
        """Commande entrée dans la ligne de commande."""
        self.checkin()
        return self.entryvar.get()

    @command.setter
    def command(self, val: str) -> None:
        """Commande entrée dans la ligne de commande."""
        self.checkin()
        if not isinstance(val, str):
            raise InvalidCommandTypeError(val)

        self.entryvar.set(val)

    def __send(self) -> None:
        self.checkin()
        cmd = self.command
        self.__sersel.ligne_serie.print(cmd, end=self.eol)
        self.command = ""

    def __clear(self) -> None:
        self.checkin()
        self.text.delete("1.0", tk.END)

    def show(self) -> None:
        """Affiche avec pack."""
        self.checkin()
        self.__update()
        self.label.grid(column=0, row=0, columnspan=5, sticky=tk.W)
        self.plot_frame.grid(
            column=0, row=1, columnspan=5, sticky=tk.W + tk.E + tk.N + tk.S
        )
        self.canvas_widget.grid(
            column=0, row=0, sticky=tk.W + tk.E + tk.N + tk.S
        )
        self.toolbar.grid(column=0, row=1, sticky=tk.W + tk.E)
        self.entry.grid(column=0, row=2, columnspan=5, sticky=tk.E + tk.W)
        self.eol_select.grid(column=3, row=3, sticky=tk.E + tk.W)
        self.send_button.grid(column=4, row=3, sticky=tk.E + tk.W)

    def pack(self, **kargs: str | int) -> None:
        """Affiche le traceur série avec pack."""
        self.checkin()
        self.show()
        super().pack(**kargs)

    def __update(self) -> None:
        """Met le contenu du composant de texte à jour."""
        self.checkin()

        if self.__sersel.is_open:
            if self.__tab is None:
                self.__tab = Tableau(self.__sersel.ligne_serie)
                self.__tab.start()

            lignes = self.lines
            self.debug("lignes = %s", lignes)
            ts, xs = self.__tab.ts, self.__tab.xs
            self.debug("ts = %s", ts)

            its, ixs = iter(ts), iter(xs)
            for ligne, _t, x in zip(lignes, its, ixs, strict=False):
                ligne.set_data(range(len(x)), x)

            for _t, x in zip(its, ixs, strict=True):
                self.axes.plot(x)

            if len(ts) > 0:
                xmax, xmin = max(map(max, xs)), min(map(min, xs))
                self.axes.set_xlim(len(xs[0]) - 100, len(xs[0]))
                self.axes.set_ylim(xmin, xmax)

            self.canvas.draw()

        elif self.__tab is not None:
            self.__tab.close()
            self.__tab = None

        if self.__sersel.is_open:
            self.labelvar.set(str(self.__sersel))
        else:
            self.labelvar.set("Aucune connexion.")

        self.label.update()

        self.update()
        self.after(1000, self.__update)


class TkTableau(ttk.Frame, WithLogger):
    """Tableau affichant les données transmises via une ligne série."""

    def __init__(self, parent: tk.Frame, sersel: SelectionPortSerie) -> None:
        """Initialise le tableau."""
        self.checkin()
        super().__init__(parent)
        self.__sersel = sersel
        self.__tab = None

        self.__build()

    def __build(self) -> None:
        """Crée les composants graphiques."""
        self.checkin()
        mod = pt.TableModel(pd.DataFrame())
        self.tab = pt.Table(self, mod)

    def __update(self) -> None:
        """Met le tableau et les données sous-jacentes à jour."""
        self.checkin()

        self.debug("open = %s", self.__sersel.is_open)
        if self.__sersel.is_open:
            if self.__tab is None:
                self.__tab = Tableau(self.__sersel.ligne_serie)
                self.__tab.start()

            df = self.__tab.df

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
        self.checkin()
        self.__update()
        self.tab.show()
        super().pack(**kargs)

    def grid(self, **kargs: str | int) -> None:
        """Affiche avec grid."""
        self.checkin()
        self.__update()
        self.tab.show()
        super().grid(**kargs)


class APropos(tk.Toplevel, WithLogger):
    """Fenêtre d'informations sur l'application."""


class Reglages(tk.Toplevel, WithLogger):
    """Fenêtre de réglages."""


class Exporter(tk.Toplevel, WithLogger):
    """Invite d'exportation."""


class FenetreMoniteurSerie(tk.Toplevel, WithLogger):
    """Moniteur série dans une fenêtre à part."""


class FenetreTraceurSerie(tk.Toplevel, WithLogger):
    """Traceur série dans une fenêtre à part."""


class Application(tk.Tk, WithLogger):
    """Application de base pour PHS1903."""

    def __init__(self, name: str, *, title: str | None = None) -> None:
        """Initialise l'application."""
        super().__init__()
        self.name = name

        if title is not None:
            self.title(title)

        self.lignes_series = []
        self.__build()

        self.protocol("WM_DELETE_WINDOW", self.quit)

    def __build(self) -> None:
        """Construit les composants graphiques."""
        self["menu"] = BarreMenu(self)

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


def application(*, debug: bool = False) -> None:
    """Exemple d'application vide."""
    if debug:
        basicConfig(DEBUG)

    app = Application("xphs1903", title="Démo")
    info("Application initialisée: %r", app)

    if debug:
        app.log_to_stderr()
        app.setLevel("debug")

    info("Lancement de l'application...")
    app.mainloop()

    info("Fin.")


def selecteur_serie(*, debug: bool = False) -> None:
    """Exemple de sélection de ligne série."""
    if debug:
        basicConfig(DEBUG)

    app = Application("xphs1903", title="Démo")
    info("Application initialisée: %r", app)

    ser = SelectionPortSerie(app)
    info("Ligne série configurée: %r", ser)

    if debug:
        app.log_to_stderr()
        app.setLevel("debug")
        ser.log_to_stderr()
        ser.setLevel("debug")

    ser.pack(side=tk.LEFT, fill=tk.Y)

    info("Lancement de l'application...")
    app.mainloop()

    info("Fin.")


def moniteur_serie(*, debug: bool = False) -> None:
    """Exemple d'affichage de mesures dans un terminal."""
    if debug:
        basicConfig(DEBUG)

    app = Application("xphs1903", title="Démo")
    info("Application initialisée: %r", app)

    ser = SelectionPortSerie(app)
    info("Ligne série configurée: %r", ser)

    mon = MoniteurSerie(app, ser)
    info("Traceur configuré: %r", mon)

    if debug:
        app.log_to_stderr()
        app.setLevel("debug")
        ser.log_to_stderr()
        ser.setLevel("debug")
        mon.log_to_stderr()
        mon.setLevel("debug")

    ser.pack(side=tk.LEFT, fill=tk.Y)
    mon.pack(side=tk.RIGHT, fill=tk.Y)

    info("Lancement de l'application...")
    app.mainloop()

    info("Fin.")


def traceur_serie(*, debug: bool = False) -> None:
    """Exemple d'affichage de mesures sur un graphique."""
    if debug:
        basicConfig(DEBUG)

    app = Application("xphs1903", title="Démo")
    info("Application initialisée: %r", app)

    ser = SelectionPortSerie(app)
    info("Ligne série configurée: %r", ser)

    mon = TraceurSerie(app, ser)
    info("Traceur configuré: %r", mon)

    if debug:
        app.log_to_stderr()
        app.setLevel("debug")
        ser.log_to_stderr()
        ser.setLevel("debug")
        mon.log_to_stderr()
        mon.setLevel("debug")

    ser.pack(side=tk.LEFT, fill=tk.Y)
    mon.pack(side=tk.RIGHT, fill=tk.Y)

    info("Lancement de l'application...")
    app.mainloop()

    info("Fin.")


def tableau_serie(*, debug: bool = False) -> None:
    """Exemple d'affichage de mesures dans un tableau."""
    if debug:
        basicConfig(DEBUG)

    app = Application("xphs1903", title="Démo")
    info("Application initialisée: %r", app)

    ser = SelectionPortSerie(app)
    info("Ligne série configurée: %r", ser)

    mon = TkTableau(app, ser)
    info("Tableau configuré: %r", mon)

    if debug:
        app.log_to_stderr()
        app.setLevel("debug")
        ser.log_to_stderr()
        ser.setLevel(DEBUG)
        mon.log_to_stderr()
        ser.setLevel(DEBUG)

    ser.pack(side=tk.LEFT, fill=tk.Y)
    mon.pack(side=tk.RIGHT, fill=tk.Y)

    info("Lancement de l'application...")
    app.mainloop()

    info("Fin.")


__all__ = ["MoniteurSerie", "SelectionPortSerie", "TkTableau", "TraceurSerie"]
