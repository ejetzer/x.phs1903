# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.

class SelectionPortSerie:
    pass

class BarreOutil:
    pass

class MenuBase:
    pass

def main(*, debug: bool = False) -> None:
    """Affiche le spectre de fréquence d'un signal artificiel."""
    from functools import partial  # noqa: PLC0415

    from .plot import Graphe, Format
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
