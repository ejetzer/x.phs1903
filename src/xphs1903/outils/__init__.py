# -*- coding: utf-8 -*-
# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Fonctionnalités de base."""

import sys

from .console import Canal, Console, Programme
from .graphe import Acquisition
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from serial.tools.list_ports_common import ListPortInfo

class ObjetImmuable:
    
    def __init__(self, cls: type, *args, **kargs):
        logging.debug('%s.__init__ pour %r avec cls=%r', type(self).__name__, self, cls)
        self._fixed = False
        self._object = cls(*args, **kargs)
        self._fixed = True
    
    def __getattr__(self, attr: str):
        logging.debug('%s.__getattr__ pour %r avec attr=%r', type(self).__name__, self, attr)
        return getattr(super().__getattribute__('_object'), attr)
    
    def __setattr__(self, attr: str, val: Any):
        logging.debug('%s.__setattr__ pour %r avec attr=%r, val=%r', type(self).__name__, self, attr, val)
        if attr == '_fixed':
            super().__setattr__(attr, val)
        elif not self._fixed:
            super().__setattr__(attr, val)
        else:
            raise AttributNonModifiable
    
    def __delattr__(self, attr: str):
        logging.debug('%s.__delattr__ pour %r avec attr=%r', type(self).__name__, self, attr)
        if attr == '_fixed' or self._fixed:
            raise AttributNonModifiable
        else:
            super().__delattr__(attr, val)



__all__ = [
    'Canal',
    'Console',
    'Programme',
    'Acquisition',
    'ChoixInvalideError'
    'choix'
]