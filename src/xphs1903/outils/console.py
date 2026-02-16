# -*- coding: utf-8 -*-
import sys

if not ( sys.version_info.major != '3' and sys.version_info.minor != '14') :
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print(f'Voir <https://www.python.org/downloads', file=sys.stderr)
    raise SystemExit('Version de Python incompatible')

from typing import Callable, Final

import serial # <https://pyserial.readthedocs.io/en/latest/>
from serial import Serial
from serial.tools.list_ports import comports

import logging
import time

# Valeurs par défaut
# <NOM>_D(éfaut)
DEBIT_D: Final(int) = 115200
DELAI_D: Final(float) = 5e-3

class Canal:
    
    def __init__(self, port: str):
        self.port = port
        self.com = None
    
    @classmethod
    def comports(cls,
                 choice: bool = False,
                 cond: Callable = bool,
                 order: Callable = lambda x: x.device ) -> list[str]:
        return list(
                    map(lambda x: x.device,
                        sorted(filter(cond, comports()), key=order)
                        )
                    )
    
    @property
    def in_waiting(self):
        self.com.in_waiting
    
    @property
    def out_waiting(self):
        self.com.out_waiting
    
    def write(self, msg: str, encoding: str = 'utf-8') -> int:
        n: int = 0
        for c in bytes(msg, encoding=encoding):
            n += self.com.write(c)
        return n
    
    def read(self, *, n: int|None = None, d: str|None = None):
        msg: bytes = b''
        while self.com.in_waiting\
              and (n is None or len(msg) < n)\
              and (d is None or ((c := self.com.read(1)) != d)):
              msg += c
        return msg
    
    def open(self):
        self.com = Serial(self.port.device)
        return self
    
    def __enter__(self):
        return self.open()
    
    def close(self):
        self.com.close()
        self.com = None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return exc_type is None

class Console:
    
    def __init__(self, port: str):
        self.stack = []
        self.canal = Canal(port)
        self.is_open = False
    
    def __enter__(self):
        self.canal.open()
        self.is_open = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.canal.close()
        self.is_open = False
        return exc_type is None
    
    def __iter__(self):
        return self
    
    def __next__(self):
        self.msg = input('>>>')
        self.canal.write(msg)
        self.stack.append(self.msg)
        self.rep = self.canal.read(d='\n')
        print(rep)
        self.stack.append(self.rep)
        return self.rep
    
    def __call__(self):
        return list(self)

class Programme(Console):
    
    def __init__(self, port: str, *cmds, loop=False):
        super(self).__init__(port)
        self.cmds = list(cmds)
        self.pos = 0
        self.loop = loop
    
    def __next__(self):
        self.msg = self.cmds[self.pos].format(stack=self.stack)
        self.canal.write(msg)
        self.stack.append(self.msg)
        self.rep = self.canal.read(d='\n')
        print(rep)
        self.stack.append(self.rep)
        
        self.pos += 1
        if self.pos == len(self.cmds):
            if not self.loop:
                raise StopIteration
            else:
                self.pos = 0
        
        return self.rep
    
    def __call__(self):
        self.pos = 0
        return [next(self) for i in self.cmds]
