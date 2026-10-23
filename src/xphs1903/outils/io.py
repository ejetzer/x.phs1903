import sys

import rich
from rich.text import Text

from .multiprocessing import Processus, Synchronisateur


class Prompt(Processus):
    @classmethod
    def prompt(cls: type[Self], i: int | None = None) -> Text:
        return Text.from_markup(rf"[green bold]\[{i}]:[/] ", end="")

    @classmethod
    def loop(cls: type[Self], i: int | None = None) -> None:
        rich.print(cls.prompt(i))
        ligne = sys.stdin.readline()
