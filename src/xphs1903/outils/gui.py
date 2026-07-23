# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
import logging
import time
import re
import tkinter as tk
from tkinter import ttk

import pandastable as pt
import pandas as pd
import serial.tools.list_ports

from .serial import LigneSerie
from .acq import Tableau
from .calcul import Calcul, Identite
from .plot import Graphe

__logger = logging.getLogger(__name__)
__logger.addHandler(logging.NullHandler())

class SelectionPortSerie(ttk.Frame):
    __logger = logging.getLogger(f'{__name__}.SelectionPortSerie')

    def __init__(self, parent: ttk.Frame | tk.Toplevel) -> None:
        super().__init__(parent)
        self.__parent = parent
        self.ligne_serie = None
        self.__build()

    def __build(self):
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
            invalidcommand=(self.invalide, '%d', '%P', '%s', '%v', '%V')
        )
        self.defil: ttk.Scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL
        )
        self.liste: tk.Listbox = tk.Listbox(
            self,
            height=10,
            listvariable=self.valeurs,
            selectmode=tk.SINGLE,
            yscrollcommand=self.defil.set,
            exportselection=False
        )
        self.liste.bind('<<ListboxSelect>>', self.__selection)
        self.defil['command'] = self.liste.yview

        self.conn = ttk.Button(
            self,
            text='Connecter',
            command=self.__connect_serial,
        )
        self.conn.state(('!disabled',))

        self.disc = ttk.Button(
            self,
            text='Déconnecter',
            command=self.__disconnect_serial
        )
        self.disc.state((tk.DISABLED,))

    def __update(self):
        self.__logger.debug('%s %s', time.process_time(), 'SelectionPortSerie.update')
        self.__logger.debug('%s', self.ligne_serie)
        self.__filtrer(None, None)
        self.update()
        self.after(1000, self.__update)

    @property
    def options(self) -> list[str]:
        return [
            x for x in self.comports
            if re.search(self.valeur.get(), x) is not None
        ]

    @property
    def comports(self) -> list[str]:
        return [
            x.device for x in serial.tools.list_ports.comports()
        ] + ['loop://']

    @property
    def selection(self):
        sel = [self.liste.get(i) for i in self.liste.curselection()]
        if len(sel) == 0:
            sel = []
        return sel

    def __filtrer(self, nom, mode, *args):
        sel = self.selection
        self.valeurs.set(self.options)

        for i, opt in enumerate(self.options):
            if opt in sel:
                self.liste.selection_set(i)

    def __valider(self, action, apres, avant, validate, reason):
        return len(self.options) > 0

    def __invalide(self, action, apres, avant, validate, reason):
        return None

    def __selection(self, event):
        pass

    def __connect_serial(self):
        self.conn.state(('disabled',))
        sel = self.selection
        if len(sel) > 0:
            self.ligne_serie = LigneSerie(self.selection[0])
            self.__parent.lignes_series.append(self.ligne_serie)
            self.ligne_serie.open()
            self.disc.state(('!disabled',))
        else:
            self.conn.state(('!disabled',))

    def __disconnect_serial(self):
        self.disc.state(('disabled',))
        self.ligne_serie.close()
        self.ligne_serie = None
        self.conn.state(('!disabled',))

    @property
    def is_open(self):
        if self.ligne_serie is None:
            return False
        else:
            return self.ligne_serie.is_open

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.ligne_serie is None:
            raise StopIteration
        ret = next(self.ligne_serie)
        if ret is None:
            raise StopIteration
        else:
            return ret

    def __str__(self):
        if self.is_open:
            ret = f"Connecté à {self.ligne_serie.device}."
        else:
            ret = 'Aucune connexion.'

        return ret

    def pack(self, **kargs):
        self.__update()
        self.champ.grid(row=0, column=0, sticky=tk.E+tk.W)
        self.liste.grid(row=1, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        self.defil.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.conn.grid(row=2, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        self.disc.grid(row=3, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        super().pack(**kargs)

    def grid(self, row: int = 0, column: int = 0, **kargs):
        self.__update()
        self.champ.pack(sticky=tk.E+tk.W)
        self.liste.grid(row=1, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        self.defil.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.conn.grid(row=2, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        self.disc.grid(row=3, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        super().grid(row=row, column=column, **kargs)

class BarreOutil(tk.Frame):
    pass

class BarreMenu(tk.Menu):
    __logger = logging.getLogger(f'{__name__}.BarreMenu')

    def __init__(self, parent: Application) -> None:
        super().__init__(parent)
        self.__parent: Application = parent
        self.__build()

    def __build(self) -> None:
        # Menu principal
        menu_app = tk.Menu(self)
        self.add_cascade(
            label=self.__parent.name,
            menu=menu_app
        )
        menu_app.add_command(
            label=f'À propos de {self.__parent.name}',
            command=self.__parent.show_about
        )
        menu_app.add_command(
            label='Réglages...',
            command=self.__parent.show_settings
        )
        menu_app.add_command(
            label='Quitter',
            command=self.__parent.quit
        )

        # Menu fichier
        menu_fic = tk.Menu(self)
        self.add_cascade(
            label='Fichier',
            menu=menu_fic
        )
        menu_fic.add_command(
            label='Exporter...',
            command=self.__parent.export
        )

        # Menu d'aide
        menu_aide = tk.Menu(self)
        self.add_cascade(
            label='Aide',
            menu=menu_aide
        )
        menu_aide.add_command(
            label='Journal de débogage',
            command=self.__parent.show_logger
        )
        menu_aide.add_command(
            label='Documentation du module x.phs1903',
            command=self.__parent.show_doc
        )

class MoniteurSerie(ttk.Frame):
    __logger = logging.getLogger(f'{__name__}.MoniteurSerie')

    def __init__(self, parent, sersel):
        super().__init__(parent)
        self.__parent = parent
        self.__sersel = sersel
        self.__build()

    def __build(self):
        self.text = tk.Text(
            self,
            width=90,
            wrap=tk.WORD
        )
        self.labelvar = tk.StringVar(
            self,
            'Aucune connexion.'
        )
        self.label = ttk.Label(
            self,
            textvariable=self.labelvar
        )

    def pack(self, **kargs):
        self.__update()
        self.label.pack()
        self.text.pack()
        super().pack(**kargs)

    def __update(self):
        self.__logger.debug('MoniteurSerie.update')
        self.__logger.debug('%s', self.__sersel.ligne_serie)
        self.__logger.debug('%s', self.__sersel.is_open)
        texte = '\n'.join(l for l in self.__sersel)

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
    pass

class TableauSerie(tk.Frame):
    __logger = logging.getLogger(f'{__name__}.TableauSerie')

    def __init__(
        self,
        parent: tk.Frame,
        sersel: SelectionPortSerie
    ) -> None:
        super().__init__(parent)
        self.__parent = parent
        self.__sersel = sersel
        self.__tab = None

        self.__build()

    def __build(self):
        mod = pt.TableModel(pd.DataFrame())
        self.tab = pt.Table(self, mod)

    def __update(self):
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

    def pack(self, **kargs):
        self.__update()
        self.tab.show()
        super().pack(**kargs)

    def grid(self, **kargs):
        self.__update()
        self.tab.show()
        super().grid(**kargs)

class TraceurSerie(tk.Frame):

    def __init__(
        self,
        parent: tk.Frame,
        sersel: SelectionPortSerie
    ) -> None:
        super().__init__(parent)
        self.__parent = parent
        self.__sersel = sersel
        self.__tab = None
        self.__fig = None
        self.__build()

    def __build(self):
        pass

    def __update(self):
        if self.__sersel.is_open:
            if self.__fig is None:
                self.__tab = Tableau(self.__sersel.ligne_serie.parse())
                self.__fig = Graphe(self, self.__tab)
                self.__tab.start()
                self.__fig.show()
        elif self.__fig is not None:
            self.__fig.close()
            self.__tab.close()
            self.__tab = None
            self.__fig = None

        self.after(500, self.__update)

    def show(self):
        self.__update()

    def pack(self, **kargs):
        self.show()
        super().pack(**kargs)

    def grid(self, **kargs):
        self.show()
        super().grid(**kargs)

class TraceurCalcul(tk.Frame):

    def __init__(
        self,
        parent: tk.Frame,
        sersel: SelectionPortSerie,
        calcul: Calcul
    ) -> None:
        super().__init__(parent)
        self.__parent = parent
        self.__sersel = sersel
        self.__calcul = calcul
        self.__tab = None
        self.__fig = None
        self.__build()

    def __build(self):
        pass

    def __update(self):
        if self.__sersel.is_open:
            if self.__fig is None:
                self.__tab = Tableau(self.__sersel.ligne_serie.parse())
                self.__fig = Graphe(self, self.__tab, self.__calcul @ Identite())
                self.__tab.start()
                self.__fig.show()
        elif self.__fig is not None:
            self.__fig.close()
            self.__tab.close()
            self.__tab = None
            self.__fig = None

        self.after(500, self.__update)

    def show(self):
        self.__update()

    def pack(self, **kargs):
        self.show()
        super().pack(**kargs)

    def grid(self, **kargs):
        self.show()
        super().grid(**kargs)

class APropos(tk.Toplevel):
    pass

class Reglages(tk.Toplevel):
    pass

class Exporter(tk.Toplevel):
    pass

class FenetreMoniteurSerie(tk.Toplevel):
    pass

class FenetreTraceurSerie(tk.Toplevel):
    pass

class ContextApp(tk.Tk):

    def __init__(self):
        super().__init__()

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def mainloop(self):
        with self:
            super().mainloop()

    def quit():
        pass

class Application(tk.Tk):

    def __init__(
        self,
        name: str,
        *,
        title: str = None
    ) -> None:
        super().__init__()
        self.name = name

        if title is not None:
            self.title(title)

        self.lignes_series = []
        self.__build()

        self.protocol('WM_DELETE_WINDOW', self.quit)

    def __build(self):
        self['menu'] = BarreMenu(self)

    # Méthodes de fonctionnalités de base
    def show_about(self):
        pass

    def show_settings(self):
        pass

    def quit(self):
        for ls in self.lignes_series:
            ls.close()

        super().quit()

    def export(self):
        pass

    def show_logger(self):
        pass

    def show_doc(self):
        pass

def main(*, debug: bool = False) -> None:
    """Affiche le spectre de fréquence d'un signal artificiel."""
    from .calcul import FFT, rectangle

    if debug:
        from .logging import config, DEBUG
        config(__name__, level=DEBUG)

    __logger.debug('%s', __name__)
    app = Application('xphs1903', title='Démonstration')
    ser = SelectionPortSerie(app)
    # txt = MoniteurSerie(app, ser)
    # tab = TableauSerie(app, ser)
    # fig = TraceurSerie(app, ser)
    cal = TraceurCalcul(app, ser, FFT() @ rectangle(500)())

    ser.pack(side=tk.LEFT)
    # txt.pack(side=tk.RIGHT)
    # tab.pack(side=tk.RIGHT)
    # fig.pack(side=tk.RIGHT)
    cal.pack(side=tk.RIGHT)
    app.mainloop()


if __name__ == '__main__':
    import sys

    debug = '--debug' in sys.argv
    main(debug=debug)
