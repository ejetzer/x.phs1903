# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Teste le fonctionnement des démonstrations.

Les démonstrations offrent un aperçu large des capacités du module.
"""

from rich import print
from rich.prompt import Prompt
from rich.markdown import Markdown

from xphs1903.demos.dummy.signal import signal
from xphs1903.demos.serial.text.echo import echo as text_echo
from xphs1903.demos.serial.text.arduino import ardecho as arduino_echo
from xphs1903.demos.serial.data.echo import echodata as data_echo
from xphs1903.demos.serial.data.arduino import arddata as arduino_data
from xphs1903.demos.acq.echo import echotab as acq_echo
from xphs1903.demos.acq.arduino import ardtab as arduino_acq
from xphs1903.demos.calcul.echo import echocalc as calcul_echo
from xphs1903.demos.calcul.arduino import ardcalc as calcul_arduino
from xphs1903.demos.plot.static.image import static_echo_image_plot
#from xphs1903.demos.plot.static.pyplot import *
from xphs1903.demos.plot.static.tk import static_echo_tk_plot
from xphs1903.demos.plot.dynamic.image import dynamic_echo_image_plot
#from xphs1903.demos.plot.dynamic.pyplot import *
from xphs1903.demos.plot.dynamic.tk import dynamic_echo_tk_plot
from xphs1903.demos.plot.interactive.pyplot import interactive_echo_pyplot_plot
from xphs1903.demos.plot.interactive.tk import interactive_echo_tk_plot

TESTS = (
    signal,
    text_echo,
    data_echo,
    acq_echo,
    calcul_echo,
    static_echo_image_plot,
    dynamic_echo_image_plot
)

INTRO = """
# Tests interactifs en ligne de commande

Ces tests sont autonomes ou interactifs en ligne de commande.
Ils ne demandent aucun fenêtrage ou affichage, mais certains peuvent créer des fichiers de sortie.
"""

HEADER = """
## Test {0}: {1}

"""

Q_POURSUIVRE = "Poursuivre?"
Q_REUSSI = "Test {0} réussi?"
Q_REPETER = "Répéter test {0}?"

H_RULE = """
------------------------------
"""

A_SUCCES = "Test {0} réussi!"
A_ECHEC = "Test {0} échoué."

def header(i: int, test: Callable) -> str:
    return Markdown(HEADER.format(i+1, test.__name__))

def ask(q: str, opt: list[str], def_: str) -> str:
    return Prompt.ask(q, choices=opt, default=def_, case_sensitive=False)

def poursuivre() -> bool | None:
    rep = ask(Q_POURSUIVRE, opt=["o", "n", "q"], def_="o")

    if veut_quitter(rep):
        return None

    if acquiesce(rep):
        return True

    return False

def reussite(i: int) -> bool | None:
    rep = ask(Q_REUSSI.format(i+1), opt=["o", "n", "r"], def_="o")

    if acquiesce(rep):
        return True

    if veut_repeter(rep):
        return None

    return False

def repeter(i: int) -> bool | None:
    rep = ask(Q_REPETER.format(i+1), opt=["o", "n"], def_="o")

    if veut_repeter(rep):
        return True

    return False

def conclusion(succès: bool, i: int) -> str:
    if succès:
        return A_SUCCES.format(i+1)

    return A_ECHEC.format(i+1)

def h_rule() -> str:
    return Markdown(H_RULE)

def veut_quitter(rep: str) -> bool:
    return rep[0] in "qQeE"

def acquiesce(rep: str) -> bool:
    return rep[0] in "oOyY"

def refuse(rep: str) -> bool:
    return rep[0] in "nN"

def veut_repeter(rep: str) -> bool:
    return rep[0] in "rRaA"

def main(tests=TESTS):
    print(Markdown(INTRO))

    min_i, max_i = 0, len(tests)
    i = min_i
    while min_i <= i < max_i:
        test = tests[i]

        print(header(i, test))

        match poursuivre():
            case None:
                break
            case False:
                continue

        succès, répéter, contexte = False, False, None

        try:
            test(debug=True)
        except KeyboardInterrupt:
            match reussite(i):
                case True:
                    succès = True
                case None:
                    répéter = True
        except Exception as err:
            répéter, contexte = repeter(i), err
            contexte = err
        else:
            succès = True
        finally:
            print(h_rule())
            print(conclusion(succès, i))

            if contexte is not None:
                print(contexte)

            print()

        if répéter:
            continue

        i += 1

if __name__ == '__main__':
    main()
