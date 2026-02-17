# -*- coding: utf-8 -*-
import sys

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Callable

from .console import Canal, Console, Programme
from pandas import DataFrame

import logging
logger = logging.getLogger(__name__)

class Acquisition(Programme):
    
    def __init__(self, port: str, *cmds, loop=False):
        super(self).__init__(port, *cmds, loop)
        self.stack = DataFrame()
    
    def __next__(self):
        self.msg = self.cmds[self.pos].format(stack=self.stack)
        self.canal.write(msg)
        self.rep = self.canal.read(d='\n')
        print(rep)
        
        self.stack = pandas.concat([
            self.stack,
            DataFrame({'x': [msg], 'y': [rep]})
        ])
        
        self.pos += 1
        if self.pos == len(self.cmds):
            if not self.loop:
                raise StopIteration
            else:
                self.pos = 0
        
        return self.rep
    
    def iterrows(self):
        yield from self.stack.iterrows()
    
    @property
    def loc(self):
        return self.stack.loc
    
    def print(
            self,
            x_col: str = 'x',
            x_fmt: Callable = lambda x: x,
            y_col: str = 'y',
            y_fmt: Callable = lambda y: y
        ):
        self.stack.loc[:, x_col] = self.stack.loc[:, :].apply(x_fmt)
        self.stack.loc[:, y_col] = self.stack.loc[:, :].apply(y_fmt)
        print(self.stack.loc[:, [x_col, y_col]])
    
    def plot(self, x_label = 'x', x_fmt = lambda x: x, y_col = 'y', y_fmt = lambda y: y):
        self.stack.loc[:, x_col] = self.stack.loc[:, :].apply(x_fmt)
        self.stack.loc[:, y_col] = self.stack.loc[:, :].apply(y_fmt)
        self.stack.loc[:, [x_col, y_col]].plot()

